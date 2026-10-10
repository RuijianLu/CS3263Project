# test-h5-hard-08

Designed difficulty: hard; label: infeasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2030S, CS2040S, CS2100, CS2106, MA1521, MA1522. I have 5 remaining normal semesters, starting with Semester 2; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS3264, CS4220, CS4248, CS4277, CS5260, CS5340. Do not newly enroll in CS3268, CS4243, CS4246, CS5339. Take CS2103T in remaining semester number 3. Take CS2109S in remaining semester number 3. Take CS3230 in remaining semester number 3. Take CS4220 in remaining semester number 3. Take CS3264 in remaining semester number 4. Take CS4277 in remaining semester number 5. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 16 | CS1101S, CS1231S, MA1521, MA1522 |
| 2 | 2 | 12 | CS2030S, CS2040S, CS2100 |
| 3 | 1 | 4 | CS2106 |

## Infeasibility

The four explicit enrolments at position 3 use 16 units. Concurrent CS2101 is additionally forced by CS2103T, raising the necessary load to 20 > 16 units.

CP-SAT returned INFEASIBLE. The independent schedule checker does not certify infeasibility.
gold.jsonl also stores a checked feasible precursor; restoring its request removes the introduced conflict.

## Changes from the checked feasible precursor

| Field | Feasible precursor | Infeasible request |
|---|---|---|
| fixed | [{"course": "CS2101", "semester": 3}, {"course": "CS2103T", "semester": 3}, {"course": "CS3264", "semester": 4}, {"course": "CS4220", "semester": 5}, {"course": "CS4277", "semester": 5}] | [{"course": "CS2103T", "semester": 3}, {"course": "CS2109S", "semester": 3}, {"course": "CS3230", "semester": 3}, {"course": "CS4220", "semester": 3}, {"course": "CS3264", "semester": 4}, {"course": "CS4277", "semester": 5}] |
