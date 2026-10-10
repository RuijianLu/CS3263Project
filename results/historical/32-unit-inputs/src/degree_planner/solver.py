"""Proposal sub-problems 1-3: compile declarative constraints into a finite CSP."""
from __future__ import annotations
from ortools.sat.python import cp_model
from .schemas import validate_spec

def solve(spec, courses, corequisite_pairs=(), time_limit=10):
    validate_spec(spec, courses)
    model = cp_model.CpModel()
    completed, horizon = set(spec["completed"]), len(spec["semesters"])
    x = {c: [model.new_bool_var(f"{c}_{t}") for t in range(horizon)] for c in courses}
    selected = {}
    for code, course in courses.items():
        model.add(sum(x[code]) <= 1)
        if code in completed or not course["selectable"]:
            model.add(sum(x[code]) == 0)
        for t, semester in enumerate(spec["semesters"]):
            if semester not in course["offered_semesters"]:
                model.add(x[code][t] == 0)
        selected[code] = model.new_bool_var(f"selected_{code}")
        model.add(selected[code] == (1 if code in completed else sum(x[code])))

    cache = {}
    def before(code, t):
        if code in completed:
            return model.new_constant(1)
        if code not in courses:
            return model.new_constant(0)
        key = (code, t)
        if key not in cache:
            cache[key] = model.new_bool_var(f"before_{code}_{t}")
            model.add(cache[key] == sum(x[code][:t]))
        return cache[key]

    def expression(tree, t):
        if tree is None or tree is True:
            return model.new_constant(1)
        if tree is False:
            return model.new_constant(0)
        if isinstance(tree, str):
            return before(tree, t)
        if "nOf" in tree:
            threshold, trees = tree["nOf"]
        else:
            op = "and" if "and" in tree else "or"
            trees = tree[op]
            threshold = len(trees) if op == "and" else 1
        children = [expression(child, t) for child in trees]
        z = model.new_bool_var("prerequisite")
        model.add(sum(children) >= threshold).only_enforce_if(z)
        model.add(sum(children) < threshold).only_enforce_if(z.Not())
        return z

    for code, course in courses.items():
        for t in range(horizon):
            model.add(x[code][t] <= expression(course["prerequisites"], t))
            for other in course["corequisites"]:
                if other in courses:
                    model.add(x[code][t] <= before(other, t) + x[other][t])
                else:
                    model.add(x[code][t] == 0)
        for other in course["preclusions"]:
            if other in selected and other != code and not {code, other} <= completed:
                model.add(selected[code] + selected[other] <= 1)
    for a, b in corequisite_pairs:
        if a in x and b in x:
            for t in range(horizon):
                model.add(x[a][t] == x[b][t])

    # Hundredths preserve fractional course credits without floating-point constraints.
    units = {c: round(course["units"] * 100) for c, course in courses.items()}
    for t in range(horizon):
        model.add(sum(units[c] * x[c][t] for c in courses) <= spec["max_units"] * 100)
    for code in spec["required"]:
        model.add(selected[code] == 1)
    for code in spec["forbidden"]:
        model.add(sum(x[code]) == 0)
    for fixed in spec["fixed"]:
        model.add(x[fixed["course"]][fixed["semester"] - 1] == 1)
    for group in spec["groups"]:
        members = group["courses"]
        for kind, total in [("units", sum(units[c] * selected[c] for c in members)),
                            ("courses", sum(selected[c] for c in members))]:
            scale = 100 if kind == "units" else 1
            for bound, relation in [("min", ">="), ("max", "<=")]:
                value = group[f"{bound}_{kind}"]
                if value is not None:
                    model.add(total >= value * scale if relation == ">=" else total <= value * scale)

    # Tie-breaking only: prefer fewer new courses and earlier completion.
    model.minimize(sum((horizon * len(courses) + t + 1) * x[c][t]
                       for c in courses for t in range(horizon)))
    engine = cp_model.CpSolver()
    engine.parameters.max_time_in_seconds = time_limit
    engine.parameters.num_search_workers = 1
    engine.parameters.random_seed = 3263
    status = engine.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": "feasible",
                "semesters": [[c for c in courses if engine.value(x[c][t])] for t in range(horizon)],
                "explanation": engine.status_name(status)}
    if status == cp_model.INFEASIBLE:
        return {"status": "infeasible", "semesters": [], "explanation": "Proven infeasible by CP-SAT"}
    return {"status": "unknown", "semesters": [], "explanation": engine.status_name(status)}
