# test-h5-hard-09

Designed difficulty: hard; label: infeasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2040S, CS2100, CS2106, MA1521, MA1522, ST2334. I have 5 remaining normal semesters, starting with Semester 2; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS5260, CS5340. Do not newly enroll in CS3243, CS3244, CS3263, CS3264, CS3268, CS4220, CS4243, CS4246, CS4248, CS4261, CS4262, CS4277, CS4278, CS5228. Take CS3230 in remaining semester number 1. Take CS5340 in remaining semester number 3. Take CS5260 in remaining semester number 5. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 16 | CS1101S, CS1231S, MA1521, MA1522 |
| 2 | 2 | 12 | CS2040S, CS2100, ST2334 |
| 3 | 1 | 4 | CS2106 |

## Infeasibility

Available members of programme_lower provide at most 58 units, below its 64-unit minimum. Level-5000 electives cannot close this lower-level deficit.

CP-SAT returned INFEASIBLE. The independent schedule checker does not certify infeasibility.
gold.jsonl also stores a checked feasible precursor; restoring its request removes the introduced conflict.

## Changes from the checked feasible precursor

| Field | Feasible precursor | Infeasible request |
|---|---|---|
| required | ["CS1101S", "CS1231S", "CS2030S", "CS2040S", "CS2100", "CS2101", "CS2103T", "CS2106", "CS2109S", "CS3230", "CS3264", "CS3268", "CS4262", "CS4278", "CS5260", "CS5340", "MA1521", "MA1522", "ST2334"] | ["CS1101S", "CS1231S", "CS2030S", "CS2040S", "CS2100", "CS2101", "CS2103T", "CS2106", "CS2109S", "CS3230", "CS5260", "CS5340", "MA1521", "MA1522", "ST2334"] |
| forbidden | ["CS4243", "CS4246", "CS4248", "CS5228"] | ["CS3243", "CS3244", "CS3263", "CS3264", "CS3268", "CS4220", "CS4243", "CS4246", "CS4248", "CS4261", "CS4262", "CS4277", "CS4278", "CS5228"] |
| fixed | [{"course": "CS3230", "semester": 1}, {"course": "CS5340", "semester": 3}, {"course": "CS4278", "semester": 4}, {"course": "CS4262", "semester": 5}, {"course": "CS5260", "semester": 5}] | [{"course": "CS3230", "semester": 1}, {"course": "CS5340", "semester": 3}, {"course": "CS5260", "semester": 5}] |
