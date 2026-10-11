"""Proposal sub-problems 1-3: feasible outputs and independent validation; no enumeration."""
from __future__ import annotations
import copy
from pathlib import Path
import pytest
from degree_planner.collect import read_json
from degree_planner.benchmark import gold_spec
from degree_planner.checker import check
from degree_planner.csp import build_csp
from degree_planner.inspection import solve_and_export
from degree_planner.policy import MAX_UNITS
from degree_planner.schemas import validate_spec
from degree_planner.solver import solve

ROOT = Path(__file__).resolve().parents[1]


def course(code, units=4, prerequisite=None):
    return dict(code=code, title=code, units=units, offered_semesters=[1,2],
                prerequisites=prerequisite, corequisites=[], preclusions=[], selectable=True)


def small_spec(required, semesters=(1,2), max_units=MAX_UNITS):
    return dict(completed=[], semesters=list(semesters), max_units=max_units,
                required=list(required), forbidden=[], fixed=[], groups=[])


@pytest.mark.parametrize("example", ["foundation-remaining","ai-remaining"])
def test_real_example_produces_independently_valid_schedule(example):
    courses=read_json(ROOT/"data/courses.json")
    req=read_json(ROOT/"data/requirements.json")
    spec=read_json(ROOT/f"data/examples/{example}.json")
    assert spec["max_units"] == req["max_units_per_semester"] == 16
    plan=solve(spec,courses,req["corequisite_pairs"])
    checked=check(plan,spec,courses,req["corequisite_pairs"])
    assert plan["status"]=="feasible"
    assert checked["valid"], checked["violations"]
    assert all(s["units"]<=16 for s in checked["semesters"])
    assert all(g["passed"] for g in checked["groups"])


def test_feasibility_model_has_no_objective():
    courses={"A":course("A"),"B":course("B",prerequisite="A")}
    problem=build_csp(small_spec(["B"]),courses)
    assert not problem.model.has_objective()
    assert problem.inspection["objective"] is None
    assert problem.inspection["constraint_count"]==len(problem.model.proto.constraints)


def test_larger_workload_is_rejected():
    courses={"A":course("A")}
    spec=small_spec(["A"],max_units=32)
    with pytest.raises(ValueError):
        validate_spec(spec,courses)
    assert not check({"status":"feasible","semesters":[["A"],[]],"explanation":""},spec,courses)["valid"]


def test_workload_and_prerequisites_are_independently_checked():
    courses={c:course(c) for c in ("A","B","C","D","E")}
    courses["E"]["prerequisites"]="A"
    spec=small_spec(list(courses))
    plan=solve(spec,courses)
    assert check(plan,spec,courses)["valid"]
    invalid={"status":"feasible","semesters":[list(courses),[]],"explanation":""}
    failures={v["type"] for v in check(invalid,spec,courses)["violations"]}
    assert {"workload","prerequisite"}<=failures


def test_completed_prerequisite_and_concurrent_pair():
    courses={"A":course("A"),"B":course("B",prerequisite="A"),"C":course("C")}
    spec=small_spec(["A","B","C"],semesters=(1,))
    spec["completed"]=["A"]
    plan=solve(spec,courses,[("B","C")])
    assert set(plan["semesters"][0])=={"B","C"}
    assert check(plan,spec,courses,[("B","C")])["valid"]


def test_or_prerequisite_and_preclusion_produce_valid_choice():
    courses={"A":course("A"),"B":course("B"),"C":course("C",prerequisite={"or":["A","B"]})}
    courses["A"]["preclusions"]=["B"]
    spec=small_spec(["C"])
    assert check(solve(spec,courses),spec,courses)["valid"]


def test_fractional_credits_and_empty_semesters_are_allowed():
    courses={"A":course("A",2.5),"B":course("B",2.5)}
    spec=small_spec(["A","B"],max_units=4)
    assert check(solve(spec,courses),spec,courses)["valid"]
    assert check({"status":"feasible","semesters":[[],[]],"explanation":""},small_spec([]),courses)["valid"]


def test_focus_counts_do_not_duplicate_breadth_credits():
    courses=read_json(ROOT/"data/courses.json")
    req=read_json(ROOT/"data/requirements.json")
    spec=gold_spec(courses,req,["CS2109S","CP3200"],4)
    groups={g["name"]:g for g in spec["groups"]}
    assert "CS2109S" in groups["ai_primary"]["courses"]
    assert "CS2109S" not in groups["breadth"]["courses"]
    assert "CP3200" in groups["breadth"]["courses"]


def test_saved_stages_can_be_checked_again(tmp_path):
    source=ROOT/"data/examples/ai-remaining.json"
    spec=read_json(source)
    output=tmp_path/"inspection"
    plan,checked=solve_and_export(ROOT,spec,source,output)
    assert checked["valid"]
    assert {p.name for p in output.iterdir()} >= {
        "spec.json","request.txt","csp.json","csp.md","model.pbtxt",
        "plan.json","schedule.csv","validation.json","report.md","manifest.json"}
    courses=read_json(ROOT/"data/courses.json")
    req=read_json(ROOT/"data/requirements.json")
    assert check(read_json(output/"plan.json"),read_json(output/"spec.json"),courses,req["corequisite_pairs"])["valid"]
    assert "PASS" in (output/"report.md").read_text(encoding="utf-8")
