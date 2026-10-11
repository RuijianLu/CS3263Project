"""Proposal sub-problems 1-3 and evaluation: reject false history credit and bad labels."""
import copy
import json
import shutil
from pathlib import Path
import pytest
from degree_planner.benchmark import GENERATOR_PATHS, load_jsonl, verify_witness
from degree_planner.collect import read_json
from degree_planner.histories import validate_history
from degree_planner.protocol import require_current_benchmark

ROOT = Path(__file__).resolve().parents[1]


def test_past_credit_cannot_be_added_without_a_matching_history():
    answer = load_jsonl(ROOT/"data/benchmark/gold.jsonl")[0]
    history = copy.deepcopy(answer["history"])
    history["completed"] = sorted(set(history["completed"]) | {"CS4246"})
    with pytest.raises(ValueError, match="completed record"):
        validate_history(history, read_json(ROOT/"data/courses.json"),
                         read_json(ROOT/"data/requirements.json")["corequisite_pairs"])


def test_infeasibility_witness_cannot_claim_a_removed_conflict():
    answer = next(a for a in load_jsonl(ROOT/"data/benchmark/gold.jsonl")
                  if (a["infeasibility_witness"] or {}).get("kind") == "required_forbidden")
    repaired = answer["feasible_precursor"]["spec"]
    with pytest.raises(ValueError, match="does not follow"):
        verify_witness(repaired, answer["infeasibility_witness"],
                       read_json(ROOT/"data/courses.json"), read_json(ROOT/"data/requirements.json"))


@pytest.fixture
def frozen_benchmark(tmp_path):
    manifest = read_json(ROOT/"data/benchmark/manifest.json")
    paths = list(GENERATOR_PATHS) + [f"data/benchmark/{name}" for name in manifest["artifact_sha256"]]
    paths.append("data/benchmark/manifest.json")
    for name in paths:
        destination = tmp_path/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/name, destination)
    return tmp_path


def test_changed_request_requires_revalidation(frozen_benchmark):
    path = frozen_benchmark/"data/benchmark/test.jsonl"
    cases = load_jsonl(path)
    cases[0]["request"] += " Take CS4246 in the first remaining semester."
    path.write_text("".join(json.dumps(c) + "\n" for c in cases), encoding="utf-8")
    with pytest.raises(ValueError, match="artifact changed"):
        require_current_benchmark(frozen_benchmark)


def test_changed_solver_requires_revalidation(frozen_benchmark):
    path = frozen_benchmark/"src/degree_planner/csp.py"
    path.write_text(path.read_text(encoding="utf-8") + "\n# Subsequent model revision.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="solver implementation changed"):
        require_current_benchmark(frozen_benchmark)


def test_hard_negative_cases_do_not_have_a_direct_required_forbidden_conflict():
    answers = load_jsonl(ROOT/"data/benchmark/gold.jsonl")
    for answer in answers:
        if "-hard-" in answer["id"] and answer["status"] == "infeasible":
            spec = answer["spec"]
            assert not ((set(spec["required"]) - set(spec["completed"])) & set(spec["forbidden"]))
