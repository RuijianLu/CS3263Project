# Local CSP solution and validation

Solver status: **feasible**. Independent schedule validation: **PASS**.

Feasible assignment found; no optimization objective.

This is local feasibility validation, not a comparison experiment or a graduation audit.

## 1. Input specification

Maximum workload: **16 units**, no minimum.
Remaining normal semesters: [2, 1, 2, 1, 2, 1, 2].
Completed record: CP3200, CS1101S, CS1231S, MA1521.
Read spec.json for the exact required, forbidden, fixed and group fields.

## 2. Compiled CSP

Read csp.md for the overview, csp.json for every variable and constraint, and model.pbtxt for the actual CP-SAT model.
The model has no course-count or semester-position objective.

## 3. Schedule

| Remaining position | Normal semester | Units / cap | Courses |
|---:|---:|---:|---|
| 1 | 2 | 8 / 16 | CS2040S, MA2104 |
| 2 | 1 | 0 / 16 | (empty) |
| 3 | 2 | 16 / 16 | CS2100, CS2109S, MA1522, ST2334 |
| 4 | 1 | 4 / 16 | CS4261 |
| 5 | 2 | 12 / 16 | CS2030S, CS2106, CS3230 |
| 6 | 1 | 16 / 16 | CS2101, CS2103T, CS3268, CS4243 |
| 7 | 2 | 16 / 16 | CS3264, CS4248, CS4277, CS5242 |

Course titles and credits are listed in schedule.csv. Completed courses are not repeated.

## 4. Independent checks

| Check family | Passed | Total |
|---|---:|---:|
| availability | 18 | 18 |
| corequisite | 1 | 1 |
| duplicate | 25 | 25 |
| eligibility | 18 | 18 |
| forbidden | 18 | 18 |
| horizon | 1 | 1 |
| preclusion | 29 | 29 |
| prerequisite | 18 | 18 |
| required | 13 | 13 |
| requirement | 8 | 8 |
| workload | 7 | 7 |

### Programme group totals

| Group | Actual units | Actual courses | Unit bounds | Course bounds | Pass |
|---|---:|---:|---|---|---|
| breadth | 34 | 8 | 32 .. - | - .. - | True |
| breadth_upper | 20 | 5 | 12 .. - | - .. - | True |
| ai_primary | 20 | 5 | - .. - | 3 .. - | True |
| ai_upper | 8 | 2 | - .. - | 1 .. - | True |
| industry | 6 | 1 | 6 .. 12 | - .. - | True |
| cp_non_industry | 0 | 0 | - .. 12 | - .. - | True |
| programme_lower | 78 | 19 | 64 .. - | - .. - | True |

Each group's matched courses:

- breadth: CP3200, CS3264, CS3268, CS4243, CS4248, CS4261, CS4277, CS5242.
- breadth_upper: CS4243, CS4248, CS4261, CS4277, CS5242.
- ai_primary: CS2109S, CS3264, CS3268, CS4243, CS4248.
- ai_upper: CS4243, CS4248.
- industry: CP3200.
- cp_non_industry: (none).
- programme_lower: CP3200, CS1231S, CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2106, CS2109S, CS3230, CS3264, CS3268, CS4243, CS4248, CS4261, CS4277, MA1521, MA1522, ST2334.

### Violations

None. All checks passed.

validation.json contains individual pass/fail checks and group membership.
A non-feasible plan has no independently validated schedule; only CP-SAT can supply its infeasibility proof.
