"""Proposal sub-problems 1-3: fixed contracts, not model-generated executable code."""
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator

def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties),
            "additionalProperties": False}

CODES = {"type": "array", "items": {"type": "string"}}
BOUND = {"type": ["integer", "null"], "minimum": 0}
GROUP = obj({"name": {"type": "string"}, "courses": CODES,
             "min_units": BOUND, "max_units": BOUND,
             "min_courses": BOUND, "max_courses": BOUND})
FIXED = obj({"course": {"type": "string"}, "semester": {"type": "integer", "minimum": 1}})
SPEC_SCHEMA = obj({
    "completed": CODES,
    "semesters": {"type": "array", "minItems": 1, "maxItems": 12,
                  "items": {"type": "integer", "enum": [1, 2]}},
    "max_units": {"type": "integer", "minimum": 0, "maximum": 64},
    "required": CODES, "forbidden": CODES,
    "fixed": {"type": "array", "items": FIXED},
    "groups": {"type": "array", "items": GROUP}
})
PLAN_SCHEMA = obj({
    "status": {"type": "string", "enum": ["feasible", "infeasible", "unknown"]},
    "semesters": {"type": "array", "items": CODES},
    "explanation": {"type": "string"}
})

def validate(value, schema):
    Draft202012Validator(schema).validate(value)

def validate_spec(spec, courses):
    validate(spec, SPEC_SCHEMA)
    refs = set(spec["completed"] + spec["required"] + spec["forbidden"])
    refs.update(f["course"] for f in spec["fixed"])
    for group in spec["groups"]:
        if len(group["courses"]) != len(set(group["courses"])):
            raise ValueError("Duplicate group membership")
        refs.update(group["courses"])
        for lo, hi in [("min_units", "max_units"), ("min_courses", "max_courses")]:
            if group[lo] is not None and group[hi] is not None and group[lo] > group[hi]:
                raise ValueError("Contradictory group bounds")
    if refs - courses.keys():
        raise ValueError(f"Unknown course codes: {sorted(refs - courses.keys())}")
    if len(spec["completed"]) != len(set(spec["completed"])):
        raise ValueError("Duplicate completed course")
    if len({g["name"] for g in spec["groups"]}) != len(spec["groups"]):
        raise ValueError("Duplicate group name")
    if any(f["semester"] > len(spec["semesters"]) for f in spec["fixed"]):
        raise ValueError("Fixed semester outside horizon")

def write_schemas(root: Path):
    folder = root / "prompts"
    folder.mkdir(exist_ok=True)
    for name, schema in [("plan.schema.json", PLAN_SCHEMA), ("spec.schema.json", SPEC_SCHEMA)]:
        (folder / name).write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
