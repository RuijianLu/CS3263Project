"""Proposal sub-problems 1-3: controlled, labelled natural-language instances."""
from __future__ import annotations
import copy
import csv
import hashlib
import json
import random
from collections import Counter
from .collect import read_json, write_json
from .checker import check
from .histories import HISTORY_COUNTS, history_pool, partition_histories, validate_history
from .policy import MAX_UNITS
from .solver import solve

VERSION = "csp16-stage-v1"
LEVELS = ("easy", "medium", "hard")
HORIZONS = (7, 6, 5, 4)
GENERATOR_PATHS = ("data/courses.json", "data/requirements.json",
                   "src/degree_planner/benchmark.py", "src/degree_planner/histories.py",
                   "src/degree_planner/csp.py", "src/degree_planner/solver.py",
                   "src/degree_planner/checker.py", "src/degree_planner/schemas.py",
                   "src/degree_planner/policy.py")

def jsonl(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in values), encoding="utf-8")

def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def group(name, codes, min_units=None, max_units=None, min_courses=None, max_courses=None):
    return dict(name=name, courses=sorted(codes), min_units=min_units, max_units=max_units,
                min_courses=min_courses, max_courses=max_courses)

def gold_spec(courses, req, completed, horizon=7, start=2, required=(), forbidden=(), fixed=()):
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
            "max_units": MAX_UNITS, "required": sorted(set(req["foundation"] + req["mathematics"]) | set(required)),
            "forbidden": sorted(forbidden),
            "fixed": [{"course": c, "semester": t} for c, t in fixed], "groups": groups}

def request(spec):
    text = (f"I am a standard single-degree NUS Computer Science student under the AY2026/27 "
            f"admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining "
            f"Programme Requirements only. I have passed {', '.join(spec['completed']) or 'no courses'}. "
            f"I have {len(spec['semesters'])} remaining normal semesters, starting with "
            f"Semester {spec['semesters'][0]}; Semester 1 and Semester 2 alternate. "
            f"The maximum is {spec['max_units']} units per semester with no minimum. "
            f"Use the supplied snapshot's recurring offerings. All qualifying mathematics and English "
            f"admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. ")
    core = {"CS1231S","CS2030S","CS2040S","CS2100","CS2101","CS2103T","CS2106","CS2109S","CS3230",
            "MA1521","MA1522","ST2334"}
    if "CP3200" in spec["completed"]:
        text += "For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. "
    extra = set(spec["required"]) - core
    if extra: text += f"My plan must include {', '.join(sorted(extra))}. "
    if spec["forbidden"]: text += f"Do not newly enroll in {', '.join(spec['forbidden'])}. "
    for f in spec["fixed"]:
        text += f"Take {f['course']} in remaining semester number {f['semester']}. "
    return text + "Give a feasible plan satisfying every requirement, or identify that the request is impossible."

def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_hashes(root):
    return {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in GENERATOR_PATHS}


def checked_solution(spec, courses, req):
    plan = solve(spec, courses, req["corequisite_pairs"])
    if plan["status"] == "unknown":
        plan = solve(spec, courses, req["corequisite_pairs"], time_limit=30)
    checked = check(plan, spec, courses, req["corequisite_pairs"])
    if plan["status"] != "feasible" or not checked["valid"]:
        return None
    return plan, checked


def elective_pool(courses, req):
    mandatory = set(req["foundation"] + req["mathematics"] + ["CS1101S"])
    return sorted(c for c, v in courses.items() if v["category"] == "breadth" and v["selectable"]
                  and not any(other in mandatory for other in v["preclusions"])
                  and not any(c in courses[other]["preclusions"] for other in mandatory))


def feasible_case(history, difficulty, courses, req, rng):
    horizon = history["remaining_semesters"]
    choices = elective_pool(courses, req)
    count = {"easy": 1, "medium": 3, "hard": 6}[difficulty]
    extras = rng.sample(choices, count)
    spec = gold_spec(courses, req, history["completed"], horizon,
                     start=1 + history["past_semesters"] % 2, required=["CS1101S", *extras])
    result = checked_solution(spec, courses, req)
    if result is None:
        return None
    plan, _ = result
    if difficulty != "easy":
        placements = [(c, t) for t, semester in enumerate(plan["semesters"], 1)
                      for c in semester if c in spec["required"] and c not in spec["completed"]]
        fixed_count = {"medium": 2, "hard": 5}[difficulty]
        spec["fixed"] = [dict(course=c, semester=t) for c, t in rng.sample(placements, min(fixed_count, len(placements)))]
        selected = {c for semester in plan["semesters"] for c in semester}
        unused = sorted(set(choices) - selected)
        forbidden_count = {"medium": 2, "hard": 4}[difficulty]
        if len(unused) < forbidden_count:
            return None
        spec["forbidden"] = sorted(rng.sample(unused, forbidden_count))
        spec["fixed"].sort(key=lambda f: (f["semester"], f["course"]))
        result = checked_solution(spec, courses, req)
        if result is None:
            return None
        plan, checked = result
    else:
        checked = result[1]
    return spec, plan, checked


