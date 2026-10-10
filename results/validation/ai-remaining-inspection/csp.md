# Compiled CSP inspection

- Workload cap: 16 units per normal semester.
- Remaining normal semesters: [1, 2, 1, 2].
- Objective: none; find any satisfying assignment.
- Variables: 1248.
- Constraints: 2127.

All decision and logical auxiliary variables have domain {0,1}. Backend constants have singleton domains.
Semester suffixes are remaining positions (1-based), not normal Semester 1/2.
csp.json lists every variable/domain and constraint description; backend_index points into model.pbtxt.

| Constraint family | Number |
|---|---:|
| before_link | 228 |
| eligibility | 16 |
| fixed_semester | 2 |
| no_retake | 87 |
| offering | 60 |
| paired_enrolment | 4 |
| preclusion | 101 |
| prerequisite | 348 |
| prerequisite_logic | 1168 |
| programme_group | 8 |
| required | 14 |
| selection_link | 87 |
| workload | 4 |

## Mandatory new enrolments

CS2106, CS3263, CS4246

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

- CS3263: remaining position 1.
- CS4246: remaining position 2.
