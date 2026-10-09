"""Independent checks of proposal sub-problems 1-3 and benchmark integrity."""
from __future__ import annotations
import copy
from itertools import product
from pathlib import Path
import pytest
from degree_planner.collect import read_json
from degree_planner.benchmark import gold_spec, load_jsonl, group
from degree_planner.checker import check
from degree_planner.normalize import resolve
from degree_planner.solver import solve

ROOT = Path(__file__).resolve().parents[1]

def course(code, units=4, offered=(1,2), prerequisite=None):
    return dict(code=code, units=units, offered_semesters=list(offered),
                prerequisites=prerequisite, corequisites=[], preclusions=[], selectable=True)

def small_spec(required, semesters=(1,2), max_units=32):
    return dict(completed=[], semesters=list(semesters), max_units=max_units,
                required=list(required), forbidden=[], fixed=[], groups=[])

def exhaustive(spec, courses, pairs=()):
    # Enumerate assignments without using any solver expression/compiler.
    names = list(courses)
    for assignments in product(range(len(spec["semesters"])+1), repeat=len(names)):
        plan = {"status":"feasible", "semesters":[[] for _ in spec["semesters"]], "explanation":"enumerated"}
        for code, semester in zip(names, assignments):
            if semester: plan["semesters"][semester-1].append(code)
        if check(plan,spec,courses,pairs)["valid"]: return True
    return False

@pytest.mark.parametrize("spec,courses,pairs", [
    (small_spec(["A","B"]), {"A":course("A"),"B":course("B",prerequisite="A")}, ()),
    (small_spec(["A","B"],(1,)), {"A":course("A"),"B":course("B",prerequisite="A")}, ()),
    (small_spec(["A"],(2,)), {"A":course("A",offered=(1,))}, ()),
    (small_spec(["A","B"],(1,),4), {"A":course("A"),"B":course("B")}, ()),
    (small_spec(["A","B"]), {"A":course("A",offered=(1,)),"B":course("B",offered=(2,))}, (("A","B"),)),
    (small_spec(["C"]), {"A":course("A"),"B":course("B"),"C":course("C",prerequisite={"nOf":[1,["A","B"]]})}, ())
])
def test_solver_agrees_with_exhaustive_search(spec,courses,pairs):
    result=solve(spec,courses,pairs)
    assert (result["status"]=="feasible")==exhaustive(spec,courses,pairs)
    if result["status"]=="feasible": assert check(result,spec,courses,pairs)["valid"]

def test_completed_prerequisite_is_not_repeated():
    courses={"A":course("A"),"B":course("B",prerequisite="A")}
    spec=small_spec(["A","B"],(1,))
    spec["completed"]=["A"]
    result=solve(spec,courses)
    assert result["semesters"]==[["B"]]

def test_preclusion_with_completed_course():
    courses={"A":course("A"),"B":course("B")}
    courses["A"]["preclusions"]=["B"]
    spec=small_spec(["B"])
    spec["completed"]=["A"]
    assert solve(spec,courses)["status"]=="infeasible"

def test_fractional_credits_and_no_minimum():
    courses={"A":course("A",2.5),"B":course("B",2.5)}
    spec=small_spec(["A","B"],max_units=4)
    result=solve(spec,courses)
    assert result["status"]=="feasible"
    assert check(result,spec,courses)["valid"]
    assert check({"status":"feasible","semesters":[[],[]],"explanation":""},small_spec([]),courses)["valid"]

def test_checker_rejects_same_semester_prerequisite():
    courses={"A":course("A"),"B":course("B",prerequisite="A")}
    report=check({"status":"feasible","semesters":[["A","B"],[]],"explanation":""},small_spec(["B"]),courses)
    assert "prerequisite" in {v["type"] for v in report["violations"]}

def test_focus_shares_completion_without_breadth_credits():
    courses=read_json(ROOT/"data/courses.json")
    req=read_json(ROOT/"data/requirements.json")
    spec=gold_spec(courses,req,["CS2109S","CP3200"],4)
    groups={g["name"]:g for g in spec["groups"]}
    assert "CS2109S" in groups["ai_primary"]["courses"]
    assert "CS2109S" not in groups["breadth"]["courses"]
    assert "CP3200" in groups["breadth"]["courses"]

def test_grade_and_cohort_normalisation():
    assert resolve({"nOf":[1,["CS1231S:D","CS2040S:D"]]})=={"nOf":[1,["CS1231S","CS2040S"]]}
    assert resolve({"cohort":{"rule":"IF_IN","years":["S:2025"]},"then":"CS2109S:D"})=="CS2109S"
    assert resolve({"cohort":{"rule":"IF_IN","years":["E:2025"]},"then":"CS2109S:D"}) is True
    with pytest.raises(ValueError): resolve("CS1010%:D")

def test_benchmark_labels_and_counts():
    gold=load_jsonl(ROOT/"data/benchmark/gold.jsonl")
    tests=load_jsonl(ROOT/"data/benchmark/test.jsonl")
    assert len(gold)==30 and len(tests)==24
    assert len({g["id"] for g in gold})==30
    assert sum(g["status"]=="infeasible" and g["id"].startswith("test-") for g in gold)==6
    courses=read_json(ROOT/"data/courses.json")
    req=read_json(ROOT/"data/requirements.json")
    for answer in gold:
        plan=solve(answer["spec"],courses,req["corequisite_pairs"])
        assert plan["status"]==answer["status"], answer["id"]
        if plan["status"]=="feasible":
            assert check(plan,answer["spec"],courses,req["corequisite_pairs"])["valid"],answer["id"]

def test_checker_detects_mutated_real_plan():
    courses=read_json(ROOT/"data/courses.json")
    req=read_json(ROOT/"data/requirements.json")
    answer=next(g for g in load_jsonl(ROOT/"data/benchmark/gold.jsonl") if g["id"]=="test-easy-06")
    plan=copy.deepcopy(answer["reference_plan"])
    plan["semesters"][0].append("CS4246")
    assert not check(plan,answer["spec"],courses,req["corequisite_pairs"])["valid"]
