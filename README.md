# CS3263 — NUS CS / AI Programme Planning

**Status: early, immature prototype.** Programme-rule interpretations and benchmark labels await student-team review. Results apply only to the initial simplified benchmark.

A small, reproducible comparison of **direct Codex planning** and **Codex translation followed by a constraint solver**. This implements the submitted proposal's sub-problems (1) course selection, (2) prerequisites, and (3) semester allocation. Preferences are deferred.

## Agreed scope

- Admission cohort AY2026/27, BComp(Computer Science), Artificial Intelligence focus area.
- Programme Requirements only: 36 Foundation units, 32 Breadth/Depth units, 12 Mathematics/Sciences units.
- Maximum **32 units per normal semester**, with no minimum.
- Completed courses, starting semester and remaining semester count vary by scenario.
- CP3200 is already completed, contributing 6 Industry Experience units.
- Common Curriculum, Unrestricted Electives, GPA, exemptions, exchange mappings and dissertation substitutions are excluded.
- Normal Semesters 1/2 alternate; AY2026/27 offerings repeat in future simulated years.
- Students satisfy standard mathematics, English and programme-entry conditions; passed courses meet the D-grade prerequisite thresholds.
- The catalogue covers Foundation, Mathematics/Sciences, AI primaries/electives and prerequisite dependencies. Other focus-area elective choices are excluded.

This is a **remaining Programme Requirements planner**, not a complete graduation audit. Workload accounts only for modelled courses. Synthetic transcripts are assumed truthful; the historical legality of completed courses/internship is not audited.

## Sources and data

