"""Proposal evaluation: selected-case outcomes, paired results and translation audits."""
from __future__ import annotations

from collections import Counter
import csv
import json
import time

from .collect import read_json, write_json
from .benchmark import load_jsonl
from .checker import check, translation_differences
from .schemas import PLAN_SCHEMA, validate, validate_spec
from .solver import solve
from .protocol import verify_manifest, require_current_benchmark

APPROACHES = ("direct", "assisted")
PENDING = {"not_run", "running"}
SCORING_POLICY = {
    "id": "outcome-v1-explanation-secondary",
    "primary": {
        "feasible": "A schema-valid plan passes the independent checker against the original specification.",
        "infeasible": "A schema-valid infeasible answer agrees with the validated gold label.",
        "denominator": "Completed selected attempts, including execution and output failures; pending and unselected attempts excluded.",
    },
    "explanations": {
        "role": "Secondary manual review; explanation content does not change primary scores.",
        "infeasibility": "Any sufficient contradiction is acceptable; the annotated witness need not be the only cause.",
        "format": "Output schema requirements still apply; where required, the explanation field remains mandatory.",
    },
    "translations": {
        "role": "Separate diagnostic; canonical field differences do not change primary outcome scores.",
        "semantic_review": "Differences require review as equivalent, non-equivalent or unresolved; outcome agreement alone does not establish fidelity.",
    },
}


def completed(row):
    return row["selected"] and row["execution_status"] not in PENDING


def summarize(rows):
    """Pending and unselected cases never enter completed-attempt accuracy denominators."""
    selected = [r for r in rows if r["selected"]]
    finished = [r for r in selected if completed(r)]
    feasible = [r for r in finished if r["gold_status"] == "feasible"]
    impossible = [r for r in finished if r["gold_status"] == "infeasible"]
    translated = [r for r in finished if r["translation_audited"]]
    correct = sum(r["success"] is True for r in finished)
    times = [float(r["elapsed_seconds"]) + float(r["solver_seconds"] or 0)
             for r in finished if r["elapsed_seconds"] != ""]
    return {
        "total": len(selected), "attempted": len(finished),
        "pending": len(selected) - len(finished), "unselected": len(rows) - len(selected),
        "feasible_valid": sum(r["valid_plan"] is True for r in feasible), "feasible_total": len(feasible),
        "infeasible_correct": sum(r["success"] is True for r in impossible), "infeasible_total": len(impossible),
        "false_infeasibility": sum(r["predicted_status"] == "infeasible" for r in feasible),
        "overall_correct": correct, "accuracy_completed": correct / len(finished) if finished else None,
        "execution_statuses": dict(Counter(r["execution_status"] for r in selected)),
        "outcomes": dict(Counter(r["outcome"] for r in selected)),
        "translations_audited": len(translated),
        "canonical_translations": sum(r["translation_canonical_match"] is True for r in translated),
        "translations_requiring_semantic_review": sum(r["translation_canonical_match"] is False for r in translated),
        "correct_with_translation_differences": sum(r["success"] is True and
                                                    r["translation_canonical_match"] is False for r in translated),
        "mean_total_seconds": round(sum(times) / len(times), 2) if times else None,
        "reported_input_tokens": sum(int(r["input_tokens"]) for r in finished if r["input_tokens"] != ""),
        "reported_output_tokens": sum(int(r["output_tokens"]) for r in finished if r["output_tokens"] != ""),
    }


