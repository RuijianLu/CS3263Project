"""Proposal sub-problems 1-3: inspect, solve and check the CSP in separate stages."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .collect import collect, read_json
from .normalize import normalize
from .benchmark import build
from .checker import check
from .codex_runner import run
from .evaluate import evaluate
from .inspection import load_spec, inspect, solve_and_export, verify_examples


def output_folder(root, value, default):
    allowed = (root / "results/validation").resolve()
    target = Path(value) if value else allowed / default
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    if not target.is_relative_to(allowed):
        raise ValueError("Local CSP artifacts must be saved inside results/validation")
    return target


def main():
    parser = argparse.ArgumentParser(description="16-unit NUS CS/AI feasibility CSP")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    collect_parser = commands.add_parser("collect")
    collect_parser.add_argument("--refresh", action="store_true")
    p = commands.add_parser("benchmark", help="Build and locally validate 24 development + 120 evaluation cases")
    p.add_argument("--seed", type=int, default=3263)
    commands.add_parser("verify", help="Solve and independently validate the two current examples")
    for name in ("solve", "inspect-csp"):
        p = commands.add_parser(name)
        p.add_argument("spec", help="Specification JSON path or example name")
        p.add_argument("--output", help="Directory inside results/validation")
        if name == "solve":
            p.add_argument("--time-limit", type=float, default=10)
    p = commands.add_parser("check", help="Independently check a saved plan against its specification")
    p.add_argument("spec")
    p.add_argument("plan", type=Path)
    p.add_argument("--json", action="store_true", help="Print every detailed check record")
    for name in ("run", "evaluate"):
        p = commands.add_parser(name, help="Future comparison; requires a new 16-unit benchmark")
        p.add_argument("--split", choices=["dev","test"], default="dev" if name == "run" else "test")
        p.add_argument("--name", default="csp16")
        if name == "run":
            p.add_argument("--limit", type=int)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == "collect":
            collect(root, args.refresh)
            normalize(root)
        elif args.command == "benchmark":
            result = build(root, args.seed)
            print(f"Benchmark validated: {result['cases']} cases; {result['feasible']} feasible, {result['infeasible']} infeasible; no model calls.")
            print(f"Review index: {root / 'data/benchmark/README.md'}")
        elif args.command == "verify":
            print("\n".join(verify_examples(root)))
        elif args.command == "run":
            if not run(root, args.split, args.limit, args.name):
                raise SystemExit(1)
        elif args.command == "evaluate":
            evaluate(root, args.name, args.split)
        elif args.command == "check":
            spec, _ = load_spec(root, args.spec)
            plan_path = args.plan if args.plan.is_absolute() else root / args.plan
            checked = check(read_json(plan_path), spec, read_json(root / "data/courses.json"),
                            read_json(root / "data/requirements.json")["corequisite_pairs"])
            if args.json:
                print(json.dumps(checked, indent=2))
            else:
                passed = sum(c["passed"] for c in checked["checks"])
                print(f"Independent validation: {'PASS' if checked['valid'] else 'FAIL'}; {passed}/{len(checked['checks'])} checks passed")
                for semester in checked["semesters"]:
                    print(f"Position {semester['position']} (normal Semester {semester['normal_semester']}): {semester['units']:g}/{semester['max_units']} units")
                for group in checked["groups"]:
                    print(f"{group['name']}: {group['units']:g} units, {group['course_count']} courses; {'PASS' if group['passed'] else 'FAIL'}")
                for violation in checked["violations"]:
                    print(f"{violation['type']}: {violation['message']}")
            if not checked["valid"]:
                raise SystemExit(1)
        else:
            spec, source = load_spec(root, args.spec)
            default = source.stem + ("-inspection" if args.command == "inspect-csp" else "")
            output = output_folder(root, args.output, default)
            if args.command == "inspect-csp":
                if (output / "plan.json").exists():
                    raise ValueError("Choose a separate inspection directory to avoid mixing new inputs with an old plan")
                problem, _, _ = inspect(root, spec, output)
                print(f"Compiled CSP: {problem.inspection['variable_count']} variables; "
                      f"{problem.inspection['constraint_count']} constraints; no objective.")
                print(f"Inspection saved to {output / 'csp.md'}")
            else:
                plan, checked = solve_and_export(root, spec, source, output, args.time_limit)
                print(f"Status: {plan['status']}; independent validation: "
                      + ("PASS" if checked["valid"] else "FAIL / no feasible schedule"))
                print(f"Readable report: {output / 'report.md'}")
                if not checked["valid"]:
                    raise SystemExit(1)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    main()
