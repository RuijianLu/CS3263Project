# Initial experiment interpretation and translation review

The frozen evaluation contains 24 synthetic cases, including 18 feasible and six infeasible cases. Both direct planning and translation followed by CP-SAT achieved 24/24 correct outcomes. Mean elapsed process-plus-solver time was 19.49 seconds for direct planning and 33.56 seconds for the assisted approach. The development pilot also achieved 6/6 for each approach.

These observations establish successful execution on this benchmark, but provide no evidence of an accuracy advantage for either approach. The assisted approach took approximately 1.72 times as long in this run. Single attempts, a small benchmark, related scenario constructions and subscription runtime variation prevent a general performance claim. More varied cases would be needed to expose differences.

## Canonical translation differences

The automated comparison found identical canonical fields in 19/24 evaluation translations. Inspection of the remaining five found only additional constraints already implied by the fixed catalogue or the original specification.

| Case | Additional required courses | Additional forbidden courses |
|---|---|---|
| test-easy-06 | CS3263, CS4246 | None |
| test-medium-06 | CS3263, CS4246 | None |
| test-hard-06 | CS3263, CS4246 | CS2040HS, EE2028, EE2211, CP3200 |
| test-easy-07 | CS3268 | None |
| test-easy-08 | CS3263, CS4246 | CS2040HS, EE2028, EE2211, CP3200 |

Every additional required course was already constrained to a specific semester by the unchanged fixed-course field. Requiring it separately does not alter the feasible set. Every additional forbidden course has selectable=false in the frozen catalogue, so the solver already prohibits its new enrolment. CP3200 is also completed in the affected profiles. The forbidden field applies only to new enrolment; completed internship credit remains available.

No courses were removed from required, and no other fields differed in these five cases. Their added constraints are therefore redundant within this model. The 19/24 canonical-match count should not be described as five translation errors. This targeted inspection is not a general semantic-equivalence procedure.

## Evidence and review status

Responses, prompts, event logs and execution records remain unchanged under results/runs/initial/. The automated outcome table is in analysis.md; case-level diagnostics are in summary.csv. All 48 evaluation attempts completed successfully, with no model tool calls detected. The 12 development attempts also completed successfully.

This interpretation and source audit were supported by Codex. Student-team review of programme rules, simplified assumptions and benchmark labels remains necessary before academic submission. The results concern remaining Programme Requirements in the agreed scope, not full degree completion or authoritative academic advice.