def evaluate(root, run_name="initial", split="test"):
    require_current_benchmark(root)
    config = read_json(root / "experiment.json")
    courses, req = read_json(root / "data/courses.json"), read_json(root / "data/requirements.json")
    cases = load_jsonl(root / f"data/benchmark/{split}.jsonl")
    gold = {g["id"]: g for g in load_jsonl(root / "data/benchmark/gold.jsonl")}
    run_folder = (root / "results/runs" / run_name).resolve()
    if not run_folder.is_relative_to((root / "results/runs").resolve()):
        raise ValueError("Run name must stay within results/runs")
    manifest = read_json(run_folder / "manifest.json")
    verify_manifest(root, manifest, split, config)
    case_ids = [c["id"] for c in cases]
    selected_ids = manifest.get("case_ids", case_ids)
    if not selected_ids or len(set(selected_ids)) != len(selected_ids) or not set(selected_ids) <= set(case_ids):
        raise ValueError("Run selection must contain distinct cases from its split")
    selected = set(selected_ids)
    records = []
    for order, case in enumerate(cases, 1):
        answer = gold[case["id"]]
        for approach in APPROACHES:
            folder = run_folder / f"{case['id']}-{approach}"
            row = {
                "case_id": case["id"], "case_order": order, "selected": case["id"] in selected,
                "remaining_semesters": case.get("remaining_semesters", len(answer["spec"]["semesters"])),
                "difficulty": case["difficulty"], "history_id": case.get("history_id", ""),
                "infeasibility_mechanism": (answer.get("infeasibility_witness") or {}).get("kind", ""),
                "approach": approach, "gold_status": answer["status"], "execution_status": "not_run",
                "predicted_status": "", "outcome": "pending", "success": None, "valid_plan": None,
                "violations": "", "translation_audited": False, "translation_canonical_match": None,
                "translation_semantic_status": "not_audited",
                "translation_differences": "", "elapsed_seconds": "", "solver_seconds": "",
                "input_tokens": "", "output_tokens": "",
            }
            if not row["selected"]:
                row.update(execution_status="not_selected", outcome="not_selected")
            elif (folder / "record.json").exists():
                record = read_json(folder / "record.json")
                if record["case_id"] != case["id"] or record["approach"] != approach:
                    raise ValueError("Attempt identity does not match its case directory")
                row["execution_status"] = record["status"]
                row["elapsed_seconds"] = record.get("elapsed_seconds", "")
                for name in ("input_tokens", "output_tokens"):
                    row[name] = (record.get("usage") or {}).get(name, "")
                if record["status"] not in PENDING:
                    row.update(success=False, outcome=record["status"])
                if record["status"] == "ok":
                    try:
                        output = read_json(folder / "response.json")
                        if approach == "assisted":
                            validate_spec(output, courses)
                            diffs = translation_differences(output, answer["spec"])
                            semantic_status = "review_required" if diffs else "canonical_match"
                            row.update(translation_audited=True, translation_canonical_match=not diffs,
                                       translation_semantic_status=semantic_status,
                                       translation_differences="|".join(diffs))
                            write_json(folder / "translation_audit.json", {
                                "canonical_match": not diffs, "differences": diffs,
                                "semantic_status": semantic_status,
                                "interpretation": "Field differences require semantic review; outcome correctness is scored separately.",
                            })
                            started = time.monotonic()
                            plan = solve(output, courses, req["corequisite_pairs"], config["solver_timeout_seconds"])
                            row["solver_seconds"] = round(time.monotonic() - started, 4)
                            write_json(folder / "solver_plan.json", plan)
                        else:
                            validate(output, PLAN_SCHEMA)
                            plan = output
                        row["predicted_status"] = plan["status"]
                        if plan["status"] == "feasible":
                            checked = check(plan, answer["spec"], courses, req["corequisite_pairs"])
                            row["valid_plan"] = checked["valid"]
                            row["violations"] = "|".join(sorted({e["type"] for e in checked["violations"]}))
                            write_json(folder / "check.json", checked)
                            row["outcome"] = "valid_plan" if checked["valid"] else "invalid_plan"
                        elif plan["status"] == "infeasible":
                            row["outcome"] = "correct_infeasibility" if answer["status"] == "infeasible" else "false_infeasibility"
                        else:
                            row["outcome"] = "solver_unknown" if approach == "assisted" else "model_unknown"
                        row["success"] = ((answer["status"] == "feasible" and row["valid_plan"] is True)
                                          or (answer["status"] == "infeasible" and plan["status"] == "infeasible"))
                    except Exception as exc:
                        row.update(outcome="invalid_output", violations="format_or_compile")
                        write_json(folder / "check.json", {"valid": False, "error": str(exc)})
            records.append(row)

    out = root / "results" / run_name
    out.mkdir(parents=True, exist_ok=True)
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    summary = {
        "scoring_policy": SCORING_POLICY,
        "run": {"name": run_name, "split": split, "selected_case_ids": selected_ids,
                "selected_cases": len(selected_ids), "split_cases": len(cases), "unselected_cases": len(cases)-len(selected_ids),
                "accuracy_denominator": "Completed selected attempts, including execution and output failures; pending attempts excluded."},
        **{a: summarize([r for r in records if r["approach"] == a]) for a in APPROACHES},
    }
    by_case = {(r["case_id"], r["approach"]): r for r in records}
    paired = [identifier for identifier in selected_ids
              if all(completed(by_case[identifier, a]) for a in APPROACHES)]
    summary["paired"] = {
        "completed_cases": len(paired),
        "both_correct": sum(all(by_case[c, a]["success"] is True for a in APPROACHES) for c in paired),
        "direct_only_correct": sum(by_case[c, "direct"]["success"] is True and by_case[c, "assisted"]["success"] is not True for c in paired),
        "assisted_only_correct": sum(by_case[c, "assisted"]["success"] is True and by_case[c, "direct"]["success"] is not True for c in paired),
        "neither_correct": sum(all(by_case[c, a]["success"] is not True for a in APPROACHES) for c in paired),
    }
    summary["by_horizon_difficulty"] = []
    for horizon in sorted({r["remaining_semesters"] for r in records if r["selected"]}, reverse=True):
        for difficulty in ("easy", "medium", "hard"):
            cell = [r for r in records if r["selected"] and r["remaining_semesters"] == horizon and r["difficulty"] == difficulty]
            if cell:
                summary["by_horizon_difficulty"].append({"remaining_semesters": horizon, "difficulty": difficulty,
                    **{a: summarize([r for r in cell if r["approach"] == a]) for a in APPROACHES}})

    def rate(value, denominator):
        return f"{value}/{denominator}" if denominator else "pending"

    lines = ["# Degree-planning development evaluation" if split == "dev" else "# Degree-planning evaluation", "",
             f"Run: {run_name}; split: {split}; model: {config['model']}; reasoning effort: {config['reasoning_effort']}.",
             f"Selected {len(selected_ids)} of {len(cases)} cases; {len(cases)-len(selected_ids)} cases were not selected.",
             "Accuracy uses completed selected attempts. Execution/output failures count as unsuccessful attempts; pending and unselected cases are reported separately.",
             "", "## Scoring policy", "",
             f"Policy: {SCORING_POLICY['id']}.",
             "Primary correctness measures schedule validity against the original specification or agreement with a validated infeasible label. "
             "Explanation content is reviewed manually as a secondary finding and does not change this score; schema requirements still apply. "
             "An infeasibility explanation may identify any sufficient contradiction, rather than reproducing the annotated witness.",
             "Translation canonical matches and semantic review are reported separately from outcome correctness. "
             "A field difference requires semantic review as equivalent, non-equivalent or unresolved; matching outcomes alone do not establish translation fidelity.",
             "", "## Outcomes", "",
             "| Approach | Completed / selected | Pending | Valid feasible plans | Correct infeasibility | False infeasibility | Overall correct / completed |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for approach in APPROACHES:
        m = summary[approach]
        lines.append(f"| {approach} | {m['attempted']}/{m['total']} | {m['pending']} | "
                     f"{rate(m['feasible_valid'],m['feasible_total'])} | {rate(m['infeasible_correct'],m['infeasible_total'])} | "
                     f"{m['false_infeasibility']} | {rate(m['overall_correct'],m['attempted'])} |")
    p = summary["paired"]
    lines += ["", f"Completed paired cases: {p['completed_cases']}; both correct: {p['both_correct']}; "
              f"direct only: {p['direct_only_correct']}; assisted only: {p['assisted_only_correct']}; neither: {p['neither_correct']}.",
              "", "## Horizon and designed difficulty", "",
              "| Remaining semesters | Difficulty | Direct correct / completed | Assisted correct / completed | Pending attempts |",
              "|---:|---|---:|---:|---:|"]
    for cell in summary["by_horizon_difficulty"]:
        cells = [rate(cell[a]["overall_correct"], cell[a]["attempted"]) for a in APPROACHES]
        lines.append(f"| {cell['remaining_semesters']} | {cell['difficulty']} | {' | '.join(cells)} | "
                     f"{sum(cell[a]['pending'] for a in APPROACHES)} |")
    lines += ["", "## Execution and answer status", "",
              "| Approach | Execution statuses | Scored outcomes |", "|---|---|---|"]
    for approach in APPROACHES:
        m = summary[approach]
        lines.append(f"| {approach} | {json.dumps(m['execution_statuses'],sort_keys=True)} | {json.dumps(m['outcomes'],sort_keys=True)} |")
    lines += ["", "## Runtime and reported usage", "",
              "| Approach | Mean completed process + solver seconds | Reported input tokens | Reported output tokens |",
              "|---|---:|---:|---:|"]
    for approach in APPROACHES:
        m = summary[approach]
        lines.append(f"| {approach} | {m['mean_total_seconds'] if m['mean_total_seconds'] is not None else 'pending'} | "
                     f"{m['reported_input_tokens']} | {m['reported_output_tokens']} |")
    assisted = summary["assisted"]
    lines += ["", "## Translation audit", "",
              f"Canonical translations without differences: {assisted['canonical_translations']}/{assisted['translations_audited']} schema-valid translations.",
              f"Correct outcomes with translation differences: {assisted['correct_with_translation_differences']}.",
              "Field and named-group differences are diagnostic mismatches, not proof of semantic inequivalence. Correct outcomes with differences require case-level review before being described as accidental correctness.",
              "", "## Case-level results", "",
              "| Case | Approach | Outcome | Violations | Translation differences |", "|---|---|---|---|---|"]
    for row in records:
        if row["selected"]:
            lines.append(f"| {row['case_id']} | {row['approach']} | {row['outcome']} | "
                         f"{row['violations'].replace('|', ', ') or '-'} | {row['translation_differences'].replace('|', ', ') or '-'} |")
    lines += ["", "## Interpretation and responsible AI", "",
              "These correlated synthetic cases are controlled instances, not representative student samples. Difficulty labels are designed, not empirically calibrated. "
              "Fixed offerings, admission assumptions, a restricted catalogue and credited internship limit realism. No personal transcripts were used; outputs are not academic advice.",
              "The solver checks a translated specification; feasible outputs are independently checked against the original specification. "
              "Correct infeasibility judgments and translation fidelity are separate findings. Raw responses are preserved without repairs or retries.",
              "Team members must review source interpretations and record actual human and AI contributions. Reported subscription tokens are not converted into per-call dollar costs.", ""]
    (out / "analysis.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(out / "metrics.json", summary)
    print(json.dumps(summary, indent=2))
    return summary


def verify_benchmark(root):
    require_current_benchmark(root)
    courses, req = read_json(root / "data/courses.json"), read_json(root / "data/requirements.json")
    counts = Counter()
    for gold in load_jsonl(root / "data/benchmark/gold.jsonl"):
        result = solve(gold["spec"], courses, req["corequisite_pairs"])
        if result["status"] != gold["status"]:
            raise RuntimeError(f"Label mismatch: {gold['id']}")
        if result["status"] == "feasible" and not check(result, gold["spec"], courses, req["corequisite_pairs"])["valid"]:
            raise RuntimeError(f"Invalid reference: {gold['id']}")
        counts[gold["status"]] += 1
    print(f"Verified benchmark: {dict(counts)}")
