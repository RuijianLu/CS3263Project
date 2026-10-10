# test-h6-hard-06

Designed difficulty: hard; label: feasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2030S, CS2040S, MA1521, MA1522, ST2334. I have 6 remaining normal semesters, starting with Semester 1; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS3263, CS3264, CS4220, CS4246, CS4277, CS5228. Do not newly enroll in CS4261, CS4262, CS5242, CS5339. Take CS2101 in remaining semester number 3. Take CS3263 in remaining semester number 4. Take CS3264 in remaining semester number 4. Take CS3230 in remaining semester number 5. Take CS4277 in remaining semester number 6. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 16 | CS1101S, CS1231S, MA1521, MA1522 |
| 2 | 2 | 12 | CS2030S, CS2040S, ST2334 |

# Local CSP solution and validation

Solver status: **feasible**. Independent schedule validation: **PASS**.

Feasible assignment found; no optimization objective.

This is local feasibility validation, not a comparison experiment or a graduation audit.

## 1. Input specification

Maximum workload: **16 units**, no minimum.
Remaining normal semesters: [1, 2, 1, 2, 1, 2].
Completed record: CP3200, CS1101S, CS1231S, CS2030S, CS2040S, MA1521, MA1522, ST2334.
Read spec.json for the exact required, forbidden, fixed and group fields.

## 2. Compiled CSP

Read csp.md for the overview, csp.json for every variable and constraint, and model.pbtxt for the actual CP-SAT model.
The model has no course-count or semester-position objective.

## 3. Schedule

| Remaining position | Normal semester | Units / cap | Courses |
|---:|---:|---:|---|
| 1 | 1 | 4 / 16 | CS2100 |
| 2 | 2 | 4 / 16 | CS2102 |
| 3 | 1 | 16 / 16 | CS2101, CS2103T, CS2109S, CS2220 |
| 4 | 2 | 12 / 16 | CS3263, CS3264, CS4220 |
| 5 | 1 | 12 / 16 | CS3230, CS4278, CS5228 |
| 6 | 2 | 12 / 16 | CS2106, CS4246, CS4277 |

Course titles and credits are listed in schedule.csv. Completed courses are not repeated.

## 4. Independent checks

| Check family | Passed | Total |
|---|---:|---:|
| availability | 15 | 15 |
| corequisite | 1 | 1 |
| duplicate | 21 | 21 |
| eligibility | 15 | 15 |
| fixed_semester | 5 | 5 |
| forbidden | 15 | 15 |
| horizon | 1 | 1 |
| preclusion | 16 | 16 |
| prerequisite | 15 | 15 |
| required | 19 | 19 |
| requirement | 8 | 8 |
| workload | 6 | 6 |

### Programme group totals

| Group | Actual units | Actual courses | Unit bounds | Course bounds | Pass |
|---|---:|---:|---|---|---|
| breadth | 34 | 8 | 32 .. - | - .. - | True |
| breadth_upper | 20 | 5 | 12 .. - | - .. - | True |
| ai_primary | 16 | 4 | - .. - | 3 .. - | True |
| ai_upper | 4 | 1 | - .. - | 1 .. - | True |
| industry | 6 | 1 | 6 .. 12 | - .. - | True |
| cp_non_industry | 0 | 0 | - .. 12 | - .. - | True |
| programme_lower | 78 | 19 | 64 .. - | - .. - | True |

Each group's matched courses:

- breadth: CP3200, CS3263, CS3264, CS4220, CS4246, CS4277, CS4278, CS5228.
- breadth_upper: CS4220, CS4246, CS4277, CS4278, CS5228.
- ai_primary: CS2109S, CS3263, CS3264, CS4246.
- ai_upper: CS4246.
- industry: CP3200.
- cp_non_industry: (none).
- programme_lower: CP3200, CS1231S, CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2106, CS2109S, CS3230, CS3263, CS3264, CS4220, CS4246, CS4277, CS4278, MA1521, MA1522, ST2334.

### Violations

None. All checks passed.

validation.json contains individual pass/fail checks and group membership.
A non-feasible plan has no independently validated schedule; only CP-SAT can supply its infeasibility proof.

