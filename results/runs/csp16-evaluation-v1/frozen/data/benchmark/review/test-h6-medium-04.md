# test-h6-medium-04

Designed difficulty: medium; label: feasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2040S, CS2100, MA1521, MA1522. I have 6 remaining normal semesters, starting with Semester 1; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS4220, CS4248, CS5339. Do not newly enroll in CS3263, CS4261. Take ST2334 in remaining semester number 2. Take CS5339 in remaining semester number 6. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 12 | CS1101S, CS1231S, MA1521 |
| 2 | 2 | 12 | CS2040S, CS2100, MA1522 |

# Local CSP solution and validation

Solver status: **feasible**. Independent schedule validation: **PASS**.

Feasible assignment found; no optimization objective.

This is local feasibility validation, not a comparison experiment or a graduation audit.

## 1. Input specification

Maximum workload: **16 units**, no minimum.
Remaining normal semesters: [1, 2, 1, 2, 1, 2].
Completed record: CP3200, CS1101S, CS1231S, CS2040S, CS2100, MA1521, MA1522.
Read spec.json for the exact required, forbidden, fixed and group fields.

## 2. Compiled CSP

Read csp.md for the overview, csp.json for every variable and constraint, and model.pbtxt for the actual CP-SAT model.
The model has no course-count or semester-position objective.

## 3. Schedule

| Remaining position | Normal semester | Units / cap | Courses |
|---:|---:|---:|---|
| 1 | 1 | 8 / 16 | CS3230, LSM1301 |
| 2 | 2 | 4 / 16 | ST2334 |
| 3 | 1 | 4 / 16 | CS2109S |
| 4 | 2 | 16 / 16 | CS2030S, CS4248, CS5242, ZB2101 |
| 5 | 1 | 16 / 16 | CS2101, CS2103T, CS2106, CS3264 |
| 6 | 2 | 16 / 16 | CS4220, CS4243, CS4262, CS5339 |

Course titles and credits are listed in schedule.csv. Completed courses are not repeated.

## 4. Independent checks

| Check family | Passed | Total |
|---|---:|---:|
| availability | 16 | 16 |
| corequisite | 1 | 1 |
| duplicate | 22 | 22 |
| eligibility | 16 | 16 |
| fixed_semester | 2 | 2 |
| forbidden | 16 | 16 |
| horizon | 1 | 1 |
| preclusion | 18 | 18 |
| prerequisite | 16 | 16 |
| required | 16 | 16 |
| requirement | 8 | 8 |
| workload | 6 | 6 |

### Programme group totals

| Group | Actual units | Actual courses | Unit bounds | Course bounds | Pass |
|---|---:|---:|---|---|---|
| breadth | 34 | 8 | 32 .. - | - .. - | True |
| breadth_upper | 24 | 6 | 12 .. - | - .. - | True |
| ai_primary | 20 | 5 | - .. - | 3 .. - | True |
| ai_upper | 12 | 3 | - .. - | 1 .. - | True |
| industry | 6 | 1 | 6 .. 12 | - .. - | True |
| cp_non_industry | 0 | 0 | - .. 12 | - .. - | True |
| programme_lower | 74 | 18 | 64 .. - | - .. - | True |

Each group's matched courses:

- breadth: CP3200, CS3264, CS4220, CS4243, CS4248, CS4262, CS5242, CS5339.
- breadth_upper: CS4220, CS4243, CS4248, CS4262, CS5242, CS5339.
- ai_primary: CS2109S, CS3264, CS4243, CS4248, CS4262.
- ai_upper: CS4243, CS4248, CS4262.
- industry: CP3200.
- cp_non_industry: (none).
- programme_lower: CP3200, CS1231S, CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2106, CS2109S, CS3230, CS3264, CS4220, CS4243, CS4248, CS4262, MA1521, MA1522, ST2334.

### Violations

None. All checks passed.

validation.json contains individual pass/fail checks and group membership.
A non-feasible plan has no independently validated schedule; only CP-SAT can supply its infeasibility proof.

