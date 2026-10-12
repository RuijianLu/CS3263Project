# Degree-planning evaluation

Run: csp16-evaluation-v1; split: test; model: gpt-6.1-sol; reasoning effort: medium.
Selected 120 of 120 cases; 0 cases were not selected.
Accuracy uses completed selected attempts. Execution/output failures count as unsuccessful attempts; pending and unselected cases are reported separately.

## Scoring policy

Policy: outcome-v1-explanation-secondary.
Primary correctness measures schedule validity against the original specification or agreement with a validated infeasible label. Explanation content is reviewed manually as a secondary finding and does not change this score; schema requirements still apply. An infeasibility explanation may identify any sufficient contradiction, rather than reproducing the annotated witness.
Translation canonical matches and semantic review are reported separately from outcome correctness. A field difference requires semantic review as equivalent, non-equivalent or unresolved; matching outcomes alone do not establish translation fidelity.

## Outcomes

| Approach | Completed / selected | Pending | Valid feasible plans | Correct infeasibility | False infeasibility | Overall correct / completed |
|---|---:|---:|---:|---:|---:|---:|
| direct | 120/120 | 0 | 83/84 | 36/36 | 1 | 119/120 |
| assisted | 120/120 | 0 | 84/84 | 36/36 | 0 | 120/120 |

Completed paired cases: 120; both correct: 119; direct only: 0; assisted only: 1; neither: 0.

## Horizon and designed difficulty

| Remaining semesters | Difficulty | Direct correct / completed | Assisted correct / completed | Pending attempts |
|---:|---|---:|---:|---:|
| 7 | easy | 10/10 | 10/10 | 0 |
| 7 | medium | 10/10 | 10/10 | 0 |
| 7 | hard | 10/10 | 10/10 | 0 |
| 6 | easy | 10/10 | 10/10 | 0 |
| 6 | medium | 10/10 | 10/10 | 0 |
| 6 | hard | 10/10 | 10/10 | 0 |
| 5 | easy | 10/10 | 10/10 | 0 |
| 5 | medium | 10/10 | 10/10 | 0 |
| 5 | hard | 10/10 | 10/10 | 0 |
| 4 | easy | 9/10 | 10/10 | 0 |
| 4 | medium | 10/10 | 10/10 | 0 |
| 4 | hard | 10/10 | 10/10 | 0 |

## Execution and answer status

| Approach | Execution statuses | Scored outcomes |
|---|---|---|
| direct | {"ok": 120} | {"correct_infeasibility": 36, "false_infeasibility": 1, "valid_plan": 83} |
| assisted | {"ok": 120} | {"correct_infeasibility": 36, "valid_plan": 84} |

## Runtime and reported usage

| Approach | Mean completed process + solver seconds | Reported input tokens | Reported output tokens |
|---|---:|---:|---:|
| direct | 22.41 | 2332737 | 62736 |
| assisted | 31.6 | 2359601 | 133277 |

## Translation audit

Canonical translations without differences: 115/120 schema-valid translations.
Correct outcomes with translation differences: 5.
Field and named-group differences are diagnostic mismatches, not proof of semantic inequivalence. Correct outcomes with differences require case-level review before being described as accidental correctness.

## Case-level results

