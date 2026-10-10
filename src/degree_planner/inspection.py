"""Proposal sub-problems 1-3: readable CSP and independent-validation artifacts."""
from __future__ import annotations
from collections import Counter
import csv
import hashlib
from pathlib import Path
from .collect import read_json, write_json
from .benchmark import request
from .csp import build_csp
from .checker import check
from .solver import solve_csp


def load_spec(root, value):
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        path = root / "data/examples" / f"{value}.json"
    if not path.is_file():
        raise ValueError("Provide a specification JSON path or an example name: foundation-remaining, ai-remaining")
    return read_json(path), path.resolve()


def inspect(root, spec, output):
    courses = read_json(root / "data/courses.json")
    req = read_json(root / "data/requirements.json")
    problem = build_csp(spec, courses, req["corequisite_pairs"])
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "spec.json", spec)
    write_json(output / "csp.json", problem.inspection)
    if not problem.model.export_to_file(str(output / "model.pbtxt")):
        raise OSError("Could not export the compiled model")
    (output / "request.txt").write_text(request(spec) + "\n\n"
        "This local example specification was assembled from the agreed rules; no model translation was run.\n",
        encoding="utf-8")
    lines = ["# Compiled CSP inspection", "",
             f"- Workload cap: {spec['max_units']} units per normal semester.",
             f"- Remaining normal semesters: {spec['semesters']}.",
             "- Objective: none; find any satisfying assignment.",
             f"- Variables: {problem.inspection['variable_count']}.",
             f"- Constraints: {problem.inspection['constraint_count']}.", "",
             "All decision and logical auxiliary variables have domain {0,1}. Backend constants have singleton domains.",
             "Semester suffixes are remaining positions (1-based), not normal Semester 1/2.",
             "csp.json lists every variable/domain and constraint description; backend_index points into model.pbtxt.", "",
             "| Constraint family | Number |", "|---|---:|"]
    for family, count in sorted(problem.inspection["constraint_families"].items()):
        lines.append(f"| {family} | {count} |")
    lines += ["", "## Mandatory new enrolments", "",
              ", ".join(sorted((set(spec["required"]) | {f["course"] for f in spec["fixed"]}) - set(spec["completed"]))) or "(none)",
              "", "## Requirement groups", "",
              "| Group | Minimum units | Maximum units | Minimum courses | Maximum courses |",
              "|---|---:|---:|---:|---:|"]
    for g in spec["groups"]:
        values = [g[k] if g[k] is not None else "-" for k in ("min_units","max_units","min_courses","max_courses")]
        lines.append(f"| {g['name']} | " + " | ".join(map(str, values)) + " |")
    lines += ["", "## Fixed new enrolments", ""]
    lines.extend(f"- {f['course']}: remaining position {f['semester']}." for f in spec["fixed"])
    if not spec["fixed"]:
        lines.append("None.")
    (output / "csp.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return problem, courses, req


def render_report(spec, plan, checked, courses):
    lines = ["# Local CSP solution and validation", "",
             f"Solver status: **{plan['status']}**. Independent schedule validation: **"
             + ("PASS" if checked["valid"] else "FAIL / no feasible schedule") + "**.", "",
             plan["explanation"], "",
             "This is local feasibility validation, not a comparison experiment or a graduation audit.", "",
             "## 1. Input specification", "",
             f"Maximum workload: **{spec['max_units']} units**, no minimum.",
             f"Remaining normal semesters: {spec['semesters']}.",
             f"Completed record: {', '.join(spec['completed']) or '(empty)'}.",
             "Read spec.json for the exact required, forbidden, fixed and group fields.", "",
             "## 2. Compiled CSP", "",
             "Read csp.md for the overview, csp.json for every variable and constraint, and model.pbtxt for the actual CP-SAT model.",
             "The model has no course-count or semester-position objective.", "",
             "## 3. Schedule", "",
             "| Remaining position | Normal semester | Units / cap | Courses |", "|---:|---:|---:|---|"]
    for semester in checked["semesters"]:
        lines.append(f"| {semester['position']} | {semester['normal_semester']} | "
                     f"{semester['units']:g} / {semester['max_units']} | "
                     f"{', '.join(semester['courses']) or '(empty)'} |")
    lines += ["", "Course titles and credits are listed in schedule.csv. Completed courses are not repeated.", "",
              "## 4. Independent checks", "",
              "| Check family | Passed | Total |", "|---|---:|---:|"]
    total = Counter(item["type"] for item in checked["checks"])
    passed = Counter(item["type"] for item in checked["checks"] if item["passed"])
    for kind in sorted(total):
        lines.append(f"| {kind} | {passed[kind]} | {total[kind]} |")
    lines += ["", "### Programme group totals", "",
              "| Group | Actual units | Actual courses | Unit bounds | Course bounds | Pass |",
              "|---|---:|---:|---|---|---|"]
    def bounds(lo, hi):
        return f"{lo if lo is not None else '-'} .. {hi if hi is not None else '-'}"
    for g in checked["groups"]:
        lines.append(f"| {g['name']} | {g['units']:g} | {g['course_count']} | "
                     f"{bounds(g['min_units'],g['max_units'])} | "
                     f"{bounds(g['min_courses'],g['max_courses'])} | {g['passed']} |")
    lines += ["", "Each group's matched courses:", ""]
    for g in checked["groups"]:
        lines.append(f"- {g['name']}: {', '.join(g['matched_courses']) or '(none)'}.")
    lines += ["", "### Violations", ""]
    if checked["violations"]:
        for violation in checked["violations"]:
            lines.append(f"- {violation['type']}: {violation['message']}")
    else:
        lines.append("None. All checks passed.")
    lines += ["", "validation.json contains individual pass/fail checks and group membership.",
              "A non-feasible plan has no independently validated schedule; only CP-SAT can supply its infeasibility proof.",
              ""]
    return "\n".join(lines)


def solve_and_export(root, spec, source, output, time_limit=10):
    if time_limit <= 0:
        raise ValueError("Solver time limit must be positive")
    problem, courses, req = inspect(root, spec, output)
    plan = solve_csp(problem, time_limit)
    checked = check(plan, spec, courses, req["corequisite_pairs"])
    write_json(output / "plan.json", plan)
    write_json(output / "validation.json", checked)
    with (output / "schedule.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["remaining_position","normal_semester","course","title","units"])
        for semester in checked["semesters"]:
            for code in semester["courses"]:
                if code in courses:
                    writer.writerow([semester["position"],semester["normal_semester"],code,
                                     courses[code]["title"],courses[code]["units"]])
    (output / "report.md").write_text(render_report(spec, plan, checked, courses), encoding="utf-8")
    paths = ["data/courses.json", "data/requirements.json",
             "src/degree_planner/csp.py", "src/degree_planner/solver.py", "src/degree_planner/checker.py",
             "src/degree_planner/schemas.py", "src/degree_planner/policy.py", "src/degree_planner/inspection.py"]
    write_json(output / "manifest.json", {
        "formulation": problem.inspection["formulation"], "objective": None,
        "spec_source": str(source), "max_units": spec["max_units"],
        "artifact_sha256": {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths},
        "spec_sha256": hashlib.sha256((output / "spec.json").read_bytes()).hexdigest(),
        "validation_only": True, "model_calls": 0})
    return plan, checked


def verify_examples(root):
    summaries = []
    for name in ("foundation-remaining", "ai-remaining"):
        spec, source = load_spec(root, name)
        output = root / "results/validation" / name
        plan, checked = solve_and_export(root, spec, source, output)
        if plan["status"] != "feasible" or not checked["valid"]:
            raise ValueError(f"{name}: no independently validated feasible schedule; inspect {output}")
        summaries.append(f"{name}: feasible; all independent checks passed ({spec['max_units']}-unit cap)")
    return summaries
