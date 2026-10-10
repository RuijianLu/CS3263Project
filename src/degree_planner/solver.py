"""Proposal sub-problems 1-3: solve a CSP for any feasible assignment."""
from __future__ import annotations
from ortools.sat.python import cp_model
from .csp import build_csp


def solve_csp(problem, time_limit=10):
    """Find a feasible schedule without optimizing course count or semester position."""
    if time_limit <= 0:
        raise ValueError("Solver time limit must be positive")
    engine = cp_model.CpSolver()
    engine.parameters.max_time_in_seconds = time_limit
    engine.parameters.num_search_workers = 1
    engine.parameters.random_seed = 3263
    status = engine.solve(problem.model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        horizon = len(problem.inspection["remaining_semesters"])
        return {"status": "feasible",
                "semesters": [[c for c in problem.enrollments if engine.value(problem.enrollments[c][t])]
                              for t in range(horizon)],
                "explanation": "Feasible assignment found; no optimization objective."}
    if status == cp_model.INFEASIBLE:
        return {"status": "infeasible", "semesters": [],
                "explanation": "Proven infeasible for this specification by CP-SAT."}
    if status == cp_model.MODEL_INVALID:
        raise ValueError("CP-SAT rejected the compiled CSP")
    return {"status": "unknown", "semesters": [],
            "explanation": "Search stopped without a solution or an infeasibility proof."}


def solve(spec, courses, corequisite_pairs=(), time_limit=10):
    return solve_csp(build_csp(spec, courses, corequisite_pairs), time_limit)
