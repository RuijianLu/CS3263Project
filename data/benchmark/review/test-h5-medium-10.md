# test-h5-medium-10

Designed difficulty: medium; label: infeasible.

## Natural-language request

I am a standard single-degree NUS Computer Science student under the AY2026/27 admission rules, pursuing the Artificial Intelligence focus area. Plan my remaining Programme Requirements only. I have passed CP3200, CS1101S, CS1231S, CS2030S, CS2040S, CS2100, CS2106, MA1521, MA1522. I have 5 remaining normal semesters, starting with Semester 2; Semester 1 and Semester 2 alternate. The maximum is 16 units per semester with no minimum. Use the supplied snapshot's recurring offerings. All qualifying mathematics and English admission conditions are met. Do not audit Common Curriculum or Unrestricted Electives. For this simplified academic-planning task, CP3200 is separately credited as 6 industry-experience units; internship eligibility is not simulated. My plan must include CS1101S, CS3263, CS4243, CS4246, CS5242. Do not newly enroll in CS4220, CS5339. Take CS4243 in remaining semester number 3. Take CS3263 in remaining semester number 4. Take CS4246 in remaining semester number 4. Take CS5242 in remaining semester number 5. Give a feasible plan satisfying every requirement, or identify that the request is impossible.

## Checked academic history

CP3200 is a separate credited internship exception.

| Past position | Normal semester | Units | Courses |
|---:|---:|---:|---|
| 1 | 1 | 16 | CS1101S, CS1231S, MA1521, MA1522 |
| 2 | 2 | 12 | CS2030S, CS2040S, CS2100 |
| 3 | 1 | 4 | CS2106 |

## Infeasibility

CS4246 needs earlier CS3263 or CS3243. CS3263 is fixed concurrently, while CS3243 is excluded by mandatory CS2109S; neither alternative is completed.

CP-SAT returned INFEASIBLE. The independent schedule checker does not certify infeasibility.
gold.jsonl also stores a checked feasible precursor; restoring its request removes the introduced conflict.

## Changes from the checked feasible precursor

| Field | Feasible precursor | Infeasible request |
|---|---|---|
| required | ["CS1101S", "CS1231S", "CS2030S", "CS2040S", "CS2100", "CS2101", "CS2103T", "CS2106", "CS2109S", "CS3230", "CS3263", "CS4243", "CS5242", "MA1521", "MA1522", "ST2334"] | ["CS1101S", "CS1231S", "CS2030S", "CS2040S", "CS2100", "CS2101", "CS2103T", "CS2106", "CS2109S", "CS3230", "CS3263", "CS4243", "CS4246", "CS5242", "MA1521", "MA1522", "ST2334"] |
| fixed | [{"course": "CS4243", "semester": 3}, {"course": "CS5242", "semester": 5}] | [{"course": "CS4243", "semester": 3}, {"course": "CS3263", "semester": 4}, {"course": "CS4246", "semester": 4}, {"course": "CS5242", "semester": 5}] |
