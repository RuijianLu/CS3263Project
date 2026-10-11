"""Proposal evaluation: detect misleading pilot denominators and accidental outcomes."""
import copy
import csv
import json
import pytest

from degree_planner import evaluate as evaluation
from degree_planner import codex_runner
from degree_planner.collect import write_json


def spec(horizon=4):
    return dict(completed=[], semesters=[1 + t % 2 for t in range(horizon)],
                max_units=16, required=["A"], forbidden=[], fixed=[], groups=[])


def course(code):
    return dict(code=code, units=4, offered_semesters=[1, 2], selectable=True,
                prerequisites=None, corequisites=[], preclusions=[])


def attempt(root, case_id, approach, status, response=None):
    folder = root / "results/runs/pilot" / f"{case_id}-{approach}"
    folder.mkdir(parents=True, exist_ok=True)
    write_json(folder / "record.json", dict(case_id=case_id, approach=approach, status=status,
                                            elapsed_seconds=2, usage=None))
    if response is not None:
        write_json(folder / "response.json", response)


@pytest.fixture
def pilot(tmp_path, monkeypatch):
    (tmp_path / "data/benchmark").mkdir(parents=True)
    write_json(tmp_path / "data/courses.json", {c: course(c) for c in ("A", "B")})
    write_json(tmp_path / "data/requirements.json", {"corequisite_pairs": []})
    write_json(tmp_path / "experiment.json", dict(model="test-model", reasoning_effort="medium",
                                                attempts_per_case=1, solver_timeout_seconds=10))
    cases, answers = [], []
    for index, difficulty in enumerate(("easy", "hard", "medium", "hard", "easy"), 1):
        identifier = f"case-{index}"
        original = spec(2 if index == 2 else 4)
        if index == 2:
            original["forbidden"] = ["A"]
        cases.append(dict(id=identifier, difficulty=difficulty, remaining_semesters=len(original["semesters"])))
        answers.append(dict(id=identifier, status="infeasible" if index == 2 else "feasible", spec=original))
    for name, values in (("dev.jsonl", cases), ("gold.jsonl", answers)):
        (tmp_path / "data/benchmark" / name).write_text("".join(json.dumps(v) + "\n" for v in values), encoding="utf-8")
    folder = tmp_path / "results/runs/pilot"
    folder.mkdir(parents=True)
    write_json(folder / "manifest.json", {"case_ids": [c["id"] for c in cases[:4]]})
    monkeypatch.setattr(evaluation, "require_current_benchmark", lambda root: None)
    monkeypatch.setattr(evaluation, "verify_manifest", lambda *args: None)
    attempt(tmp_path, "case-1", "direct", "ok", {"status": "unknown", "semesters": [], "explanation": "Uncertain"})
    attempt(tmp_path, "case-1", "assisted", "ok", answers[0]["spec"])
    attempt(tmp_path, "case-2", "direct", "ok", {"status": "infeasible", "semesters": [], "explanation": "Contradiction"})
    wrong_translation = copy.deepcopy(answers[1]["spec"])
    wrong_translation["forbidden"].append("B")
    attempt(tmp_path, "case-2", "assisted", "ok", wrong_translation)
    attempt(tmp_path, "case-3", "direct", "timeout")
    attempt(tmp_path, "case-4", "direct", "execution_error")
    attempt(tmp_path, "case-4", "assisted", "ok", {"wrong": "schema"})
    return tmp_path


