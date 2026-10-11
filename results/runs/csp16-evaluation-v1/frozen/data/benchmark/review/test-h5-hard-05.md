# test-h5-hard-05

Designed difficulty: hard; label: feasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2040S, CS2109S, CS3230, MA1521, MA1522, ST2334. I have 5 remaining normal semesters, starting with Semester 2; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS3268, CS4243, CS4246, CS5260, CS5339, CS5340. Do not newly enroll in CS4248, CS4261, CS4278, CS5228. Take CS2030S in remaining semester number 2. Take CS2101 in remaining semester number 4. Take CS2103T in remaining semester number 4. Take CS2106 in remaining semester number 4. Take CS5340 in remaining semester number 5. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 16 | CS1101S, CS1231S, MA1521, MA1522 |
| 2 | 2 | 8 | CS2040S, ST2334 |
| 3 | 1 | 8 | CS2109S, CS3230 |

# Local CSP solution and validation

Solver status: **feasible**. Independent schedule validation: **PASS**.

Feasible assignment found; no optimization objective.

This is local feasibility validation, not a comparison experiment or a graduation audit.

## 1. Input specification

Maximum workload: **16 units**, no minimum.
Remaining normal semesters: [2, 1, 2, 1, 2].
Completed record: CP3200, CS1101S, CS1231S, CS2040S, CS2109S, CS3230, MA1521, MA1522, ST2334.
Read spec.json for the exact required, forbidden, fixed and group fields.

## 2. Compiled CSP

Read csp.md for the overview, csp.json for every variable and constraint, and model.pbtxt for the actual CP-SAT model.
The model has no course-count or semester-position objective.

## 3. Schedule

| Remaining position | Normal semester | Units / cap | Courses |
|---:|---:|---:|---|
| 1 | 2 | 16 / 16 | CS2100, CS3263, CS3264, CS5242 |
| 2 | 1 | 12 / 16 | CS2030S, CS3268, CS4246 |
| 3 | 2 | 8 / 16 | CS4243, CS5260 |
| 4 | 1 | 12 / 16 | CS2101, CS2103T, CS2106 |
| 5 | 2 | 8 / 16 | CS5339, CS5340 |

Course titles and credits are listed in schedule.csv. Completed courses are not repeated.

## 4. Independent checks

| Check family | Passed | Total |
|---|---:|---:|
| availability | 14 | 14 |
| corequisite | 1 | 1 |
| duplicate | 19 | 19 |
| eligibility | 14 | 14 |
| fixed_semester | 5 | 5 |
| forbidden | 14 | 14 |
| horizon | 1 | 1 |
| preclusion | 11 | 11 |
| prerequisite | 14 | 14 |
| required | 19 | 19 |
| requirement | 8 | 8 |
| workload | 5 | 5 |

### Programme group totals

| Group | Actual units | Actual courses | Unit bounds | Course bounds | Pass |
|---|---:|---:|---|---|---|
| breadth | 42 | 10 | 32 .. - | - .. - | True |
| breadth_upper | 24 | 6 | 12 .. - | - .. - | True |
| ai_primary | 24 | 6 | - .. - | 3 .. - | True |
| ai_upper | 8 | 2 | - .. - | 1 .. - | True |
| industry | 6 | 1 | 6 .. 12 | - .. - | True |
| cp_non_industry | 0 | 0 | - .. 12 | - .. - | True |
| programme_lower | 74 | 18 | 64 .. - | - .. - | True |

Each group's matched courses:

- breadth: CP3200, CS3263, CS3264, CS3268, CS4243, CS4246, CS5242, CS5260, CS5339, CS5340.
- breadth_upper: CS4243, CS4246, CS5242, CS5260, CS5339, CS5340.
- ai_primary: CS2109S, CS3263, CS3264, CS3268, CS4243, CS4246.
- ai_upper: CS4243, CS4246.
- industry: CP3200.
- cp_non_industry: (none).
- programme_lower: CP3200, CS1231S, CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2106, CS2109S, CS3230, CS3263, CS3264, CS3268, CS4243, CS4246, MA1521, MA1522, ST2334.

### Violations

None. All checks passed.

validation.json contains individual pass/fail checks and group membership.
A non-feasible plan has no independently validated schedule; only CP-SAT can supply its infeasibility proof.

