# Development pilot comparison and inspection

The development pilot compared direct model planning with model translation followed by CP-SAT on the first 12 development cases. Both approaches answered all 12 cases correctly under the frozen 16-unit feasibility model. Direct planning had lower mean elapsed time in this run. Inspection found two direct explanations with incorrect AI course counts, although their schedules were valid, and one canonical translation difference that was a redundant requirement.

## Experimental protocol

The pilot ran on 11 October 2026 in the client timezone using gpt-6.1-sol at medium reasoning effort through the authenticated Codex subscription. Each approach received the same course facts and case request in a fresh session. Tools were disabled and audited. The process timeout was 180 seconds and the solver limit was 10 seconds. Each approach made one attempt per case; raw responses were retained without repair or retry.

The selected cases cover four remaining-semester horizons and three designed difficulty levels, with six feasible and six infeasible cases. The other 12 development cases were not selected. The 120 evaluation cases were not run. The run manifest freezes the selected case IDs, configuration, prompts, schemas, relevant implementation files and dataset hashes.

## Results

| Approach | Valid feasible plans | Correct infeasibility | Overall correct | Mean process and solver time | Reported output tokens |
|---|---:|---:|---:|---:|---:|
| Direct planning | 6/6 | 6/6 | 12/12 | 13.72 seconds | 5,279 |
| Translation and solver | 6/6 | 6/6 | 12/12 | 21.27 seconds | 13,567 |

All 24 model processes completed successfully, and all responses passed the applicable output schema. No timeout, unknown answer, invalid plan, false infeasibility judgment, execution failure or tool-use violation occurred. Both approaches were correct in every selected horizon and difficulty cell. All 23 implementation tests passed before execution.

Reported input usage was 233,280 tokens for direct planning and 235,966 for translation. The translation response format requires explicit group membership and bounds, so the runtime comparison includes different output formats as well as planning or translation work. These subscription token counts do not establish monetary costs.

See [generated analysis](analysis.md), [case-level scores](summary.csv), [metrics](metrics.json) and the [frozen run manifest](../runs/csp16-pilot/manifest.json).

## Inspection of successful outputs

Both approaches solved dev-h7-hard-01, whose history leaves CS1101S unfinished. The direct schedule follows the selected chain CS1101S in remaining position 1, CS2040S in position 2, CS2109S in position 3, CS3263 in position 4 and CS4246 in position 7. It satisfies all five fixed placements and takes CS2101 and CS2103T concurrently. The independent checker also verified workload, offerings, preclusions and programme groups.

Eleven of the 12 assisted translations match the canonical reference fields. In dev-h6-hard-02, the model adds LSM1301 to the required list, while preserving its fixed enrolment at position 5. That fixed constraint already forces LSM1301 to be newly enrolled. Adding the required entry is therefore redundant and preserves the request. The canonical mismatch is not evidence of an unfaithful translation or accidental correctness. This result illustrates why field differences require semantic inspection. Evidence: [reference specification](../../data/benchmark/cases/dev-h6-hard-02.json), [translation](../runs/csp16-pilot/dev-h6-hard-02-assisted/response.json) and [canonical audit](../runs/csp16-pilot/dev-h6-hard-02-assisted/translation_audit.json).

Two of the six feasible direct responses contain incorrect numerical claims in their explanations:

| Case | Claim in the model explanation | Independent count | Effect on scored schedule |
|---|---|---|---|
| dev-h7-easy-01 | Eight AI primary courses and four upper-level AI courses | Seven AI primary courses and three upper-level AI courses | Schedule remains valid |
| dev-h5-hard-01 | Five AI primary courses | Four AI primary courses | Schedule remains valid |

These discrepancies do not change the pre-established schedule-validity score, which checks structured course assignments. They show that a valid plan does not guarantee a fully accurate explanation. Verified totals should come from the checker when presenting advice. Evidence: [first response](../runs/csp16-pilot/dev-h7-easy-01-direct/response.json), [first check](../runs/csp16-pilot/dev-h7-easy-01-direct/check.json), [second response](../runs/csp16-pilot/dev-h5-hard-01-direct/response.json) and [second check](../runs/csp16-pilot/dev-h5-hard-01-direct/check.json).

## Inspection of infeasibility judgments

The six negative cases use three annotated mechanisms, each twice: required/forbidden conflicts, preclusions and co-requisite overload. The direct explanations identify sufficient contradictions. In dev-h4-hard-02, the model identifies an unavailable earlier probability prerequisite for CS3263 instead of the annotated overload; this is a valid alternative explanation under the supplied facts.

The two hard negative cases contain multiple contradictions. Separate local checks removed the fixed enrolment of LSM1301 from dev-h6-hard-02 and CS5242 from dev-h4-hard-02, respectively. Each change removes the annotated forced-load excess, but both modified specifications remain infeasible. In the first, CS3268 is fixed before its available mandatory prerequisite pathway; in the second, CS3263 is fixed before its available probability prerequisite. These checks used in-memory copies, made no model calls and did not alter the benchmark. The annotated mechanism should therefore not be interpreted as the sole cause of infeasibility.

## Interpretation and next decisions

The pilot validates the execution and scoring workflow and provides examples of reliable planning and translation under this restricted model. The 12/12 tie does not establish an accuracy advantage for solver assistance, and a single attempt on a small, correlated development subset does not establish general reliability or an empirical ordering of difficulty. The negative subset covers only three of the benchmark's contradiction mechanisms.

No prompt or model-configuration changes were made after inspection, and no additional model attempts were run. A possible future presentation refinement is to use checker-derived numerical totals instead of relying on numerical claims in model explanations. Before the held-out evaluation, the team should review source interpretations and decide whether explanation quality will remain a secondary manual finding or become an explicitly defined additional metric.

The findings address the proposal's Evaluation component. Public source snapshots, simplified completed internship credit, repeated offerings and the restricted catalogue constrain applicability; outputs are not a complete graduation audit or authoritative academic advice. Codex supported the evaluator changes, pilot execution and inspection. Actual student review and analysis should be recorded separately.