def contradiction(base, plan, kind, courses, req, rng):
    """Each negative is derived from a checked feasible request and carries a witness."""
    spec = copy.deepcopy(base)
    witness = {"kind": kind}
    pending = sorted(set(spec["required"]) - set(spec["completed"]))
    if kind == "required_forbidden":
        code = rng.choice(pending)
        spec["forbidden"] = sorted(set(spec["forbidden"]) | {code})
        witness.update(courses=[code], reason=f"{code} is not completed, is required, and is forbidden from new enrolment.")
    elif kind == "unavailable_offering":
        code = rng.choice(["CS4277", "CS4278", "CS3268", "CS4261", "CS4263"])
        position = rng.choice([t for t, season in enumerate(spec["semesters"], 1)
                               if season not in courses[code]["offered_semesters"]])
        spec["required"] = sorted(set(spec["required"]) | {code})
        spec["fixed"] = [f for f in spec["fixed"] if f["course"] != code] + [dict(course=code, semester=position)]
        witness.update(courses=[code], position=position,
                       reason=f"{code} is fixed to normal Semester {spec['semesters'][position - 1]}, but is offered only in {courses[code]['offered_semesters']}.")
    elif kind == "prerequisite_first":
        spec["required"] = sorted(set(spec["required"]) | {"CS4246"})
        spec["fixed"] = [f for f in spec["fixed"] if f["course"] != "CS4246"] + [dict(course="CS4246", semester=1)]
        witness.update(courses=["CS4246", "CS3243", "CS3263"], position=1,
                       reason="CS4246 requires CS3243 or CS3263 in an earlier semester. Neither is completed, so position 1 is impossible.")
    elif kind == "preclusion":
        spec["required"] = sorted(set(spec["required"]) | {"CS3243"})
        witness.update(courses=["CS2109S", "CS3243"],
                       reason="CS2109S is mandatory and precludes CS3243. CS3243 is also required and is not completed.")
    elif kind == "corequisite_split":
        if "CS2103T" in spec["completed"]:
            return None
        placements = {c: t for t, semester in enumerate(plan["semesters"], 1) for c in semester}
        first = placements["CS2103T"]
        second = rng.choice([t for t in range(1, len(spec["semesters"]) + 1) if t != first])
        spec["fixed"] = [f for f in spec["fixed"] if f["course"] not in {"CS2101", "CS2103T"}]
        spec["fixed"] += [dict(course="CS2103T", semester=first), dict(course="CS2101", semester=second)]
        witness.update(courses=["CS2101", "CS2103T"], positions=[second, first],
                       reason=f"CS2101 and CS2103T must be newly enrolled together, but are fixed to positions {second} and {first}.")
    elif kind == "prerequisite_order":
        position = rng.randint(2, len(spec["semesters"]))
        spec["required"] = sorted(set(spec["required"]) | {"CS3263", "CS4246"})
        spec["forbidden"] = sorted(set(spec["forbidden"]) - {"CS3263", "CS4246"})
        spec["fixed"] = [f for f in spec["fixed"] if f["course"] not in {"CS3263", "CS4246"}]
        spec["fixed"] += [dict(course="CS3263", semester=position), dict(course="CS4246", semester=position)]
        witness.update(courses=["CS3263", "CS4246", "CS3243", "CS2109S"], position=position,
                       reason="CS4246 needs earlier CS3263 or CS3243. CS3263 is fixed concurrently, while CS3243 is excluded by mandatory CS2109S; neither alternative is completed.")
    elif kind == "corequisite_overload":
        if "CS2103T" in spec["completed"]:
            return None
        placements = {c: t for t, semester in enumerate(plan["semesters"], 1) for c in semester}
        position = placements["CS2103T"]
        others = [c for semester in plan["semesters"] for c in semester
                  if c not in {"CS2101", "CS2103T"} and courses[c]["units"] == 4
                  and spec["semesters"][position - 1] in courses[c]["offered_semesters"]]
        if len(others) < 3:
            return None
        selected = rng.sample(sorted(others), 3)
        fixed_codes = set(selected) | {"CS2103T"}
        spec["fixed"] = [f for f in spec["fixed"] if f["course"] not in fixed_codes | {"CS2101"}
                         and f["semester"] != position]
        spec["fixed"] += [dict(course=c, semester=position) for c in sorted(fixed_codes)]
        witness.update(courses=sorted(fixed_codes | {"CS2101"}), position=position,
                       reason=f"The four explicit enrolments at position {position} use 16 units. Concurrent CS2101 is additionally forced by CS2103T, raising the necessary load to 20 > 16 units.")
    elif kind == "lower_level_coverage":
        lower = [c for c, v in courses.items() if v["category"] == "breadth" and v["level"] <= 4000]
        allowed = rng.sample([c for c in lower if c.startswith("CS42") and c in req["ai_primaries"]], 2)
        spec["forbidden"] = sorted(set(spec["forbidden"]) | (set(lower) - set(allowed)))
        spec["required"] = sorted(set(spec["required"]) - set(spec["forbidden"]))
        spec["fixed"] = [f for f in spec["fixed"] if f["course"] not in spec["forbidden"]]
        group = next(g for g in spec["groups"] if g["name"] == "programme_lower")
        available = set(group["courses"]) - set(spec["forbidden"])
        maximum = sum(courses[c]["units"] for c in available)
        if maximum >= group["min_units"]:
            return None
        witness.update(courses=sorted(available), maximum_units=maximum, minimum_units=group["min_units"],
                       reason=f"Available members of programme_lower provide at most {maximum:g} units, below its {group['min_units']}-unit minimum. Level-5000 electives cannot close this lower-level deficit.")
    elif kind == "alternative_exhaustion":
        spec["required"] = sorted(set(spec["required"]) | {"CS4246"})
        spec["forbidden"] = sorted((set(spec["forbidden"]) | {"CS3243", "CS3263"}) - {"CS4246"})
        spec["required"] = sorted(set(spec["required"]) - {"CS3243", "CS3263"})
        spec["fixed"] = [f for f in spec["fixed"] if f["course"] not in {"CS3243", "CS3263"}]
        witness.update(courses=["CS4246", "CS3243", "CS3263"],
                       reason="Required CS4246 needs earlier CS3243 or CS3263. Both alternatives are forbidden and neither is completed.")
    else:
        raise ValueError(f"Unknown contradiction: {kind}")
    spec["fixed"].sort(key=lambda f: (f["semester"], f["course"]))
    negative = solve(spec, courses, req["corequisite_pairs"])
    if negative["status"] == "unknown":
        negative = solve(spec, courses, req["corequisite_pairs"], time_limit=30)
    if negative["status"] != "infeasible":
        return None
    return spec, negative, witness