| Case | Approach | Outcome | Violations | Translation differences |
|---|---|---|---|---|
| test-h7-easy-01 | direct | valid_plan | - | - |
| test-h7-easy-01 | assisted | valid_plan | - | - |
| test-h7-easy-02 | direct | valid_plan | - | - |
| test-h7-easy-02 | assisted | valid_plan | - | - |
| test-h7-easy-03 | direct | valid_plan | - | - |
| test-h7-easy-03 | assisted | valid_plan | - | - |
| test-h7-easy-04 | direct | valid_plan | - | - |
| test-h7-easy-04 | assisted | valid_plan | - | - |
| test-h7-easy-05 | direct | valid_plan | - | - |
| test-h7-easy-05 | assisted | valid_plan | - | - |
| test-h7-easy-06 | direct | valid_plan | - | - |
| test-h7-easy-06 | assisted | valid_plan | - | - |
| test-h7-easy-07 | direct | valid_plan | - | - |
| test-h7-easy-07 | assisted | valid_plan | - | - |
| test-h7-easy-08 | direct | correct_infeasibility | - | - |
| test-h7-easy-08 | assisted | correct_infeasibility | - | - |
| test-h7-easy-09 | direct | correct_infeasibility | - | - |
| test-h7-easy-09 | assisted | correct_infeasibility | - | - |
| test-h7-easy-10 | direct | correct_infeasibility | - | - |
| test-h7-easy-10 | assisted | correct_infeasibility | - | - |
| test-h7-medium-01 | direct | valid_plan | - | - |
| test-h7-medium-01 | assisted | valid_plan | - | - |
| test-h7-medium-02 | direct | valid_plan | - | - |
| test-h7-medium-02 | assisted | valid_plan | - | - |
| test-h7-medium-03 | direct | valid_plan | - | - |
| test-h7-medium-03 | assisted | valid_plan | - | - |
| test-h7-medium-04 | direct | valid_plan | - | - |
| test-h7-medium-04 | assisted | valid_plan | - | - |
| test-h7-medium-05 | direct | valid_plan | - | - |
| test-h7-medium-05 | assisted | valid_plan | - | - |
| test-h7-medium-06 | direct | valid_plan | - | - |
| test-h7-medium-06 | assisted | valid_plan | - | - |
| test-h7-medium-07 | direct | valid_plan | - | - |
| test-h7-medium-07 | assisted | valid_plan | - | - |
| test-h7-medium-08 | direct | correct_infeasibility | - | - |
| test-h7-medium-08 | assisted | correct_infeasibility | - | - |
| test-h7-medium-09 | direct | correct_infeasibility | - | - |
| test-h7-medium-09 | assisted | correct_infeasibility | - | - |
| test-h7-medium-10 | direct | correct_infeasibility | - | - |
| test-h7-medium-10 | assisted | correct_infeasibility | - | - |
| test-h7-hard-01 | direct | valid_plan | - | - |
| test-h7-hard-01 | assisted | valid_plan | - | - |
| test-h7-hard-02 | direct | valid_plan | - | - |
| test-h7-hard-02 | assisted | valid_plan | - | - |
| test-h7-hard-03 | direct | valid_plan | - | - |
| test-h7-hard-03 | assisted | valid_plan | - | - |
| test-h7-hard-04 | direct | valid_plan | - | - |
| test-h7-hard-04 | assisted | valid_plan | - | - |
| test-h7-hard-05 | direct | valid_plan | - | - |
| test-h7-hard-05 | assisted | valid_plan | - | - |
| test-h7-hard-06 | direct | valid_plan | - | - |
| test-h7-hard-06 | assisted | valid_plan | - | - |
| test-h7-hard-07 | direct | valid_plan | - | - |
| test-h7-hard-07 | assisted | valid_plan | - | - |
| test-h7-hard-08 | direct | correct_infeasibility | - | - |
| test-h7-hard-08 | assisted | correct_infeasibility | - | - |
| test-h7-hard-09 | direct | correct_infeasibility | - | - |
| test-h7-hard-09 | assisted | correct_infeasibility | - | - |
| test-h7-hard-10 | direct | correct_infeasibility | - | - |
| test-h7-hard-10 | assisted | correct_infeasibility | - | - |
| test-h6-easy-01 | direct | valid_plan | - | - |
| test-h6-easy-01 | assisted | valid_plan | - | - |
| test-h6-easy-02 | direct | valid_plan | - | - |
| test-h6-easy-02 | assisted | valid_plan | - | - |
| test-h6-easy-03 | direct | valid_plan | - | - |
| test-h6-easy-03 | assisted | valid_plan | - | - |
| test-h6-easy-04 | direct | valid_plan | - | - |
| test-h6-easy-04 | assisted | valid_plan | - | - |
| test-h6-easy-05 | direct | valid_plan | - | - |
| test-h6-easy-05 | assisted | valid_plan | - | - |
| test-h6-easy-06 | direct | valid_plan | - | - |
| test-h6-easy-06 | assisted | valid_plan | - | - |
| test-h6-easy-07 | direct | valid_plan | - | - |
| test-h6-easy-07 | assisted | valid_plan | - | group:required |
| test-h6-easy-08 | direct | correct_infeasibility | - | - |
| test-h6-easy-08 | assisted | correct_infeasibility | - | - |
| test-h6-easy-09 | direct | correct_infeasibility | - | - |
| test-h6-easy-09 | assisted | correct_infeasibility | - | - |
| test-h6-easy-10 | direct | correct_infeasibility | - | - |
| test-h6-easy-10 | assisted | correct_infeasibility | - | - |
| test-h6-medium-01 | direct | valid_plan | - | - |
| test-h6-medium-01 | assisted | valid_plan | - | - |
| test-h6-medium-02 | direct | valid_plan | - | - |
| test-h6-medium-02 | assisted | valid_plan | - | - |
| test-h6-medium-03 | direct | valid_plan | - | - |
| test-h6-medium-03 | assisted | valid_plan | - | - |
| test-h6-medium-04 | direct | valid_plan | - | - |
| test-h6-medium-04 | assisted | valid_plan | - | - |
| test-h6-medium-05 | direct | valid_plan | - | - |
| test-h6-medium-05 | assisted | valid_plan | - | - |
| test-h6-medium-06 | direct | valid_plan | - | - |
| test-h6-medium-06 | assisted | valid_plan | - | - |
| test-h6-medium-07 | direct | valid_plan | - | - |
| test-h6-medium-07 | assisted | valid_plan | - | - |
| test-h6-medium-08 | direct | correct_infeasibility | - | - |
| test-h6-medium-08 | assisted | correct_infeasibility | - | - |
| test-h6-medium-09 | direct | correct_infeasibility | - | - |
| test-h6-medium-09 | assisted | correct_infeasibility | - | - |
| test-h6-medium-10 | direct | correct_infeasibility | - | - |
| test-h6-medium-10 | assisted | correct_infeasibility | - | - |
| test-h6-hard-01 | direct | valid_plan | - | - |
| test-h6-hard-01 | assisted | valid_plan | - | - |
| test-h6-hard-02 | direct | valid_plan | - | - |
| test-h6-hard-02 | assisted | valid_plan | - | - |
| test-h6-hard-03 | direct | valid_plan | - | - |
| test-h6-hard-03 | assisted | valid_plan | - | - |
| test-h6-hard-04 | direct | valid_plan | - | - |
| test-h6-hard-04 | assisted | valid_plan | - | - |
| test-h6-hard-05 | direct | valid_plan | - | - |
| test-h6-hard-05 | assisted | valid_plan | - | - |
| test-h6-hard-06 | direct | valid_plan | - | - |
| test-h6-hard-06 | assisted | valid_plan | - | - |
| test-h6-hard-07 | direct | valid_plan | - | - |
| test-h6-hard-07 | assisted | valid_plan | - | - |
| test-h6-hard-08 | direct | correct_infeasibility | - | - |
| test-h6-hard-08 | assisted | correct_infeasibility | - | - |
| test-h6-hard-09 | direct | correct_infeasibility | - | - |
| test-h6-hard-09 | assisted | correct_infeasibility | - | - |
| test-h6-hard-10 | direct | correct_infeasibility | - | - |
| test-h6-hard-10 | assisted | correct_infeasibility | - | - |
| test-h5-easy-01 | direct | valid_plan | - | - |
| test-h5-easy-01 | assisted | valid_plan | - | - |
| test-h5-easy-02 | direct | valid_plan | - | - |
| test-h5-easy-02 | assisted | valid_plan | - | - |
| test-h5-easy-03 | direct | valid_plan | - | - |
| test-h5-easy-03 | assisted | valid_plan | - | - |
| test-h5-easy-04 | direct | valid_plan | - | - |
| test-h5-easy-04 | assisted | valid_plan | - | - |
| test-h5-easy-05 | direct | valid_plan | - | - |
| test-h5-easy-05 | assisted | valid_plan | - | - |
| test-h5-easy-06 | direct | valid_plan | - | - |
| test-h5-easy-06 | assisted | valid_plan | - | - |
| test-h5-easy-07 | direct | valid_plan | - | - |
| test-h5-easy-07 | assisted | valid_plan | - | - |
| test-h5-easy-08 | direct | correct_infeasibility | - | - |
| test-h5-easy-08 | assisted | correct_infeasibility | - | - |
| test-h5-easy-09 | direct | correct_infeasibility | - | - |
| test-h5-easy-09 | assisted | correct_infeasibility | - | - |
| test-h5-easy-10 | direct | correct_infeasibility | - | - |
| test-h5-easy-10 | assisted | correct_infeasibility | - | - |
| test-h5-medium-01 | direct | valid_plan | - | - |
| test-h5-medium-01 | assisted | valid_plan | - | - |
| test-h5-medium-02 | direct | valid_plan | - | - |
| test-h5-medium-02 | assisted | valid_plan | - | - |
| test-h5-medium-03 | direct | valid_plan | - | - |
| test-h5-medium-03 | assisted | valid_plan | - | - |
| test-h5-medium-04 | direct | valid_plan | - | - |
| test-h5-medium-04 | assisted | valid_plan | - | - |
| test-h5-medium-05 | direct | valid_plan | - | - |
| test-h5-medium-05 | assisted | valid_plan | - | - |
| test-h5-medium-06 | direct | valid_plan | - | - |
| test-h5-medium-06 | assisted | valid_plan | - | - |
| test-h5-medium-07 | direct | valid_plan | - | - |
| test-h5-medium-07 | assisted | valid_plan | - | - |
| test-h5-medium-08 | direct | correct_infeasibility | - | - |
| test-h5-medium-08 | assisted | correct_infeasibility | - | - |
| test-h5-medium-09 | direct | correct_infeasibility | - | - |
| test-h5-medium-09 | assisted | correct_infeasibility | - | - |
| test-h5-medium-10 | direct | correct_infeasibility | - | - |
| test-h5-medium-10 | assisted | correct_infeasibility | - | - |
| test-h5-hard-01 | direct | valid_plan | - | - |
| test-h5-hard-01 | assisted | valid_plan | - | - |
| test-h5-hard-02 | direct | valid_plan | - | - |
| test-h5-hard-02 | assisted | valid_plan | - | - |
| test-h5-hard-03 | direct | valid_plan | - | - |
| test-h5-hard-03 | assisted | valid_plan | - | - |
| test-h5-hard-04 | direct | valid_plan | - | - |
| test-h5-hard-04 | assisted | valid_plan | - | - |
| test-h5-hard-05 | direct | valid_plan | - | - |
| test-h5-hard-05 | assisted | valid_plan | - | - |
| test-h5-hard-06 | direct | valid_plan | - | - |
| test-h5-hard-06 | assisted | valid_plan | - | - |
| test-h5-hard-07 | direct | valid_plan | - | - |
| test-h5-hard-07 | assisted | valid_plan | - | - |
| test-h5-hard-08 | direct | correct_infeasibility | - | - |
| test-h5-hard-08 | assisted | correct_infeasibility | - | - |
| test-h5-hard-09 | direct | correct_infeasibility | - | - |
| test-h5-hard-09 | assisted | correct_infeasibility | - | - |
| test-h5-hard-10 | direct | correct_infeasibility | - | - |
| test-h5-hard-10 | assisted | correct_infeasibility | - | - |
| test-h4-easy-01 | direct | false_infeasibility | - | - |
| test-h4-easy-01 | assisted | valid_plan | - | - |
| test-h4-easy-02 | direct | valid_plan | - | - |
| test-h4-easy-02 | assisted | valid_plan | - | - |
| test-h4-easy-03 | direct | valid_plan | - | - |
| test-h4-easy-03 | assisted | valid_plan | - | forbidden |
| test-h4-easy-04 | direct | valid_plan | - | - |
| test-h4-easy-04 | assisted | valid_plan | - | - |
| test-h4-easy-05 | direct | valid_plan | - | - |
| test-h4-easy-05 | assisted | valid_plan | - | - |
| test-h4-easy-06 | direct | valid_plan | - | - |
| test-h4-easy-06 | assisted | valid_plan | - | - |
| test-h4-easy-07 | direct | valid_plan | - | - |
| test-h4-easy-07 | assisted | valid_plan | - | forbidden |
| test-h4-easy-08 | direct | correct_infeasibility | - | - |
| test-h4-easy-08 | assisted | correct_infeasibility | - | - |
| test-h4-easy-09 | direct | correct_infeasibility | - | - |
| test-h4-easy-09 | assisted | correct_infeasibility | - | - |
| test-h4-easy-10 | direct | correct_infeasibility | - | - |
| test-h4-easy-10 | assisted | correct_infeasibility | - | - |
| test-h4-medium-01 | direct | valid_plan | - | - |
| test-h4-medium-01 | assisted | valid_plan | - | - |
| test-h4-medium-02 | direct | valid_plan | - | - |
| test-h4-medium-02 | assisted | valid_plan | - | - |
| test-h4-medium-03 | direct | valid_plan | - | - |
| test-h4-medium-03 | assisted | valid_plan | - | - |
| test-h4-medium-04 | direct | valid_plan | - | - |
| test-h4-medium-04 | assisted | valid_plan | - | - |
| test-h4-medium-05 | direct | valid_plan | - | - |
| test-h4-medium-05 | assisted | valid_plan | - | - |
| test-h4-medium-06 | direct | valid_plan | - | - |
| test-h4-medium-06 | assisted | valid_plan | - | - |
| test-h4-medium-07 | direct | valid_plan | - | - |
| test-h4-medium-07 | assisted | valid_plan | - | - |
| test-h4-medium-08 | direct | correct_infeasibility | - | - |
| test-h4-medium-08 | assisted | correct_infeasibility | - | - |
| test-h4-medium-09 | direct | correct_infeasibility | - | - |
| test-h4-medium-09 | assisted | correct_infeasibility | - | - |
| test-h4-medium-10 | direct | correct_infeasibility | - | - |
| test-h4-medium-10 | assisted | correct_infeasibility | - | - |
| test-h4-hard-01 | direct | valid_plan | - | - |
| test-h4-hard-01 | assisted | valid_plan | - | required, group:required |
| test-h4-hard-02 | direct | valid_plan | - | - |
| test-h4-hard-02 | assisted | valid_plan | - | - |
| test-h4-hard-03 | direct | valid_plan | - | - |
| test-h4-hard-03 | assisted | valid_plan | - | - |
| test-h4-hard-04 | direct | valid_plan | - | - |
| test-h4-hard-04 | assisted | valid_plan | - | - |
| test-h4-hard-05 | direct | valid_plan | - | - |
| test-h4-hard-05 | assisted | valid_plan | - | - |
| test-h4-hard-06 | direct | valid_plan | - | - |
| test-h4-hard-06 | assisted | valid_plan | - | - |
| test-h4-hard-07 | direct | valid_plan | - | - |
| test-h4-hard-07 | assisted | valid_plan | - | - |
| test-h4-hard-08 | direct | correct_infeasibility | - | - |
| test-h4-hard-08 | assisted | correct_infeasibility | - | required |
| test-h4-hard-09 | direct | correct_infeasibility | - | - |
| test-h4-hard-09 | assisted | correct_infeasibility | - | - |
| test-h4-hard-10 | direct | correct_infeasibility | - | - |
| test-h4-hard-10 | assisted | correct_infeasibility | - | - |