def test_pilot_separates_selection_pending_and_execution_failures(pilot):
    result = evaluation.evaluate(pilot, "pilot", "dev")
    assert result["run"]["selected_cases"] == 4
    assert result["run"]["unselected_cases"] == 1
    assert result["direct"]["attempted"] == 4
    assert result["direct"]["overall_correct"] == 1
    assert result["direct"]["accuracy_completed"] == 0.25
    assert result["direct"]["outcomes"] == {"model_unknown": 1, "correct_infeasibility": 1,
                                             "timeout": 1, "execution_error": 1}
    assert result["assisted"]["attempted"] == 3
    assert result["assisted"]["pending"] == 1
    assert result["assisted"]["accuracy_completed"] == pytest.approx(2 / 3)
    assert result["assisted"]["outcomes"]["invalid_output"] == 1
    assert result["paired"] == {"completed_cases": 3, "both_correct": 1, "direct_only_correct": 0,
                                "assisted_only_correct": 1, "neither_correct": 1}
    with (pilot / "results/pilot/summary.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 10
    unselected = [r for r in rows if r["selected"] == "False"]
    assert all(r["outcome"] == "not_selected" and r["success"] == "" for r in unselected)
    pending = next(r for r in rows if r["case_id"] == "case-3" and r["approach"] == "assisted")
    assert pending["outcome"] == "pending" and pending["success"] == ""


def test_correct_infeasibility_does_not_imply_faithful_translation(pilot):
    result = evaluation.evaluate(pilot, "pilot", "dev")
    assert result["assisted"]["translations_audited"] == 2
    assert result["assisted"]["canonical_translations"] == 1
    assert result["assisted"]["correct_with_translation_differences"] == 1
    cell = next(c for c in result["by_horizon_difficulty"]
                if c["remaining_semesters"] == 2 and c["difficulty"] == "hard")
    assert cell["assisted"]["overall_correct"] == 1
    assert cell["assisted"]["canonical_translations"] == 0
    audit = json.loads((pilot / "results/runs/pilot/case-2-assisted/translation_audit.json").read_text())
    assert audit["differences"] == ["forbidden"]
    assert not audit["canonical_match"]
    assert audit["semantic_status"] == "review_required"
    assert result["assisted"]["translations_requiring_semantic_review"] == 1


def test_explanation_content_does_not_override_primary_correctness(pilot):
    attempt(pilot, "case-1", "direct", "ok", {
        "status": "feasible", "semesters": [["A"], [], [], []],
        "explanation": "Two courses were scheduled.",
    })
    attempt(pilot, "case-3", "direct", "ok", {
        "status": "feasible", "semesters": [["A"], ["A"], [], []],
        "explanation": "Every course is scheduled only once and all requirements are satisfied.",
    })
    attempt(pilot, "case-4", "direct", "ok", {
        "status": "infeasible", "semesters": [], "explanation": "This is definitely impossible.",
    })
    result = evaluation.evaluate(pilot, "pilot", "dev")
    assert result["direct"]["overall_correct"] == 2
    assert result["direct"]["outcomes"] == {
        "valid_plan": 1, "correct_infeasibility": 1, "invalid_plan": 1, "false_infeasibility": 1,
    }
    assert result["scoring_policy"]["id"] == "outcome-v1-explanation-secondary"
    saved = json.loads((pilot / "results/pilot/metrics.json").read_text())
    assert saved["scoring_policy"] == result["scoring_policy"]


def test_redundant_required_entry_is_a_canonical_difference_not_a_fidelity_verdict(pilot):
    path = pilot / "data/benchmark/gold.jsonl"
    answers = [json.loads(line) for line in path.read_text().splitlines()]
    original = answers[0]["spec"]
    original["fixed"] = [{"course": "B", "semester": 2}]
    path.write_text("".join(json.dumps(v) + "\n" for v in answers), encoding="utf-8")
    equivalent = copy.deepcopy(original)
    equivalent["required"].append("B")
    attempt(pilot, "case-1", "assisted", "ok", equivalent)
    evaluation.evaluate(pilot, "pilot", "dev")
    with (pilot / "results/pilot/summary.csv").open(newline="", encoding="utf-8") as stream:
        row = next(r for r in csv.DictReader(stream)
                   if r["case_id"] == "case-1" and r["approach"] == "assisted")
    assert row["success"] == "True"
    assert row["translation_canonical_match"] == "False"
    assert row["translation_semantic_status"] == "review_required"
    assert "translation_faithful" not in row
    audit = json.loads((pilot / "results/runs/pilot/case-1-assisted/translation_audit.json").read_text())
    assert audit["differences"] == ["required"]


def test_run_selection_cannot_expand_under_the_same_name(pilot, monkeypatch):
    monkeypatch.setattr(codex_runner, "require_current_benchmark", lambda root: None)
    monkeypatch.setattr(codex_runner, "verify_manifest", lambda *args: None)
    monkeypatch.setattr(codex_runner, "fingerprints", lambda *args: {})
    monkeypatch.setattr(codex_runner.shutil, "which", lambda name: "test-cli")
    monkeypatch.setattr(codex_runner.subprocess, "check_output", lambda *args, **kwargs: "test-version")
    monkeypatch.setattr(codex_runner, "run_one", lambda *args: {"status": "ok", "elapsed_seconds": 0})
    assert codex_runner.run(pilot, "dev", 1, "selection")
    with pytest.raises(ValueError, match="Selected cases changed"):
        codex_runner.run(pilot, "dev", 2, "selection")
    with pytest.raises(ValueError, match="Limit"):
        codex_runner.run(pilot, "dev", 0, "empty")
