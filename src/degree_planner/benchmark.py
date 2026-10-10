"""Proposal sub-problems 1-3: controlled, labelled natural-language instances."""
from __future__ import annotations
import json
from .policy import MAX_UNITS

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
            "max_units": MAX_UNITS, "required": sorted(set(req["foundation"] + req["mathematics"]) | set(required)),
            "forbidden": sorted(forbidden),
            "fixed": [{"course": c, "semester": t} for c, t in fixed], "groups": groups}

def request(spec):
    text = (f"I am a standard single-degree NUS Computer Science student under the AY2026/27 "
            f"admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining "
            f"Programme Requirements only. I have passed {', '.join(spec['completed'])}. "
            f"CP3200 is already completed and contributes 6 industry-experience units. "
            f"I have {len(spec['semesters'])} remaining normal semesters, starting with "
            f"Semester {spec['semesters'][0]}; Semester 1 and Semester 2 alternate. "
            f"The maximum is {spec['max_units']} units per semester with no minimum. "
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
    raise ValueError("Benchmark generation is deferred. Historical 32-unit cases are preserved; use the two 16-unit examples for local validation.")
