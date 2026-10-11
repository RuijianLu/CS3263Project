"""Proposal sub-problems 1-3: independent arithmetic/set-based plan checking."""
from __future__ import annotations
from .schemas import PLAN_SCHEMA, validate, validate_spec


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
    """Check the original input independently of the CSP builder and solver."""
    errors, checks, semesters, groups = [], [], [], []

    def expect(kind, subject, passed, detail):
        record = {"type": kind, "subject": subject, "passed": bool(passed), "detail": detail}
        checks.append(record)
        if not passed:
            errors.append({"type": kind, "message": f"{subject}: {detail}"})
        return record

    def result():
        return {"valid": not errors, "violations": errors, "checks": checks,
                "semesters": semesters, "groups": groups}

    try:
        validate_spec(spec, courses)
        validate(plan, PLAN_SCHEMA)
    except Exception as exc:
        expect("format", "input", False, str(exc))
        return result()
    if plan["status"] != "feasible":
        expect("no_plan", "schedule", False,
               f"status={plan['status']}; the checker validates schedules, not infeasibility proofs")
        return result()
    expect("horizon", "schedule", len(plan["semesters"]) == len(spec["semesters"]),
           f"{len(plan['semesters'])} semester lists; expected {len(spec['semesters'])}")
    taken = set(spec["completed"])
    newly_taken, placement = set(), {}
    for t, semester_courses in enumerate(plan["semesters"]):
        this = set(semester_courses)
        subject = f"remaining semester {t + 1}"
        expect("duplicate", subject, len(this) == len(semester_courses), "No duplicate codes within this semester")
        known = this & courses.keys()
        for code in sorted(this - courses.keys()):
            expect("unknown_course", code, False, "Code is absent from the catalogue")
        units = sum(courses[c]["units"] for c in known)
        expect("workload", subject, units <= spec["max_units"] + 1e-8,
               f"{units:g} units <= {spec['max_units']} units")
        season = spec["semesters"][t] if t < len(spec["semesters"]) else None
        semesters.append({"position": t + 1, "normal_semester": season, "courses": sorted(this),
                          "units": units, "max_units": spec["max_units"]})
        for code in sorted(known):
            course = courses[code]
            placement[code] = t + 1
            expect("duplicate", code, code not in taken, "Not previously completed or scheduled")
            expect("forbidden", code, code not in spec["forbidden"], "New enrolment is permitted by the request")
            expect("eligibility", code, course["selectable"], "Selectable under the catalogue assumptions")
            expect("availability", code, season in course["offered_semesters"],
                   f"Normal Semester {season}; offered in {course['offered_semesters']}")
            evidence = expect("prerequisite", code, satisfied(course["prerequisites"], taken),
                              "Prerequisite expression satisfied using only completed and earlier-semester courses")
            evidence.update(prerequisites=course["prerequisites"], available_before=sorted(taken))
            for other in course["corequisites"]:
                expect("corequisite", code, other in taken | this, f"{other} completed before or concurrently")
        newly_taken |= known
        taken |= known

    for a, b in corequisite_pairs:
        if a in placement or b in placement:
            expect("corequisite", f"{a}/{b}", placement.get(a) == placement.get(b),
                   f"Same new-enrolment semester: {placement.get(a)} / {placement.get(b)}")
    conflicts = set()
    for code in courses:
        for other in courses[code]["preclusions"]:
            if other in courses and other != code and {code, other} & newly_taken:
                pair = tuple(sorted((code, other)))
                if pair not in conflicts:
                    expect("preclusion", "/".join(pair), not {code, other} <= taken,
                           "Cannot include both when at least one is newly enrolled")
                    conflicts.add(pair)
    for code in sorted(set(spec["required"])):
        expect("required", code, code in taken, "Present in completed record or new schedule")
    for fixed in spec["fixed"]:
        code, semester = fixed["course"], fixed["semester"]
        expect("fixed_semester", code, placement.get(code) == semester,
               f"Scheduled position {placement.get(code)}; required position {semester}")
    for group in spec["groups"]:
        members = taken & set(group["courses"])
        totals = {"courses": len(members), "units": sum(courses[c]["units"] for c in members)}
        bounds = {k: group[k] for k in ("min_units", "max_units", "min_courses", "max_courses")}
        group_passed = True
        for kind, total in totals.items():
            lo, hi = group[f"min_{kind}"], group[f"max_{kind}"]
            if lo is not None:
                passed = total + 1e-8 >= lo
                expect("requirement", group["name"], passed, f"{total:g} {kind} >= {lo}")
                group_passed &= passed
            if hi is not None:
                passed = total - 1e-8 <= hi
                expect("requirement", group["name"], passed, f"{total:g} {kind} <= {hi}")
                group_passed &= passed
        groups.append({"name": group["name"], "matched_courses": sorted(members),
                       "units": totals["units"], "course_count": totals["courses"],
                       **bounds, "passed": bool(group_passed)})
    return result()


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