NEGATIVE_KINDS = {
    "easy": ("required_forbidden", "unavailable_offering", "prerequisite_first"),
    "medium": ("preclusion", "corequisite_split", "prerequisite_order"),
    "hard": ("corequisite_overload", "lower_level_coverage", "alternative_exhaustion"),
}


def case_metrics(spec, history, plan, courses):
    completed = set(spec["completed"])
    pending = sorted(set(spec["required"]) - completed)
    breadth = next(g for g in spec["groups"] if g["name"] == "breadth")
    earned = sum(courses[c]["units"] for c in completed.intersection(breadth["courses"]))
    mandatory_units = sum(courses[c]["units"] for c in pending)
    pending_breadth_units = sum(courses[c]["units"] for c in set(pending).intersection(breadth["courses"]))
    lower_bound = mandatory_units + max(0, breadth["min_units"] - earned - pending_breadth_units)
    return dict(remaining_semesters=len(spec["semesters"]), completed_academic_courses=history["academic_course_count"],
                completed_academic_units=history["academic_units"], required_new_courses=len(pending),
                required_new_units=mandatory_units, new_workload_lower_bound_units=lower_bound,
                horizon_capacity_units=len(spec["semesters"]) * MAX_UNITS,
                fixed_enrolments=len(spec["fixed"]), forbidden_courses=len(spec["forbidden"]),
                restricted_offering_required=sum(len(courses[c]["offered_semesters"]) == 1 for c in pending),
                reference_new_courses=sum(map(len, plan["semesters"])),
                reference_new_units=sum(courses[c]["units"] for semester in plan["semesters"] for c in semester))


