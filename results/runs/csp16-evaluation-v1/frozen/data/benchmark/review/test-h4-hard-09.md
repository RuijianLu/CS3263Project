# test-h4-hard-09

Designed difficulty: hard; label: infeasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2109S, CS3230, MA1521. I have 4 remaining normal semesters, starting with Semester 1; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS4243, CS5228, CS5242. Do not newly enroll in CS3243, CS3244, CS3263, CS3264, CS3268, CS4220, CS4246, CS4248, CS4261, CS4262, CS4277, CS4278, CS5260, CS5340. Take CS2106 in remaining semester number 1. Take CS4243 in remaining semester number 2. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 8 | CS1101S, CS1231S |
| 2 | 2 | 12 | CS2030S, CS2040S, MA1521 |
| 3 | 1 | 4 | CS2100 |
| 4 | 2 | 16 | CS2101, CS2103T, CS2109S, CS3230 |

## Infeasibility

Available members of programme_lower provide at most 62 units, below its 64-unit minimum. Level-5000 electives cannot close this lower-level deficit.

CP-SAT returned INFEASIBLE. The independent schedule checker does not certify infeasibility.
gold.jsonl also stores a checked feasible precursor; restoring its request removes the introduced conflict.

## Changes from the checked feasible precursor

| Field | Feasible precursor | Infeasible request |
|---|---|---|
| required | ["CS1101S", "CS1231S", "CS2030S", "CS2040S", "CS2100", "CS2101", "CS2103T", "CS2106", "CS2109S", "CS3230", "CS3268", "CS4243", "CS4246", "CS4262", "CS5228", "CS5242", "MA1521", "MA1522", "ST2334"] | ["CS1101S", "CS1231S", "CS2030S", "CS2040S", "CS2100", "CS2101", "CS2103T", "CS2106", "CS2109S", "CS3230", "CS4243", "CS5228", "CS5242", "MA1521", "MA1522", "ST2334"] |
| forbidden | ["CS4248", "CS4277", "CS5260", "CS5340"] | ["CS3243", "CS3244", "CS3263", "CS3264", "CS3268", "CS4220", "CS4246", "CS4248", "CS4261", "CS4262", "CS4277", "CS4278", "CS5260", "CS5340"] |
| fixed | [{"course": "CS2106", "semester": 1}, {"course": "CS4243", "semester": 2}, {"course": "CS3268", "semester": 3}, {"course": "CS4246", "semester": 4}, {"course": "CS4262", "semester": 4}] | [{"course": "CS2106", "semester": 1}, {"course": "CS4243", "semester": 2}] |