## Interpretation and responsible AI

These correlated synthetic cases are controlled instances, not representative student samples. Difficulty labels are designed, not empirically calibrated. Fixed offerings, admission assumptions, a restricted catalogue and credited internship limit realism. No personal transcripts were used; outputs are not academic advice.
The solver checks a translated specification; feasible outputs are independently checked against the original specification. Correct infeasibility judgments and translation fidelity are separate findings. Raw responses are preserved without repairs or retries.
Team members must review source interpretations and record actual human and AI contributions. Reported subscription tokens are not converted into per-call dollar costs.

## Completed-run secondary audit

All 240 planned model attempts completed with execution status `ok`, one attempt per case and approach, and no tool invocations. The completion audit verified the 240 prompt hashes, all 426 original input files and their frozen copies, the protected documentation and pilot evidence, and the unchanged manifest and scoring policy. See [completion.json](completion.json).

The direct approach achieved 119/120 correct outcomes (99.17%); the assisted approach achieved 120/120 (100%). Both correctly classified all 36 infeasible cases. The direct approach produced 83/84 valid feasible plans; the assisted approach produced 84/84. The only discordant pair was `test-h4-easy-01`: the direct response treated completed CS1101S as a forced new enrolment and declared infeasibility. Under the frozen semantics, a required course may be satisfied by the completed record. The validated reference plan remains feasible; its independent check is preserved in [false_infeasibility_reference_check.json](false_infeasibility_reference_check.json).