def verify_witness(spec, witness, courses, req):
    """Check the stated contradiction arithmetically, separately from the solver proof."""
    done, required, forbidden = map(set, (spec["completed"], spec["required"], spec["forbidden"]))
    fixed = {f["course"]: f["semester"] for f in spec["fixed"]}
    kind, codes = witness["kind"], witness["courses"]
    if kind == "required_forbidden":
        valid = codes[0] in (required & forbidden) - done
    elif kind == "unavailable_offering":
        code = codes[0]
        valid = fixed.get(code) == witness["position"] and spec["semesters"][witness["position"] - 1] not in courses[code]["offered_semesters"]
    elif kind == "prerequisite_first":
        valid = fixed.get("CS4246") == 1 and not done.intersection({"CS3243", "CS3263"})
    elif kind == "preclusion":
        valid = {"CS2109S", "CS3243"} <= (done | required) and "CS3243" not in done and "CS3243" in courses["CS2109S"]["preclusions"]
    elif kind == "corequisite_split":
        valid = ["CS2101", "CS2103T"] in req["corequisite_pairs"] and not done.intersection(codes) and fixed.get(codes[0]) != fixed.get(codes[1]) and all(c in fixed for c in codes)
    elif kind == "prerequisite_order":
        valid = (fixed.get("CS3263") == fixed.get("CS4246") == witness["position"]
                 and not done.intersection({"CS3263", "CS3243"})
                 and "CS2109S" in required and "CS3243" in courses["CS2109S"]["preclusions"])
    elif kind == "corequisite_overload":
        explicit = {c for c, t in fixed.items() if t == witness["position"]}
        forced = explicit | {"CS2101"}
        valid = ("CS2103T" in explicit and ["CS2101", "CS2103T"] in req["corequisite_pairs"]
                 and not done.intersection(forced)
                 and sum(courses[c]["units"] for c in explicit) <= MAX_UNITS
                 and sum(courses[c]["units"] for c in forced) > MAX_UNITS)
    elif kind == "lower_level_coverage":
        group = next(g for g in spec["groups"] if g["name"] == "programme_lower")
        available = set(group["courses"]) - (forbidden - done)
        maximum = sum(courses[c]["units"] for c in available)
        valid = maximum == witness["maximum_units"] and maximum < group["min_units"]
    elif kind == "alternative_exhaustion":
        valid = "CS4246" in required - done and {"CS3243", "CS3263"} <= forbidden and not done.intersection({"CS3243", "CS3263"})
    else:
        valid = False
    if kind in {"prerequisite_first", "prerequisite_order", "alternative_exhaustion"}:
        valid &= {"or": ["CS3243", "CS3263"]} in courses["CS4246"]["prerequisites"].get("and", [])
    if not valid:
        raise ValueError(f"Contradiction witness does not follow from the specification: {kind}")


