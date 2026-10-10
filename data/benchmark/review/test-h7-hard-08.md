# test-h7-hard-08

Designed difficulty: hard; label: infeasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1231S, MA1521. I have 7 remaining normal semesters, starting with Semester 2; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS3263, CS3264, CS3268, CS4277, CS5260, CS5339. Do not newly enroll in CS4220, CS4248, CS4278, CS5340. Take CS2109S in remaining semester number 3. Take CS2030S in remaining semester number 5. Take CS4277 in remaining semester number 5. Take CS2103T in remaining semester number 6. Take CS2106 in remaining semester number 6. Take CS3230 in remaining semester number 6. Take MA1522 in remaining semester number 6. Take CS5339 in remaining semester number 7. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 8 | CS1231S, MA1521 |

## Infeasibility

The four explicit enrolments at position 6 use 16 units. Concurrent CS2101 is additionally forced by CS2103T, raising the necessary load to 20 > 16 units.

CP-SAT returned INFEASIBLE. The independent schedule checker does not certify infeasibility.
gold.jsonl also stores a checked feasible precursor; restoring its request removes the introduced conflict.

## Changes from the checked feasible precursor

| Field | Feasible precursor | Infeasible request |
|---|---|---|
| fixed | [{"course": "CS2109S", "semester": 3}, {"course": "CS2030S", "semester": 5}, {"course": "CS2106", "semester": 5}, {"course": "CS4277", "semester": 5}, {"course": "CS5339", "semester": 7}] | [{"course": "CS2109S", "semester": 3}, {"course": "CS2030S", "semester": 5}, {"course": "CS4277", "semester": 5}, {"course": "CS2103T", "semester": 6}, {"course": "CS2106", "semester": 6}, {"course": "CS3230", "semester": 6}, {"course": "MA1522", "semester": 6}, {"course": "CS5339", "semester": 7}] |
