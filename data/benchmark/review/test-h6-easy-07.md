# test-h6-easy-07

Designed difficulty: easy; label: feasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS2030S, MA1521, MA1522, ST2334. I have 6 remaining normal semesters, starting with Semester 1; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS4243. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 8 | CS1101S, MA1521 |
| 2 | 2 | 12 | CS2030S, MA1522, ST2334 |

# Local CSP solution and validation

Solver status: **feasible**. Independent schedule validation: **PASS**.

Feasible assignment found; no optimization objective.

This is local feasibility validation, not a comparison experiment or a graduation audit.

## 1. Input specification

Maximum workload: **16 units**, no minimum.
Remaining normal semesters: [1, 2, 1, 2, 1, 2].
Completed record: CP3200, CS1101S, CS2030S, MA1521, MA1522, ST2334.
Read spec.json for the exact required, forbidden, fixed and group fields.

## 2. Compiled CSP

Read csp.md for the overview, csp.json for every variable and constraint, and model.pbtxt for the actual CP-SAT model.
The model has no course-count or semester-position objective.

## 3. Schedule

| Remaining position | Normal semester | Units / cap | Courses |
|---:|---:|---:|---|
| 1 | 1 | 0 / 16 | (empty) |
| 2 | 2 | 8 / 16 | CS1231S, CS2100 |
| 3 | 1 | 8 / 16 | CS2040S, CS2106 |
| 4 | 2 | 16 / 16 | CS2109S, CS3230, CS4243, CS4277 |
| 5 | 1 | 16 / 16 | CS2101, CS2103T, CS3268, CS4261 |
| 6 | 2 | 12 / 16 | CS3263, CS3264, CS5242 |

Course titles and credits are listed in schedule.csv. Completed courses are not repeated.

## 4. Independent checks

| Check family | Passed | Total |
|---|---:|---:|
| availability | 15 | 15 |
| corequisite | 1 | 1 |
| duplicate | 21 | 21 |
| eligibility | 15 | 15 |
| forbidden | 15 | 15 |
| horizon | 1 | 1 |
| preclusion | 23 | 23 |
| prerequisite | 15 | 15 |
| required | 14 | 14 |
| requirement | 8 | 8 |
| workload | 6 | 6 |

### Programme group totals

| Group | Actual units | Actual courses | Unit bounds | Course bounds | Pass |
|---|---:|---:|---|---|---|
| breadth | 34 | 8 | 32 .. - | - .. - | True |
| breadth_upper | 16 | 4 | 12 .. - | - .. - | True |
| ai_primary | 20 | 5 | - .. - | 3 .. - | True |
| ai_upper | 4 | 1 | - .. - | 1 .. - | True |
| industry | 6 | 1 | 6 .. 12 | - .. - | True |
| cp_non_industry | 0 | 0 | - .. 12 | - .. - | True |
| programme_lower | 78 | 19 | 64 .. - | - .. - | True |

Each group's matched courses:

- breadth: CP3200, CS3263, CS3264, CS3268, CS4243, CS4261, CS4277, CS5242.
- breadth_upper: CS4243, CS4261, CS4277, CS5242.
- ai_primary: CS2109S, CS3263, CS3264, CS3268, CS4243.
- ai_upper: CS4243.
- industry: CP3200.
- cp_non_industry: (none).
- programme_lower: CP3200, CS1231S, CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2106, CS2109S, CS3230, CS3263, CS3264, CS3268, CS4243, CS4261, CS4277, MA1521, MA1522, ST2334.

### Violations

None. All checks passed.

validation.json contains individual pass/fail checks and group membership.
A non-feasible plan has no independently validated schedule; only CP-SAT can supply its infeasibility proof.

