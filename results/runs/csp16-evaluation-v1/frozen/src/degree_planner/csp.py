"""Proposal sub-problems 1-3: explicit Boolean CSP construction and inspection."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from ortools.sat.python import cp_model
from .policy import FORMULATION_VERSION
from .schemas import validate_spec


@dataclass
class CspProblem:
    model: cp_model.CpModel
    enrollments: dict
    selected: dict
    inspection: dict


def build_csp(spec, courses, corequisite_pairs=()):
    """Construct variables, domains and constraints without searching."""
    validate_spec(spec, courses)
    model = cp_model.CpModel()
    completed, horizon = set(spec["completed"]), len(spec["semesters"])
    roles, rules = {}, []

    def boolean(name, role):
        roles[name] = role
        return model.new_bool_var(name)

    def add(family, description, expression, condition=None):
        index = len(model.proto.constraints)
        constraint = model.add(expression)
        if condition is not None:
            constraint.only_enforce_if(condition)
        rules.append({"id": f"C{index + 1:04d}", "family": family,
                      "description": description, "backend_index": index})
        return constraint

    x = {c: [boolean(f"x_{c}_{t + 1}", "enrolment") for t in range(horizon)] for c in courses}
    y = {c: boolean(f"y_{c}", "completion_or_selection") for c in courses}

    for code, course in courses.items():
        add("no_retake", f"sum_t x_{code}_t <= 1", sum(x[code]) <= 1)
        if code in completed or not course["selectable"]:
            reason = "already completed" if code in completed else "not selectable"
            add("eligibility", f"sum_t x_{code}_t = 0 ({reason})", sum(x[code]) == 0)
        for t, season in enumerate(spec["semesters"]):
            if season not in course["offered_semesters"]:
                add("offering", f"x_{code}_{t + 1} = 0 (not offered in normal Semester {season})",
                    x[code][t] == 0)
        done = code in completed
        add("selection_link", f"y_{code} = " + ("1 (completed)" if done else f"sum_t x_{code}_t"),
            y[code] == (1 if done else sum(x[code])))

    cache = {}
    def before(code, t):
        if code in completed:
            return 1
        if code not in courses:
            return 0
        key = code, t
        if key not in cache:
            z = boolean(f"before_{code}_{t + 1}", "completed_before_semester")
            add("before_link", f"{z.name} = sum_(s < {t + 1}) x_{code}_s", z == sum(x[code][:t]))
            cache[key] = z
        return cache[key]

    def name(value):
        return str(value) if isinstance(value, int) else value.name

    def prerequisite(tree, t, prefix):
        if tree is None or tree is True:
            return 1
        if tree is False:
            return 0
        if isinstance(tree, str):
            return before(tree, t)
        if "nOf" in tree:
            threshold, trees = tree["nOf"]
        else:
            op = "and" if "and" in tree else "or"
            trees = tree[op]
            threshold = len(trees) if op == "and" else 1
        children = [prerequisite(child, t, f"{prefix}_{i + 1}") for i, child in enumerate(trees)]
        z = boolean(prefix, "prerequisite_expression")
        terms = " + ".join(name(child) for child in children) or "0"
        add("prerequisite_logic", f"{z.name} = 1 implies ({terms}) >= {threshold}",
            sum(children) >= threshold, z)
        add("prerequisite_logic", f"{z.name} = 0 implies ({terms}) < {threshold}",
            sum(children) < threshold, z.Not())
        return z

    for code, course in courses.items():
        for t in range(horizon):
            p = prerequisite(course["prerequisites"], t, f"prereq_{code}_{t + 1}")
            add("prerequisite", f"x_{code}_{t + 1} <= {name(p)}", x[code][t] <= p)
            for other in course["corequisites"]:
                if other in courses:
                    earlier = before(other, t)
                    add("corequisite", f"x_{code}_{t + 1} <= {name(earlier)} + x_{other}_{t + 1}",
                        x[code][t] <= earlier + x[other][t])
                else:
                    add("corequisite", f"x_{code}_{t + 1} = 0 (unavailable co-requisite {other})",
                        x[code][t] == 0)

    pairs = set()
    for code, course in courses.items():
        for other in course["preclusions"]:
            if other in y and other != code:
                pair = tuple(sorted((code, other)))
                if pair not in pairs and not set(pair) <= completed:
                    a, b = pair
                    add("preclusion", f"y_{a} + y_{b} <= 1", y[a] + y[b] <= 1)
                    pairs.add(pair)
    for a, b in corequisite_pairs:
        if a in x and b in x:
            for t in range(horizon):
                add("paired_enrolment", f"x_{a}_{t + 1} = x_{b}_{t + 1}", x[a][t] == x[b][t])

    units = {}
    for code, course in courses.items():
        scaled = Decimal(str(course["units"])) * 100
        if not scaled.is_finite() or scaled < 0 or scaled != scaled.to_integral_value():
            raise ValueError(f"{code}: units must be nonnegative multiples of 0.01")
        units[code] = int(scaled)
    for t in range(horizon):
        add("workload", f"sum_c units(c) * x_c_{t + 1} <= {spec['max_units']} units",
            sum(units[c] * x[c][t] for c in courses) <= spec["max_units"] * 100)
    for code in spec["required"]:
        add("required", f"y_{code} = 1", y[code] == 1)
    for code in spec["forbidden"]:
        add("forbidden", f"sum_t x_{code}_t = 0 (new enrolment forbidden)", sum(x[code]) == 0)
    for fixed in spec["fixed"]:
        code, semester = fixed["course"], fixed["semester"]
        add("fixed_semester", f"x_{code}_{semester} = 1", x[code][semester - 1] == 1)
    for group in spec["groups"]:
        members = group["courses"]
        for kind, total in [("units", sum(units[c] * y[c] for c in members)),
                            ("courses", sum(y[c] for c in members))]:
            scale = 100 if kind == "units" else 1
            for bound in ("min", "max"):
                value = group[f"{bound}_{kind}"]
                if value is not None:
                    relation = ">=" if bound == "min" else "<="
                    expr = total >= value * scale if bound == "min" else total <= value * scale
                    add("programme_group",
                        f"{group['name']}: selected/completed members' {kind} {relation} {value}", expr)

    # Satisfaction only: no objective on course count or semester position.
    error = model.validate()
    if error:
        raise ValueError(f"Invalid compiled CSP: {error}")
    variables = [{"index": i, "name": v.name or f"constant_{i}",
                  "domain_intervals": list(v.domain), "role": roles.get(v.name, "constant")}
                 for i, v in enumerate(model.proto.variables)]
    inspection = {
        "formulation": FORMULATION_VERSION, "objective": None,
        "specification": deepcopy(spec),
        "max_units": spec["max_units"], "remaining_semesters": list(spec["semesters"]),
        "units_scale": 100, "domain_encoding": "Inclusive interval endpoints: [0,1] means {0,1}.",
        "variable_count": len(variables), "constraint_count": len(rules),
        "variable_roles": dict(Counter(v["role"] for v in variables)),
        "constraint_families": dict(Counter(r["family"] for r in rules)),
        "variables": variables, "constraints": rules,
        "courses": {c: {k: v[k] for k in ("units", "offered_semesters", "prerequisites",
                                         "corequisites", "preclusions", "selectable")}
                    for c, v in courses.items()},
        "corequisite_pairs": [list(pair) for pair in corequisite_pairs],
    }
    return CspProblem(model, x, y, inspection)
