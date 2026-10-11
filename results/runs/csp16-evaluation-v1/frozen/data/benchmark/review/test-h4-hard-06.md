# test-h4-hard-06

Designed difficulty: hard; label: feasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2106, CS2109S, MA1521. I have 4 remaining normal semesters, starting with Semester 1; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS3268, CS4243, CS4248, CS5228, CS5242, CS5340. Do not newly enroll in CS4246, CS4262, CS4278, CS5260. Take CS3230 in remaining semester number 1. Take CS4248 in remaining semester number 2. Take CS5242 in remaining semester number 2. Take CS3268 in remaining semester number 3. Take CS4243 in remaining semester number 3. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 12 | CS1101S, CS1231S, MA1521 |
| 2 | 2 | 12 | CS2030S, CS2040S, CS2100 |
| 3 | 1 | 4 | CS2106 |
| 4 | 2 | 12 | CS2101, CS2103T, CS2109S |

# Local CSP solution and validation

Solver status: **feasible**. Independent schedule validation: **PASS**.

Feasible assignment found; no optimization objective.

This is local feasibility validation, not a comparison experiment or a graduation audit.

## 1. Input specification

Maximum workload: **16 units**, no minimum.
Remaining normal semesters: [1, 2, 1, 2].
Completed record: CP3200, CS1101S, CS1231S, CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2106, CS2109S, MA1521.
Read spec.json for the exact required, forbidden, fixed and group fields.

## 2. Compiled CSP

Read csp.md for the overview, csp.json for every variable and constraint, and model.pbtxt for the actual CP-SAT model.
The model has no course-count or semester-position objective.

## 3. Schedule

| Remaining position | Normal semester | Units / cap | Courses |
|---:|---:|---:|---|
| 1 | 1 | 12 / 16 | CS3230, MA1522, ST2334 |
| 2 | 2 | 8 / 16 | CS4248, CS5242 |
| 3 | 1 | 16 / 16 | CS2102, CS3263, CS3268, CS4243 |
| 4 | 2 | 8 / 16 | CS5228, CS5340 |

Course titles and credits are listed in schedule.csv. Completed courses are not repeated.

## 4. Independent checks

| Check family | Passed | Total |
|---|---:|---:|
| availability | 11 | 11 |
| duplicate | 15 | 15 |
| eligibility | 11 | 11 |
| fixed_semester | 5 | 5 |
| forbidden | 11 | 11 |
| horizon | 1 | 1 |
| preclusion | 9 | 9 |
| prerequisite | 11 | 11 |
| required | 19 | 19 |
| requirement | 8 | 8 |
| workload | 4 | 4 |

### Programme group totals

| Group | Actual units | Actual courses | Unit bounds | Course bounds | Pass |
|---|---:|---:|---|---|---|
| breadth | 34 | 8 | 32 .. - | - .. - | True |
| breadth_upper | 20 | 5 | 12 .. - | - .. - | True |
| ai_primary | 20 | 5 | - .. - | 3 .. - | True |
| ai_upper | 8 | 2 | - .. - | 1 .. - | True |
| industry | 6 | 1 | 6 .. 12 | - .. - | True |
| cp_non_industry | 0 | 0 | - .. 12 | - .. - | True |
| programme_lower | 70 | 17 | 64 .. - | - .. - | True |

Each group's matched courses:

- breadth: CP3200, CS3263, CS3268, CS4243, CS4248, CS5228, CS5242, CS5340.
- breadth_upper: CS4243, CS4248, CS5228, CS5242, CS5340.
- ai_primary: CS2109S, CS3263, CS3268, CS4243, CS4248.
- ai_upper: CS4243, CS4248.
- industry: CP3200.
- cp_non_industry: (none).
- programme_lower: CP3200, CS1231S, CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2106, CS2109S, CS3230, CS3263, CS3268, CS4243, CS4248, MA1521, MA1522, ST2334.

### Violations

None. All checks passed.

validation.json contains individual pass/fail checks and group membership.
A non-feasible plan has no independently validated schedule; only CP-SAT can supply its infeasibility proof.