def generate(courses, req, seed=3263, progress=None):
    rng = random.Random(seed)
    histories = {}
    for horizon in HORIZONS:
        histories[horizon] = partition_histories(history_pool(courses, req, horizon, rng), rng)
    cases, answers, used = {"dev": [], "test": []}, [], set()
    for split, pool_index in (("dev", 0), ("test", 1)):
        for horizon in HORIZONS:
            for difficulty in LEVELS:
                labels = ["feasible", "infeasible"] if split == "dev" else ["feasible"] * 7 + ["infeasible"] * 3
                pool = histories[horizon][pool_index]
                for index, label in enumerate(labels, 1):
                    kind = NEGATIVE_KINDS[difficulty][(index - (1 if split == "dev" else 7) - 1) % 3]
                    candidates = [h for h in pool if kind not in {"corequisite_split", "corequisite_overload"}
                                  or "CS2103T" not in h["completed"]] if label == "infeasible" else pool
                    if not candidates:
                        raise ValueError(f"No suitable {split} history for {kind}")
                    for attempt in range(150):
                        history = copy.deepcopy(rng.choice(candidates))
                        positive = feasible_case(history, difficulty, courses, req, rng)
                        if positive is None:
                            continue
                        spec, plan, checked = positive
                        repair = None
                        witness = None
                        if label == "infeasible":
                            negative = contradiction(spec, plan, kind, courses, req, rng)
                            if negative is None:
                                continue
                            repair = dict(spec=copy.deepcopy(spec), reference_plan=plan,
                                          validation=checked, reason="Restore the checked feasible precursor request.")
                            spec, plan, witness = negative
                        digest = canonical_hash(spec)
                        if digest not in used:
                            break
                    else:
                        raise ValueError(f"Could not construct a unique validated case: {split}/{horizon}/{difficulty}/{label}")
                    used.add(digest)
                    identifier = f"{split}-h{horizon}-{difficulty}-{index:02d}"
                    case = dict(id=identifier, difficulty=difficulty, request=request(spec),
                                remaining_semesters=horizon, history_id=history["id"],
                                metrics=case_metrics(spec, history, plan, courses))
                    answer = dict(id=identifier, status=label, spec=spec, reference_plan=plan,
                                  history=history, spec_sha256=digest,
                                  validation=checked if label == "feasible" else None,
                                  infeasibility_witness=witness, feasible_precursor=repair,
                                  label_rationale="Independent schedule checks passed." if label == "feasible" else witness["reason"],
                                  label_review="Locally validated against frozen facts; source interpretations remain subject to review.")
                    cases[split].append(case)
                    answers.append(answer)
                if progress:
                    progress(f"{split}: horizon {horizon}, {difficulty}: {len(labels)} labelled cases validated")
    by_id = {a["id"]: a for a in answers}
    def development_order(case):
        cell = HORIZONS.index(case["remaining_semesters"]) * len(LEVELS) + LEVELS.index(case["difficulty"])
        first_label = "feasible" if cell % 2 == 0 else "infeasible"
        return (by_id[case["id"]]["status"] != first_label, cell)
    cases["dev"].sort(key=development_order)
    return cases, answers


def audit(cases, answers, courses, req):
    by_id = {a["id"]: a for a in answers}
    if len(by_id) != len(answers):
        raise ValueError("Duplicate gold identifiers")
    all_cases = cases["dev"] + cases["test"]
    if {c["id"] for c in all_cases} != set(by_id) or len(all_cases) != len(answers):
        raise ValueError("Case/gold membership mismatch")
    digests, completed_sets = set(), {"dev": set(), "test": set()}
    for split, values in cases.items():
        counts = Counter((c["remaining_semesters"], c["difficulty"], by_id[c["id"]]["status"]) for c in values)
        for horizon in HORIZONS:
            for difficulty in LEVELS:
                expected = (1, 1) if split == "dev" else (7, 3)
                if tuple(counts[horizon, difficulty, label] for label in ("feasible", "infeasible")) != expected:
                    raise ValueError("Unexpected horizon/difficulty/label distribution")
        for case in values:
            answer = by_id[case["id"]]
            spec, history = answer["spec"], answer["history"]
            validate_history(history, courses, req["corequisite_pairs"])
            horizon = case["remaining_semesters"]
            if spec["completed"] != history["completed"] or len(spec["semesters"]) != horizon:
                raise ValueError("History and remaining request disagree")
            if spec["semesters"] != [1 + ((8 - horizon + t) % 2) for t in range(horizon)] or spec["max_units"] != MAX_UNITS:
                raise ValueError("Study stage or workload policy mismatch")
            lo, hi = HISTORY_COUNTS[horizon]
            if not lo <= history["academic_course_count"] <= hi:
                raise ValueError("Implausible completed-course count for the stage")
            if request(spec) != case["request"]:
                raise ValueError("Natural-language request and specification disagree")
            if not set(req["foundation"] + req["mathematics"] + ["CS1101S"]) <= set(spec["required"]):
                raise ValueError("Mandatory courses silently omitted")
            digest = canonical_hash(spec)
            if digest in digests or digest != answer["spec_sha256"]:
                raise ValueError("Duplicate or altered specification")
            digests.add(digest)
            completed_sets[split].add(tuple(spec["completed"]))
            if answer["status"] == "feasible":
                checked = check(answer["reference_plan"], spec, courses, req["corequisite_pairs"])
                if not checked["valid"]:
                    raise ValueError(f"Invalid reference schedule: {case['id']}")
            else:
                if case["difficulty"] == "hard" and (set(spec["required"]) - set(spec["completed"])) & set(spec["forbidden"]):
                    raise ValueError("A hard negative has an unintended direct required/forbidden conflict")
                verify_witness(spec, answer["infeasibility_witness"], courses, req)
                if not answer["infeasibility_witness"] or solve(spec, courses, req["corequisite_pairs"])["status"] != "infeasible":
                    raise ValueError("Infeasible label lacks a confirmed proof")
                repair = answer["feasible_precursor"]
                if not check(repair["reference_plan"], repair["spec"], courses, req["corequisite_pairs"])["valid"]:
                    raise ValueError("Negative case has no valid feasible precursor")
    if completed_sets["dev"] & completed_sets["test"]:
        raise ValueError("A completed-course history leaks between splits")
    return dict(valid=True, cases=len(all_cases), feasible=sum(a["status"] == "feasible" for a in answers),
                infeasible=sum(a["status"] == "infeasible" for a in answers),
                unique_specifications=len(digests),
                distinct_histories={s: len(v) for s, v in completed_sets.items()},
                history_split_overlap=0, model_calls=0)


