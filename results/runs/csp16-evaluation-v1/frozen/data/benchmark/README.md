# 16-unit study-stage benchmark

24 development cases and 120 evaluation cases. No language-model calls were made.

Each of the 12 horizon/difficulty cells contains 1 feasible + 1 infeasible development case, and 7 feasible + 3 infeasible evaluation cases.
Difficulty is designed, not empirically calibrated; compare levels within a horizon. Negative-case proof difficulty can differ from its surrounding request.

## Study stages

| Remaining | Past semesters | Completed academic course range |
|---:|---:|---:|
| 7 | 1 | 2-4 |
| 6 | 2 | 5-7 |
| 5 | 3 | 8-9 |
| 4 | 4 | 10-12 |

## Construction and review

Histories contain prerequisite-valid academic semester schedules with at most 16 units. Some early histories leave CS1101S outstanding, exercising the full introductory programming chain; later progress varies. CP3200 is credited separately under the retained internship simplification.
Completed-course sets are disjoint between development and evaluation. Histories recur within a split to support controlled comparisons; cases are correlated synthetic instances, not independent student samples or template-disjoint tests.
Easy feasible cases request one elective without fixed/forbidden additions; medium requests three electives plus two fixed positions and two forbidden alternatives; hard requests six electives plus five fixed positions and four forbidden alternatives. Prerequisites, offerings, course facts, programme bounds and the 16-unit cap stay fixed.
Feasible references pass the independent checker. Every infeasible request is solver-proven and includes a concrete contradiction and a checked feasible precursor. Timeouts are not labelled infeasible.
Reference schedules are any satisfying assignments, not minimal or optimal plans. Extra permissible courses can appear.

Validation: 144 unique requests, 96 feasible and 48 infeasible; zero overlapping completed-course sets between splits.
Distinct used histories: development 8, evaluation 70.

- index.csv: case counts, workload measures, history identifiers and contradiction mechanisms.
- review/CASE_ID.md: request, checked past history and readable reference result.
- cases/CASE_ID.json: specification usable with solve/check. Copy it before editing; these convenience exports do not change the scored JSONL requests or gold records.
- gold.jsonl: labels, full reference plans/checks, histories and negative-case precursors. Keep it out of model prompts.
- validation.json and manifest.json: local audit and frozen source/input hashes.

To inspect a single case, run `python -m degree_planner solve data/benchmark/cases/CASE_ID.json`. Output goes to results/validation/CASE_ID. Infeasible cases have no validated schedule, so solve exits unsuccessfully while retaining its proof status and artifacts.

The old 32-unit inputs and results remain under results/historical/32-unit-inputs and results/pilot, results/initial, results/runs. This benchmark has not yet been evaluated by a language model.
