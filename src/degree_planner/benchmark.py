"""Proposal sub-problems 1-3: controlled, labelled natural-language instances."""
from __future__ import annotations
import copy
import hashlib
import json
from .collect import read_json, write_json
from .solver import solve
from .checker import check

def jsonl(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in values), encoding="utf-8")

def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def group(name, codes, min_units=None, max_units=None, min_courses=None, max_courses=None):
    return dict(name=name, courses=sorted(codes), min_units=min_units, max_units=max_units,
                min_courses=min_courses, max_courses=max_courses)

def gold_spec(courses, req, completed, horizon=3, start=1, required=(), forbidden=(), fixed=()):
    breadth = {c for c, v in courses.items() if v["category"] in {"breadth", "industry"}}
    programme = breadth | set(req["foundation"] + req["mathematics"])
    primary = set(req["ai_primaries"]) & courses.keys()
    groups = [
        group("breadth", breadth, min_units=req["breadth_min_units"]),
        group("breadth_upper", {c for c in breadth if courses[c]["level"] >= 4000}, min_units=12),
        group("ai_primary", primary, min_courses=3),
        group("ai_upper", {c for c in primary if courses[c]["level"] >= 4000}, min_courses=1),
        group("industry", {c for c in breadth if courses[c]["category"] == "industry"}, min_units=6, max_units=12),
        group("cp_non_industry", {c for c in breadth if c.startswith("CP") and courses[c]["category"] != "industry"}, max_units=12),
        group("programme_lower", {c for c in programme if 1000 <= courses[c]["level"] <= 4000}, min_units=64)
    ]
    return {"completed": sorted(completed), "semesters": [1 + ((start - 1 + t) % 2) for t in range(horizon)],
            "max_units": 32, "required": sorted(set(req["foundation"] + req["mathematics"]) | set(required)),
            "forbidden": sorted(forbidden),
            "fixed": [{"course": c, "semester": t} for c, t in fixed], "groups": groups}

def request(spec):
    text = (f"I am a standard single-degree NUS Computer Science student under the AY2026/27 "
            f"admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining "
            f"Programme Requirements only. I have passed {', '.join(spec['completed'])}. "
            f"CP3200 is already completed and contributes 6 industry-experience units. "
            f"I have {len(spec['semesters'])} remaining normal semesters, starting with "
            f"Semester {spec['semesters'][0]}; Semester 1 and Semester 2 alternate. "
            f"The maximum is 32 units per semester with no minimum. "
            f"Use the supplied snapshot's recurring offerings. All qualifying mathematics and English "
            f"admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. ")
    core = {"CS1231S","CS2030S","CS2040S","CS2100","CS2101","CS2103T","CS2106","CS2109S","CS3230",
            "MA1521","MA1522","ST2334"}
    extra = set(spec["required"]) - core
    if extra: text += f"My plan must include {', '.join(sorted(extra))}. "
    if spec["forbidden"]: text += f"Do not newly enroll in {', '.join(spec['forbidden'])}. "
    for f in spec["fixed"]:
        text += f"Take {f['course']} in remaining semester number {f['semester']}. "
    return text + "Give a feasible plan satisfying every requirement, or identify that the request is impossible."