Mean recorded process plus solver time was 22.41 seconds for direct planning and 31.60 seconds for assisted planning, a difference of 9.19 seconds (approximately 41% longer for assisted planning). These figures exclude orchestration and manual review time.

### Translation fidelity

The automatic comparison found 115/120 canonical matches. All five remaining translations were reviewed using their constraint semantics and classified as equivalent. The automated diagnostic fields above retain their original values; this secondary review is recorded separately in [manual_audit.json](manual_audit.json).

| Case | Difference | Equivalence evidence |
|---|---|---|
| test-h6-easy-07 | Added required-course group | All 14 members were already individually required; the group repeats these constraints. |
| test-h4-easy-03 | Added four forbidden courses | All four courses are non-selectable in the frozen catalogue, so new enrolment was already prohibited. Completed CP3200 credit remains counted. |
| test-h4-easy-07 | Added four forbidden courses | The same catalogue restriction makes all four additions redundant. |
| test-h4-hard-01 | Replaced individual required list with a group | The group contains exactly the original 19 required courses and requires all 19, counting completed and newly enrolled courses. |
| test-h4-hard-08 | Added CS4278 to required | The original fixed placement already forces new enrolment in CS4278 at position 1. |

These equivalence judgments use the actual constraints in both directions; shared solver outcomes alone were not taken as evidence of faithful translation.

