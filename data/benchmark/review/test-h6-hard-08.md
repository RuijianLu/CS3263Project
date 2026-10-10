# test-h6-hard-08

Designed difficulty: hard; label: infeasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2030S, CS2040S, MA1521, MA1522. I have 6 remaining normal semesters, starting with Semester 1; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS3268, CS4246, CS4261, CS4277, CS5242, CS5260. Do not newly enroll in CS3264, CS4248, CS5228, CS5339. Take CS2103T in remaining semester number 1. Take CS2109S in remaining semester number 1. Take CS3230 in remaining semester number 1. Take CS5242 in remaining semester number 1. Take ST2334 in remaining semester number 2. Take CS4246 in remaining semester number 6. Take CS4277 in remaining semester number 6. Take CS5260 in remaining semester number 6. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 16 | CS1101S, CS1231S, MA1521, MA1522 |
| 2 | 2 | 8 | CS2030S, CS2040S |

## Infeasibility

The four explicit enrolments at position 1 use 16 units. Concurrent CS2101 is additionally forced by CS2103T, raising the necessary load to 20 > 16 units.

CP-SAT returned INFEASIBLE. The independent schedule checker does not certify infeasibility.
gold.jsonl also stores a checked feasible precursor; restoring its request removes the introduced conflict.

## Changes from the checked feasible precursor

| Field | Feasible precursor | Infeasible request |
|---|---|---|
| fixed | [{"course": "ST2334", "semester": 2}, {"course": "CS5242", "semester": 4}, {"course": "CS4246", "semester": 6}, {"course": "CS4277", "semester": 6}, {"course": "CS5260", "semester": 6}] | [{"course": "CS2103T", "semester": 1}, {"course": "CS2109S", "semester": 1}, {"course": "CS3230", "semester": 1}, {"course": "CS5242", "semester": 1}, {"course": "ST2334", "semester": 2}, {"course": "CS4246", "semester": 6}, {"course": "CS4277", "semester": 6}, {"course": "CS5260", "semester": 6}] |