def build(root):
    courses, req = read_json(root / "data/courses.json"), read_json(root / "data/requirements.json")
    full = set(req["foundation"] + req["mathematics"] + ["CS1101S", "CP3200"])
    middle = full - {"CS2109S", "CS3230", "ST2334"}
    early = {"CS1101S", "CP3200", "CS1231S", "MA1521", "MA1522"}
    cases, answers = [], []
    def add(identifier, split, level, done, horizon, start=1, required=(), forbidden=(), fixed=(),
            expected="feasible", reason="Constructed feasible scenario"):
        spec = gold_spec(courses, req, done, horizon, start, required, forbidden, fixed)
        plan = solve(spec, courses, req["corequisite_pairs"], time_limit=15)
        if plan["status"] != expected:
            raise RuntimeError(f"{identifier}: expected {expected}, obtained {plan['status']}: {plan}")
        checked = check(plan, spec, courses, req["corequisite_pairs"]) if expected == "feasible" else None
        if checked is not None and not checked["valid"]:
            raise RuntimeError(f"Reference checker rejected {identifier}: {checked}")
        case = {"id": identifier, "split": split, "difficulty": level,
                "request": request(spec), "tags": [level, reason]}
        cases.append(case)
        answers.append({"id": identifier, "status": expected, "spec": spec,
                        "reference_plan": plan, "label_rationale": reason,
                        "label_review": "Solver verified; feasible plans independently checked. Team source review pending."})
        print(f"{identifier}: {expected}", flush=True)

    # Development fixtures are not scored in the held-out summary.
    add("dev-easy-01", "dev", "easy", full | {"CS3263"}, 2, required=["CS4246"])
    add("dev-easy-02", "dev", "easy", full, 2, start=2, fixed=[("CS3268", 1)],
        expected="infeasible", reason="CS3268 is not offered in Semester 2")
    add("dev-medium-01", "dev", "medium", middle | {"ST2334"}, 4, required=["CS4262"])
    add("dev-medium-02", "dev", "medium", middle, 3, required=["CS3244"],
        expected="infeasible", reason="Mandatory CS2109S conflicts with CS3244")
    add("dev-hard-01", "dev", "hard", early | {"CS2030S"}, 5, required=["CS4278"])
    add("dev-hard-02", "dev", "hard", early, 2, fixed=[("CS2103T", 1)],
        expected="infeasible", reason="CS2103T prerequisites cannot be completed before the first semester")

    configurations = [
        ("easy", full, [(2,1,[],[],[]), (2,2,["CS3263"],[],[]),
         (3,1,["CS3264"],[],[]), (3,2,["CS4246"],[],[]),
         (2,1,[],["CS5242","CS5228"],[]), (3,1,[],[],[("CS3263",1),("CS4246",2)])]),
        ("medium", middle, [(3,1,[],[],[]), (4,2,["CS4262"],[],[]),
         (3,1,["CS3268"],[],[]), (4,1,["CS4278"],[],[]),
         (3,2,["CS4243"],["CS5242"],[]), (4,1,[],[],[("ST2334",1),("CS3263",2),("CS4246",3)])]),
        ("hard", early, [(4,1,[],[],[]), (5,2,["CS4246"],[],[]),
         (5,1,["CS4262"],[],[]), (6,2,["CS4278"],[],[]),
         (4,1,["CS4248"],["CS5228","CS5242"],[]),
         (5,1,[],[],[("CS2040S",1),("CS2109S",2),("CS3263",3),("CS4246",4)])])
    ]
    for level, done, variants in configurations:
        for index, (h, s, wanted, avoid, fixed) in enumerate(variants, 1):
            add(f"test-{level}-{index:02d}", "test", level, done, h, s, wanted, avoid, fixed)
    add("test-easy-07", "test", "easy", full, 2, start=2, fixed=[("CS3268",1)],
        expected="infeasible", reason="Fixed course violates its Semester 1-only offering")
    add("test-easy-08", "test", "easy", full, 2, fixed=[("CS3263",1),("CS4246",1)],
        expected="infeasible", reason="CS3263 must precede CS4246")
    add("test-medium-07", "test", "medium", middle, 3, required=["CS3243"],
        expected="infeasible", reason="Mandatory CS2109S precludes CS3243")
    primary_to_forbid = (set(req["ai_primaries"]) & courses.keys()) - middle
    add("test-medium-08", "test", "medium", middle, 4, forbidden=primary_to_forbid,
        expected="infeasible", reason="Required CS2109S and focus-area courses are forbidden")
    add("test-hard-07", "test", "hard", early, 1,
        expected="infeasible", reason="One semester cannot fit the missing Programme units under the 32-unit cap")
    add("test-hard-08", "test", "hard", early, 4, fixed=[("CS2109S",1)],
        expected="infeasible", reason="CS2040S must be completed before CS2109S")
    folder = root / "data/benchmark"
    for split in ("dev", "test"):
        jsonl(folder / f"{split}.jsonl", [c for c in cases if c["split"] == split])
    jsonl(folder / "gold.jsonl", answers)
    write_json(folder / "manifest.json", {
        "development_cases": 6, "evaluation_cases": 24, "evaluation_infeasible": 6,
        "construction": "Deterministic synthetic profiles and controlled restrictions over real course data.",
        "limitations": ["Difficulty categories are designed, not empirically calibrated.",
                       "Cases are related controlled variants, not independent samples of the NUS student population.",
                       "Some development and test cases share failure mechanisms; do not claim template-disjoint generalisation.",
                       "Benchmark labels are implementation-verified, not yet independently reviewed by the student team."],
        "catalogue_sha256": hashlib.sha256((root / "data/courses.json").read_bytes()).hexdigest(),
        "requirements_sha256": hashlib.sha256((root / "data/requirements.json").read_bytes()).hexdigest()
    })
    return cases