def case_report(case, answer, courses):
    from .inspection import render_report
    history = answer["history"]
    lines = [f"# {case['id']}", "", f"Designed difficulty: {case['difficulty']}; label: {answer['status']}.", "",
             "## Natural-language request", "", case["request"], "",
             "## Checked academic history", "", "CP3200 is a separate credited internship exception.", "",
             "| Past position | Normal semester | Units | Courses |", "|---:|---:|---:|---|"]
    for t, semester in enumerate(history["academic_semesters"], 1):
        lines.append(f"| {t} | {1 + (t - 1) % 2} | {sum(courses[c]['units'] for c in semester):g} | {', '.join(semester)} |")
    if answer["status"] == "feasible":
        lines += ["", render_report(answer["spec"], answer["reference_plan"], answer["validation"], courses)]
    else:
        lines += ["", "## Infeasibility", "", answer["label_rationale"], "",
                  "CP-SAT returned INFEASIBLE. The independent schedule checker does not certify infeasibility.",
                  "gold.jsonl also stores a checked feasible precursor; restoring its request removes the introduced conflict.",
                  "", "## Changes from the checked feasible precursor", "",
                  "| Field | Feasible precursor | Infeasible request |", "|---|---|---|"]
        precursor = answer["feasible_precursor"]["spec"]
        for key in ("required", "forbidden", "fixed"):
            if precursor[key] != answer["spec"][key]:
                lines.append(f"| {key} | {json.dumps(precursor[key])} | {json.dumps(answer['spec'][key])} |")
    return "\n".join(lines) + "\n"


