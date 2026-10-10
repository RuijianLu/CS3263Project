"""Proposal sub-problems 1-3: independent arithmetic/set-based plan checking."""
from __future__ import annotations
from .schemas import PLAN_SCHEMA, validate

def satisfied(tree, completed):
    if tree is None or tree is True:
        return True
    if tree is False:
        return False
    if isinstance(tree, str):
        return tree in completed
    if "and" in tree:
        return all(satisfied(t, completed) for t in tree["and"])
    if "or" in tree:
        return any(satisfied(t, completed) for t in tree["or"])
    count, children = tree["nOf"]
    return sum(satisfied(t, completed) for t in children) >= count

def check(plan, spec, courses, corequisite_pairs=()):
    errors = []
    def error(kind, message):
        errors.append({"type": kind, "message": message})
    try:
        validate(plan, PLAN_SCHEMA)
    except Exception as exc:
        return {"valid": False, "violations": [{"type": "format", "message": str(exc)}]}
    if plan["status"] != "feasible":
        return {"valid": False, "violations": [{"type": "no_plan", "message": plan["status"]}]}
    if len(plan["semesters"]) != len(spec["semesters"]):
        error("horizon", "Must supply exactly one course list per remaining semester")
    taken = set(spec["completed"])
    newly_taken, placement = set(), {}
    for t, semester_courses in enumerate(plan["semesters"]):
        this = set(semester_courses)
        if len(this) != len(semester_courses):
            error("duplicate", f"Duplicate enrollment in semester {t + 1}")
        known = this & courses.keys()
        for code in this - courses.keys():
            error("unknown_course", code)
        if sum(courses[c]["units"] for c in known) > spec["max_units"] + 1e-8:
            error("workload", f"Semester {t + 1} exceeds {spec['max_units']} units")
        for code in known:
            course = courses[code]
            placement[code] = t + 1
            if code in taken:
                error("duplicate", f"{code} was already completed")
            if code in spec["forbidden"]:
                error("forbidden", code)
            if not course["selectable"]:
                error("eligibility", f"{code} is blocked pending review or excluded from new selection")
            if t >= len(spec["semesters"]) or spec["semesters"][t] not in course["offered_semesters"]:
                error("availability", f"{code} not offered in semester {t + 1}")
            if not satisfied(course["prerequisites"], taken):
                error("prerequisite", f"{code} prerequisites not completed before semester {t + 1}")
            for other in course["corequisites"]:
                if other not in taken | this:
                    error("corequisite", f"{code} needs {other} before or concurrently")
        newly_taken |= known
        taken |= known
    for a, b in corequisite_pairs:
        if (a in placement or b in placement) and placement.get(a) != placement.get(b):
            error("corequisite", f"{a} and {b} must be taken in the same semester")
    for code in newly_taken:
        for other in courses[code]["preclusions"]:
            if other in taken and other != code:
                error("preclusion", f"{code} conflicts with {other}")
    for code in taken - newly_taken:
        for other in courses[code]["preclusions"]:
            if other in newly_taken:
                error("preclusion", f"{other} conflicts with completed {code}")
    for code in set(spec["required"]) - taken:
        error("required", f"Missing {code}")
    for fixed in spec["fixed"]:
        if placement.get(fixed["course"]) != fixed["semester"]:
            error("fixed_semester", f"{fixed['course']} must be in semester {fixed['semester']}")
    for group in spec["groups"]:
        members = taken & set(group["courses"])
        totals = {"courses": len(members), "units": sum(courses[c]["units"] for c in members)}
        for kind, total in totals.items():
            lo, hi = group[f"min_{kind}"], group[f"max_{kind}"]
            if lo is not None and total + 1e-8 < lo:
                error("requirement", f"{group['name']}: {total:g} {kind}, needs at least {lo}")
            if hi is not None and total - 1e-8 > hi:
                error("requirement", f"{group['name']}: {total:g} {kind}, permits at most {hi}")
    return {"valid": not errors, "violations": errors}

def translation_differences(actual, gold):
    """Field-level audit; named group membership ignores ordering, not semantics."""
    differences = []
    for key in ["completed", "required", "forbidden"]:
        if set(actual[key]) != set(gold[key]):
            differences.append(key)
    for key in ["semesters", "max_units"]:
        if actual[key] != gold[key]:
            differences.append(key)
    if {(f["course"], f["semester"]) for f in actual["fixed"]} != {(f["course"], f["semester"]) for f in gold["fixed"]}:
        differences.append("fixed")
    def groups(spec):
        return {g["name"]: (frozenset(g["courses"]), g["min_units"], g["max_units"],
                            g["min_courses"], g["max_courses"]) for g in spec["groups"]}
    a, b = groups(actual), groups(gold)
    for name in sorted(a.keys() | b.keys()):
        if a.get(name) != b.get(name):
            differences.append(f"group:{name}")
    return differences
