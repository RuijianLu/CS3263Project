# Degree-planning development evaluation

Run: csp16-pilot; split: dev; model: gpt-6.1-sol; reasoning effort: medium.
Selected 12 of 24 cases; 12 cases were not selected.
Accuracy uses completed selected attempts. Execution/output failures count as unsuccessful attempts; pending and unselected cases are reported separately.

## Outcomes

| Approach | Completed / selected | Pending | Valid feasible plans | Correct infeasibility | False infeasibility | Overall correct / completed |
|---|---:|---:|---:|---:|---:|---:|
| direct | 12/12 | 0 | 6/6 | 6/6 | 0 | 12/12 |
| assisted | 12/12 | 0 | 6/6 | 6/6 | 0 | 12/12 |

Completed paired cases: 12; both correct: 12; direct only: 0; assisted only: 0; neither: 0.

## Horizon and designed difficulty

| Remaining semesters | Difficulty | Direct correct / completed | Assisted correct / completed | Pending attempts |
|---:|---|---:|---:|---:|
| 7 | easy | 1/1 | 1/1 | 0 |
| 7 | medium | 1/1 | 1/1 | 0 |
| 7 | hard | 1/1 | 1/1 | 0 |
| 6 | easy | 1/1 | 1/1 | 0 |
| 6 | medium | 1/1 | 1/1 | 0 |
| 6 | hard | 1/1 | 1/1 | 0 |
| 5 | easy | 1/1 | 1/1 | 0 |
| 5 | medium | 1/1 | 1/1 | 0 |
| 5 | hard | 1/1 | 1/1 | 0 |
| 4 | easy | 1/1 | 1/1 | 0 |
| 4 | medium | 1/1 | 1/1 | 0 |
| 4 | hard | 1/1 | 1/1 | 0 |

## Execution and answer status

| Approach | Execution statuses | Scored outcomes |
|---|---|---|
| direct | {"ok": 12} | {"correct_infeasibility": 6, "valid_plan": 6} |
| assisted | {"ok": 12} | {"correct_infeasibility": 6, "valid_plan": 6} |

## Runtime and reported usage

| Approach | Mean completed process + solver seconds | Reported input tokens | Reported output tokens |
|---|---:|---:|---:|
| direct | 13.72 | 233280 | 5279 |
| assisted | 21.27 | 235966 | 13567 |

## Translation audit

Canonical translations without differences: 11/12 schema-valid translations.
Correct outcomes with translation differences: 1.
Field and named-group differences are diagnostic mismatches, not proof of semantic inequivalence. Correct outcomes with differences require case-level review before being described as accidental correctness.

## Case-level results

| Case | Approach | Outcome | Violations | Translation differences |
|---|---|---|---|---|
| dev-h7-easy-01 | direct | valid_plan | - | - |
| dev-h7-easy-01 | assisted | valid_plan | - | - |
| dev-h7-medium-02 | direct | correct_infeasibility | - | - |
| dev-h7-medium-02 | assisted | correct_infeasibility | - | - |
| dev-h7-hard-01 | direct | valid_plan | - | - |
| dev-h7-hard-01 | assisted | valid_plan | - | - |
| dev-h6-easy-02 | direct | correct_infeasibility | - | - |
| dev-h6-easy-02 | assisted | correct_infeasibility | - | - |
| dev-h6-medium-01 | direct | valid_plan | - | - |
| dev-h6-medium-01 | assisted | valid_plan | - | - |
| dev-h6-hard-02 | direct | correct_infeasibility | - | - |
| dev-h6-hard-02 | assisted | correct_infeasibility | - | required |
| dev-h5-easy-01 | direct | valid_plan | - | - |
| dev-h5-easy-01 | assisted | valid_plan | - | - |
| dev-h5-medium-02 | direct | correct_infeasibility | - | - |
| dev-h5-medium-02 | assisted | correct_infeasibility | - | - |
| dev-h5-hard-01 | direct | valid_plan | - | - |
| dev-h5-hard-01 | assisted | valid_plan | - | - |
| dev-h4-easy-02 | direct | correct_infeasibility | - | - |
| dev-h4-easy-02 | assisted | correct_infeasibility | - | - |
| dev-h4-medium-01 | direct | valid_plan | - | - |
| dev-h4-medium-01 | assisted | valid_plan | - | - |
| dev-h4-hard-02 | direct | correct_infeasibility | - | - |
| dev-h4-hard-02 | assisted | correct_infeasibility | - | - |

## Interpretation and responsible AI

These correlated synthetic cases are controlled instances, not representative student samples. Difficulty labels are designed, not empirically calibrated. Fixed offerings, admission assumptions, a restricted catalogue and credited internship limit realism. No personal transcripts were used; outputs are not academic advice.
The solver checks a translated specification; feasible outputs are independently checked against the original specification. Correct infeasibility judgments and translation fidelity are separate findings. Raw responses are preserved without repairs or retries.
Team members must review source interpretations and record actual human and AI contributions. Reported subscription tokens are not converted into per-call dollar costs.