def write_review(root, cases, answers, validation):
    courses = read_json(root / "data/courses.json")
    folder = root / "data/benchmark"
    by_id = {a["id"]: a for a in answers}
    fields = ["id", "split", "horizon", "difficulty", "status", "history_id", "completed_academic_courses",
              "required_new_courses", "new_workload_lower_bound_units", "fixed_enrolments", "forbidden_courses", "contradiction"]
    with (folder / "index.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for split, values in cases.items():
            for case in values:
                answer = by_id[case["id"]]
                write_json(folder / "cases" / f"{case['id']}.json", answer["spec"])
                review_path = folder / "review" / f"{case['id']}.md"
                review_path.parent.mkdir(parents=True, exist_ok=True)
                review_path.write_text(case_report(case, answer, courses), encoding="utf-8")
                row = {k: case["metrics"][k] for k in fields if k in case["metrics"]}
                row.update(id=case["id"], split=split, horizon=case["remaining_semesters"], difficulty=case["difficulty"],
                           status=answer["status"], history_id=case["history_id"],
                           contradiction=(answer["infeasibility_witness"] or {}).get("kind", ""))
                writer.writerow(row)
    lines = ["# 16-unit study-stage benchmark", "",
             "24 development cases and 120 evaluation cases. No language-model calls were made.", "",
             "Each of the 12 horizon/difficulty cells contains 1 feasible + 1 infeasible development case, and 7 feasible + 3 infeasible evaluation cases.",
             "Difficulty is designed, not empirically calibrated; compare levels within a horizon. Negative-case proof difficulty can differ from its surrounding request.", "",
             "## Study stages", "", "| Remaining | Past semesters | Completed academic course range |", "|---:|---:|---:|"]
    for h in HORIZONS:
        lines.append(f"| {h} | {8 - h} | {HISTORY_COUNTS[h][0]}-{HISTORY_COUNTS[h][1]} |")
    lines += ["", "## Construction and review", "",
              "Histories contain prerequisite-valid academic semester schedules with at most 16 units. Some early histories leave CS1101S outstanding, exercising the full introductory programming chain; later progress varies. CP3200 is credited separately under the retained internship simplification.",
              "Completed-course sets are disjoint between development and evaluation. Histories recur within a split to support controlled comparisons; cases are correlated synthetic instances, not independent student samples or template-disjoint tests.",
              "Easy feasible cases request one elective without fixed/forbidden additions; medium requests three electives plus two fixed positions and two forbidden alternatives; hard requests six electives plus five fixed positions and four forbidden alternatives. Prerequisites, offerings, course facts, programme bounds and the 16-unit cap stay fixed.",
              "Feasible references pass the independent checker. Every infeasible request is solver-proven and includes a concrete contradiction and a checked feasible precursor. Timeouts are not labelled infeasible.",
              "Reference schedules are any satisfying assignments, not minimal or optimal plans. Extra permissible courses can appear.", "",
              f"Validation: {validation['cases']} unique requests, {validation['feasible']} feasible and {validation['infeasible']} infeasible; zero overlapping completed-course sets between splits.",
              f"Distinct used histories: development {validation['distinct_histories']['dev']}, evaluation {validation['distinct_histories']['test']}.", "",
              "- index.csv: case counts, workload measures, history identifiers and contradiction mechanisms.",
              "- review/CASE_ID.md: request, checked past history and readable reference result.",
              "- cases/CASE_ID.json: specification usable with solve/check. Copy it before editing; these convenience exports do not change the scored JSONL requests or gold records.",
              "- gold.jsonl: labels, full reference plans/checks, histories and negative-case precursors. Keep it out of model prompts.",
              "- validation.json and manifest.json: local audit and frozen source/input hashes.", "",
              "To inspect a single case, run `python -m degree_planner solve data/benchmark/cases/CASE_ID.json`. Output goes to results/validation/CASE_ID. Infeasible cases have no validated schedule, so solve exits unsuccessfully while retaining its proof status and artifacts.", "",
              "The old 32-unit inputs and results remain under results/historical/32-unit-inputs and results/pilot, results/initial, results/runs. This benchmark has not yet been evaluated by a language model."]
    (folder / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(root, seed=3263):
    import sys
    import ortools
    courses, req = read_json(root / "data/courses.json"), read_json(root / "data/requirements.json")
    folder = root / "data/benchmark"
    if (folder / "gold.jsonl").exists():
        old = load_jsonl(folder / "gold.jsonl")
        if any(a["spec"]["max_units"] != MAX_UNITS for a in old):
            archive = root / "results/historical/32-unit-inputs/data/benchmark"
            for name in ("dev.jsonl", "test.jsonl", "gold.jsonl", "manifest.json"):
                if not (archive / name).exists() or (folder / name).read_bytes() != (archive / name).read_bytes():
                    raise ValueError("Preserve the exact historical benchmark before replacing active inputs")
    cases, answers = generate(courses, req, seed, progress=lambda message: print(message, flush=True))
    validation = audit(cases, answers, courses, req)
    folder.mkdir(parents=True, exist_ok=True)
    for split, values in cases.items():
        jsonl(folder / f"{split}.jsonl", values)
    jsonl(folder / "gold.jsonl", answers)
    write_json(folder / "validation.json", validation)
    write_review(root, cases, answers, validation)
    data_paths = ("dev.jsonl", "test.jsonl", "gold.jsonl", "index.csv", "validation.json")
    manifest = dict(version=VERSION, seed=seed, objective=None, max_units=MAX_UNITS,
                    runtime=dict(python=sys.version.split()[0], ortools=ortools.__version__),
                    development_cases=24, evaluation_cases=120, evaluation_feasible=84, evaluation_infeasible=36,
                    local_validation=validation, model_calls=0, source_sha256=source_hashes(root),
                    artifact_sha256={p: hashlib.sha256((folder / p).read_bytes()).hexdigest() for p in data_paths},
                    limitations=["Designed difficulty is not empirical model difficulty.",
                                 "Synthetic cases reuse histories within splits and share constraint mechanisms across splits.",
                                 "Academic completed-course sets are split-disjoint; this is not population representativeness.",
                                 "Separate CP3200 credit is an idealized internship exception.",
                                 "Source interpretations still require review; no model comparison has been run."])
    write_json(folder / "manifest.json", manifest)
    return validation
