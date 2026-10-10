"""Proposal evaluation: paired outcomes, translation audits and concise results."""
from __future__ import annotations
from collections import Counter
import csv
import json
from pathlib import Path
from .collect import read_json, write_json
from .benchmark import load_jsonl
from .checker import check, translation_differences
from .schemas import PLAN_SCHEMA, validate, validate_spec
from .solver import solve
from .protocol import verify_manifest, require_current_benchmark

def evaluate(root, run_name="initial", split="test"):
    require_current_benchmark(root)
    courses, req = read_json(root / "data/courses.json"), read_json(root / "data/requirements.json")
    cases = load_jsonl(root / f"data/benchmark/{split}.jsonl")
    gold = {g["id"]: g for g in load_jsonl(root / "data/benchmark/gold.jsonl")}
    run_folder = root / "results/runs" / run_name
    verify_manifest(root, read_json(run_folder / "manifest.json"), split, read_json(root / "experiment.json"))
    records, examples = [], []
    for case in cases:
        answer = gold[case["id"]]
        for approach in ("direct", "assisted"):
            folder = run_folder / f"{case['id']}-{approach}"
            row = {"case_id": case["id"], "difficulty": case["difficulty"], "approach": approach,
                   "gold_status": answer["status"], "execution_status": "not_run", "predicted_status": "",
                   "success": False, "valid_plan": False, "violations": "", "translation_differences": "",
                   "elapsed_seconds": "", "solver_seconds": "", "input_tokens": "", "output_tokens": ""}
            if (folder / "record.json").exists():
                record = read_json(folder / "record.json")
                row["execution_status"] = record["status"]
                row["elapsed_seconds"] = record.get("elapsed_seconds", "")
                for name in ("input_tokens", "output_tokens"):
                    row[name] = (record.get("usage") or {}).get(name, "")
                if record["status"] == "ok":
                    try:
                        output = read_json(folder / "response.json")
                        if approach == "assisted":
                            validate_spec(output, courses)
                            diffs = translation_differences(output, answer["spec"])
                            row["translation_differences"] = "|".join(diffs)
                            import time
                            start = time.monotonic()
                            plan = solve(output, courses, req["corequisite_pairs"],
                                         read_json(root / "experiment.json")["solver_timeout_seconds"])
                            row["solver_seconds"] = round(time.monotonic() - start, 4)
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
                        row["success"] = ((answer["status"] == "feasible" and row["valid_plan"])
                                          or (answer["status"] == "infeasible" and plan["status"] == "infeasible"))
                    except Exception as exc:
                        row["execution_status"] = "invalid_output"
                        row["violations"] = "format_or_compile"
                        write_json(folder / "check.json", {"valid": False, "error": str(exc)})
            records.append(row)
            if not row["success"] and row["execution_status"] != "not_run":
                examples.append(row)
    out = root / "results" / run_name
    out.mkdir(parents=True, exist_ok=True)
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    lines = [
        "# Initial degree-planning evaluation",
        "",
        f"Run: {run_name}; split: {split}. Results apply only to the simplified benchmark.",
        "Pending cases are retained in denominators and explicitly reported; they are not model successes or model failures.",
        "",
        "| Approach | Completed attempts | Valid feasible plans | Correct infeasibility | False infeasibility | Overall correct |",
        "|---|---:|---:|---:|---:|---:|"
    ]
    summary = {}
    for approach in ("direct", "assisted"):
        rows = [r for r in records if r["approach"] == approach]
        feasible = [r for r in rows if r["gold_status"] == "feasible"]
        impossible = [r for r in rows if r["gold_status"] == "infeasible"]
        attempted = sum(r["execution_status"] not in {"not_run", "running"} for r in rows)
        passed = sum(r["valid_plan"] for r in feasible)
        correct_inf = sum(r["success"] for r in impossible)
        false_inf = sum(r["predicted_status"] == "infeasible" for r in feasible)
        correct = sum(r["success"] for r in rows)
        summary[approach] = {"attempted": attempted, "total": len(rows), "feasible_valid": passed,
                             "feasible_total": len(feasible), "infeasible_correct": correct_inf,
                             "infeasible_total": len(impossible), "false_infeasibility": false_inf,
                             "overall_correct": correct,
                             "execution_statuses": dict(Counter(r["execution_status"] for r in rows))}
        lines.append(f"| {approach} | {attempted}/{len(rows)} | {passed}/{len(feasible)} | "
                     f"{correct_inf}/{len(impossible)} | {false_inf} | {correct}/{len(rows)} |")
    lines += ["", "## Results by designed difficulty", "",
              "| Difficulty | Direct correct | Assisted correct |", "|---|---:|---:|"]
    for level in ("easy","medium","hard"):
        cells = []
        for approach in ("direct","assisted"):
            rows = [r for r in records if r["difficulty"]==level and r["approach"]==approach]
            cells.append(f"{sum(r['success'] for r in rows)}/{len(rows)}")
        lines.append(f"| {level} | {' | '.join(cells)} |")
    lines += ["", "## Runtime and reported usage", "",
              "| Approach | Mean completed process + solver seconds | Reported input tokens | Reported output tokens |",
              "|---|---:|---:|---:|"]
    for approach in ("direct", "assisted"):
        rows = [r for r in records if r["approach"] == approach and r["execution_status"] not in {"not_run", "running"}]
        times = [float(r["elapsed_seconds"]) + float(r["solver_seconds"] or 0) for r in rows if r["elapsed_seconds"] != ""]
        inputs = sum(int(r["input_tokens"]) for r in rows if r["input_tokens"] != "")
        outputs = sum(int(r["output_tokens"]) for r in rows if r["output_tokens"] != "")
        mean = round(sum(times)/len(times), 2) if times else None
        summary[approach]["mean_total_seconds"] = mean
        summary[approach]["reported_input_tokens"] = inputs
        summary[approach]["reported_output_tokens"] = outputs
        lines.append(f"| {approach} | {mean if mean is not None else 'pending'} | {inputs} | {outputs} |")
    lines += ["", "## Translation audit", "",
              "Differences compare canonical fields and named group membership against the reference specification. "
              "They are diagnostic mismatches, not a proof that every alternative representation is semantically wrong."]
    assisted = [r for r in records if r["approach"]=="assisted" and r["execution_status"]=="ok"]
    lines.append(f"Canonical translations without differences: {sum(not r['translation_differences'] for r in assisted)}/{len(assisted)}.")
    lines += ["", "## Representative failures", ""]
    for row in examples[:6]:
        lines.append(f"- {row['case_id']} ({row['approach']}): status={row['execution_status']}; "
                     f"answer={row['predicted_status'] or 'none'}; violations={row['violations'] or 'none'}; "
                     f"translation differences={row['translation_differences'] or 'none'}.")
    if not examples: lines.append("No completed failing attempts.")
    lines += ["", "## Interpretation and responsible AI", "",
              "The profiles are synthetic; these are controlled related cases, not a representative sample of NUS students. "
              "No personal academic records were used. Fixed offerings, admission assumptions, a limited elective catalogue, "
              "and completed internship credit limit realism. This is not a graduation audit or academic advice.",
              "Team members must review source interpretations and labels. Document human and AI contributions in the final report. "
              "A solver validates the translated model; only the independent checker evaluates the original request.",
              "Token counts describe subscription usage when supplied; no per-call dollar cost is inferred.",
              ""]
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
