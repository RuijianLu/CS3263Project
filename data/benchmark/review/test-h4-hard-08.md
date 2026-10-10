# test-h4-hard-08

Designed difficulty: hard; label: infeasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2030S, CS2040S, CS2100, CS2109S, CS3230, MA1521, MA1522, ST2334. I have 4 remaining normal semesters, starting with Semester 1; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS3263, CS3264, CS4220, CS4246, CS4248, CS4277. Do not newly enroll in CS4243, CS4262, CS5228, CS5340. Take CS2103T in remaining semester number 1. Take CS3263 in remaining semester number 1. Take CS4246 in remaining semester number 1. Take CS4278 in remaining semester number 1. Take CS2106 in remaining semester number 4. Take CS3264 in remaining semester number 4. Take CS4220 in remaining semester number 4. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 8 | MA1521, MA1522 |
| 2 | 2 | 12 | CS1101S, CS1231S, ST2334 |
| 3 | 1 | 4 | CS2040S |
| 4 | 2 | 16 | CS2030S, CS2100, CS2109S, CS3230 |

## Infeasibility

The four explicit enrolments at position 1 use 16 units. Concurrent CS2101 is additionally forced by CS2103T, raising the necessary load to 20 > 16 units.

CP-SAT returned INFEASIBLE. The independent schedule checker does not certify infeasibility.
gold.jsonl also stores a checked feasible precursor; restoring its request removes the introduced conflict.

## Changes from the checked feasible precursor

| Field | Feasible precursor | Infeasible request |
|---|---|---|
| fixed | [{"course": "CS2101", "semester": 1}, {"course": "CS2103T", "semester": 1}, {"course": "CS2106", "semester": 4}, {"course": "CS3264", "semester": 4}, {"course": "CS4220", "semester": 4}] | [{"course": "CS2103T", "semester": 1}, {"course": "CS3263", "semester": 1}, {"course": "CS4246", "semester": 1}, {"course": "CS4278", "semester": 1}, {"course": "CS2106", "semester": 4}, {"course": "CS3264", "semester": 4}, {"course": "CS4220", "semester": 4}] |
