"""Proposal sub-problems 1-3 and evaluation: a small command-line entry point."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .collect import collect, read_json
from .normalize import normalize
from .benchmark import build, load_jsonl
from .solver import solve
from .checker import check
from .codex_runner import run
from .evaluate import evaluate, verify_benchmark

def main():
    parser = argparse.ArgumentParser(description="NUS CS/AI simplified Programme planning experiment")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    collect_parser = commands.add_parser("collect")
    collect_parser.add_argument("--refresh", action="store_true")
    commands.add_parser("benchmark")
    commands.add_parser("verify")
    solve_parser = commands.add_parser("solve")
    solve_parser.add_argument("case_id")
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--split", choices=["dev","test"], default="dev")
    run_parser.add_argument("--limit", type=int)
    run_parser.add_argument("--name", default="initial")
    evaluate_parser = commands.add_parser("evaluate")
    evaluate_parser.add_argument("--split", choices=["dev","test"], default="test")
    evaluate_parser.add_argument("--name", default="initial")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "collect":
        collect(root, args.refresh)
        normalize(root)
    elif args.command == "benchmark": build(root)
    elif args.command == "verify": verify_benchmark(root)
    elif args.command == "run":
        if not run(root, args.split, args.limit, args.name): raise SystemExit(1)
    elif args.command == "evaluate": evaluate(root, args.name, args.split)
    else:
        courses = read_json(root / "data/courses.json")
        req = read_json(root / "data/requirements.json")
        case = next(c for c in load_jsonl(root / "data/benchmark/gold.jsonl") if c["id"] == args.case_id)
        plan = solve(case["spec"], courses, req["corequisite_pairs"])
        print(json.dumps({"plan": plan, "check": check(plan, case["spec"], courses, req["corequisite_pairs"])}, indent=2))

if __name__ == "__main__":
    main()