Course facts come from the [NUSMods API](https://api.nusmods.com/v2/). Programme rules come from the [AY2026/27 CS cohort page](https://www.comp.nus.edu.sg/cug/per-cohort/cs/cs-26-27/) and [CS focus-area page](https://www.comp.nus.edu.sg/programmes/ug/focus/).

The first snapshot contains **86 NUSMods course records**, plus one **completed-credit-only CP3200 record** sourced from the official programme page. CP3200 is not represented as a current-year offering. Curriculum-listed courses missing from the API are recorded in data/sources.json. Unresolved prerequisite conditions are blocked from new selection; see data/review.json. All source interpretations need student-team review before submission.

Grade-tagged prerequisites are normalised under the stated passing-grade assumption. AND, OR, n-of, admission-cohort and programme-type conditions are supported. Missing prerequisite trees are not automatically interpreted as no requirements. Wildcard conditions currently unresolved are flagged and blocked.

CS2109S can count toward the AI focus area while its credits remain in Foundation. Foundation and mathematics credits do not also earn Breadth/Depth credits. The 80% lower-level condition is modelled as at least **64 Programme units at levels 1000–4000**, based on the fixed 80-unit requirement; excess units may be needed because the six-unit internship and four-unit electives do not sum to exactly 32.

## Setup (PowerShell)

The project-local environment has already been created on this machine.

    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -e ".[dev]"
    .venv\Scripts\python.exe -m pytest -q

For the exact versions used in the initial run:

    .venv\Scripts\python.exe -m pip install -r requirements-lock.txt
    .venv\Scripts\python.exe -m pip install -e . --no-deps

## Usage

Inspect a reference solution:

    .venv\Scripts\python.exe -m degree_planner solve test-hard-01

Verify the checked-in benchmark:

    .venv\Scripts\python.exe -m degree_planner verify

Collect/rebuild only when deliberately preparing a **new benchmark version**:

    .venv\Scripts\python.exe -m degree_planner collect
    .venv\Scripts\python.exe -m degree_planner benchmark

Use --refresh on collect only to replace the source snapshot. Do not refresh data or rebuild labels during a frozen experiment. Raw snapshots are cached.

## Codex subscription execution

Install or use the existing Codex CLI and sign in with ChatGPT. Each teammate uses their own authenticated account; no credentials are stored in this project. This machine's CLI was already signed in.

    codex login
    .venv\Scripts\python.exe -m degree_planner run --split dev --name pilot
    .venv\Scripts\python.exe -m degree_planner evaluate --split dev --name pilot
    .venv\Scripts\python.exe -m degree_planner run --split test --name initial
    .venv\Scripts\python.exe -m degree_planner evaluate --split test --name initial

experiment.json fixes the requested model (gpt-6.1-sol), medium reasoning, one attempt and a 180-second timeout. Team members must use the same model/settings. Model updates and subscription limits can affect repeatability and elapsed time.

The runner disables model-side shell, browsing, apps, plugins, agents and memory; starts each case in an empty temporary workspace; suppresses project instruction loading; and requests schema-constrained output. It audits saved events for tool use. The host script, not Codex, invokes CP-SAT after translation. CLI runtime warning items are preserved and distinguished from tool calls. Any unexpected model tool item stops the batch. Empty case workspaces are removed afterward.

Both approaches receive the same domain facts and natural-language request. The direct model produces a plan; the translator produces the fixed declarative specification. A Python compiler enforces catalogue prerequisites/offerings/preclusions for pipeline B. The independent checker evaluates both plans against the benchmark's original specification.

Gold labels/reference plans are never included in model prompts. Existing attempts are retained when resuming a batch. Do not repair model outputs or retry failed cases inside the same experiment.

## Benchmark and results

- 6 development cases.
- 24 evaluation cases: 8 per designed difficulty level, including 6 infeasible cases.
- Feasible references are solver-produced and independently checked.
- Infeasible labels require solver proofs and have documented construction rationales.
- Solver timeouts are unknown, not infeasible.
- Difficulty categories describe designed constraint interactions, not a calibrated student difficulty scale.
- These are related controlled synthetic scenarios, not independent representative samples. Some development/evaluation cases share mechanisms.

results/runs/ stores each prompt, response, event log, execution record and evaluation diagnostics. results/initial/summary.csv and analysis.md present counts, valid-plan rates, infeasibility detection, canonical translation mismatches and failure examples. Runtime/token usage is reported when available; a dollar cost is not inferred from subscription tokens.

The completed initial comparison achieved **24/24 correct evaluation outcomes for both approaches** (18 feasible, 6 infeasible). Mean process-plus-solver time was **19.49 seconds direct** and **33.56 seconds assisted**. Both passed all six development cases. The five canonical translation differences were redundant constraints in this frozen model; see [experiment interpretation and translation review](results/initial/translation_review.md). This small benchmark did not demonstrate an accuracy advantage for the assisted approach.

Canonical translation mismatches are diagnostics, not a complete semantic-equivalence test. Infeasible predictions are evaluated against the original label even when a translation has errors; the translation audit exposes such coincidental correctness.

## Files and proposal mapping

| Component | Responsibility | Proposal |
|---|---|---|
| collect.py, normalize.py | Source snapshots and explicit rule interpretations | 1–3 |
| schemas.py | Course-plan and formal-specification contracts | 1–3 |
| benchmark.py | Controlled requests and verified references | 1–3 |
| solver.py | Course selection, prerequisite and semester CSP | 1–3 |
| checker.py | Independent constraint verification | 1–3 |
| codex_runner.py | Same-model controlled comparison | Approach/evaluation |
| evaluate.py | Metrics, translation diagnostics and results | Approach/evaluation |

docs/ remains unchanged. Original guidelines and proposal use CS3263_Project_Guidelines.md and CS3263_Project_Proposal.md; the shorter names in AGENTS.md are stale references.

## Responsible AI and academic contribution

No private student records are used. Preserve the distinction between verified source facts, simplified assumptions and unresolved rules. Outputs must not be used as authoritative graduation advice.

The student team chose and approved the scope. Codex supported implementation, data acquisition, benchmark construction and initial evaluation. See CONTRIBUTIONS.md; the team should record its own source reviews, design changes, experimental interpretation and report/presentation work. The course guidelines require transparent contributions and student understanding of the complete work.

The report remains the team's academic deliverable: explain the CSP, comparison protocol, assumptions, observed errors and responsible-AI limitations within the course's ten-page limit. The implementation is deliberately small and extensible; enlarge the benchmark before adding a user interface or extra models.