### Explanation accuracy

A diagnostic numeric audit checked 453 matched claims across all 83 feasible direct responses. Manual inspection confirmed 17 incorrect numeric claims in 15 responses, covering AI focus-course counts, group-credit totals and a semester load. Each affected schedule still passed the independent checker. Under the frozen scoring policy, these explanation errors remain secondary and do not reduce the primary schedule score. Literal claims and independently computed evidence are preserved in [explanation_numeric_checks.json](explanation_numeric_checks.json).

For example, `test-h4-easy-04` claims eight AI primary courses and four AI upper courses, while the supplied plan and completed record contain seven and three respectively. In `test-h4-hard-02`, the explanation reports a final-semester load of 16 units, while the plan contains 12. The numeric parser covers explicit matched patterns and does not constitute an exhaustive audit of every prose claim. All 36 correctly labelled direct infeasibility explanations were read for a sufficient contradiction; explanations may identify an alternative sufficient cause under the frozen policy.

### Interpretation for the project report

The assisted approach achieved one additional correct outcome on this frozen benchmark, at greater recorded runtime. This single discordant pair does not establish a broad reliability advantage. Cases are correlated synthetic variants, and the designed difficulty labels are not empirically calibrated. Moreover, the translation prompt explicitly explains how completed mandatory courses satisfy requirements; the direct prompt prohibits re-enrolment but leaves the wording of requested inclusion less explicit. This prompt difference prevents attributing the observed false infeasibility solely to the absence of a solver.

The strongest supported findings are high primary correctness for both approaches, equivalent translations after case-level review, and a measurable distinction between valid schedules and reliable numerical explanations. A subsequent, separately named experiment could align the completed-credit guidance or explore harder constraint instances; these results and frozen inputs should remain intact.
