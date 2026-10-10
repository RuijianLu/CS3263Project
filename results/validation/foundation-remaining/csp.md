# Compiled CSP inspection

- Workload cap: 16 units per normal semester.
- Remaining normal semesters: [1, 2, 1, 2, 1, 2, 1, 2].
- Objective: none; find any satisfying assignment.
- Variables: 2448.
- Constraints: 3967.

All decision and logical auxiliary variables have domain {0,1}. Backend constants have singleton domains.
Semester suffixes are remaining positions (1-based), not normal Semester 1/2.
csp.json lists every variable/domain and constraint description; backend_index points into model.pbtxt.

| Constraint family | Number |
|---|---:|
| before_link | 496 |
| eligibility | 8 |
| no_retake | 87 |
| offering | 120 |
| paired_enrolment | 8 |
| preclusion | 101 |
| prerequisite | 696 |
| prerequisite_logic | 2336 |
| programme_group | 8 |
| required | 12 |
| selection_link | 87 |
| workload | 8 |

## Mandatory new enrolments

CS2030S, CS2040S, CS2100, CS2101, CS2103T, CS2106, CS2109S, CS3230, ST2334

## Requirement groups

| Group | Minimum units | Maximum units | Minimum courses | Maximum courses |
|---|---:|---:|---:|---:|
| breadth | 32 | - | - | - |
| breadth_upper | 12 | - | - | - |
| ai_primary | - | - | 3 | - |
| ai_upper | - | - | 1 | - |
| industry | 6 | 12 | - | - |
| cp_non_industry | - | 12 | - | - |
| programme_lower | 64 | - | - | - |

## Fixed new enrolments

None.
