# CS3263 - NUS CS / AI Programme Planning

**Current version: a feasibility CSP with a maximum of 16 modelled units per normal semester.** There is no scheduling or course-count objective. The implementation addresses proposal sub-problems (1) course selection, (2) prerequisites, and (3) semester allocation. Preferences are deferred.

The **24-development/120-evaluation benchmark** is locally validated. A 12-case paired development pilot is complete: both approaches answered 12/12 correctly. See [the pilot comparison and inspection](results/csp16-pilot/review.md) for runtime, translation equivalence and explanation errors. The user confirmed the source and assumption review complete on 11 October 2026, with no major problems found. The 120-case evaluation is frozen as csp16-evaluation-v1 and has not been run.

Start with the readable results:

- [Foundation-remaining example: solution and checks](results/validation/foundation-remaining/report.md)
- [AI-remaining example: solution and checks](results/validation/ai-remaining/report.md)
- [AI-remaining example: compiled CSP overview](results/validation/ai-remaining/csp.md)
- [Current benchmark design and review index](data/benchmark/README.md)

## Scope and assumptions

- NUS BComp(Computer Science), AY2026/27 admission cohort, Artificial Intelligence focus area.
- Programme Requirements only: 36 Foundation units, 32 Breadth/Depth units, and 12 Mathematics/Sciences units.
- **At most 16 units of modelled courses per normal semester; no minimum.** This is the project's workload policy, not a claim about an official NUS enrolment limit. It reserves room for courses outside our model and other study commitments.
- Completed courses, the first normal semester, and the number of remaining semesters are inputs.
- Foundation and mathematics courses are not automatically completed. Only courses explicitly listed in a testcase's completed record receive past credit; outstanding required courses must be newly scheduled.
- CP3200 is assumed already completed and contributes six Industry Experience units.
- The catalogue includes Foundation, Mathematics/Sciences, AI primaries/electives and prerequisite dependencies. Other focus-area electives are excluded.
- Normal Semesters 1 and 2 alternate. The AY2026/27 offering pattern is repeated in simulated future years.
- Students meet the standard mathematics, English and CS programme-entry conditions. Passed courses meet prerequisite grade thresholds.
- Common Curriculum, Unrestricted Electives, GPA, exemptions, exchange mappings, dissertation substitutions and special terms are outside the model.
- Completed transcripts are trusted; their historical legality is not audited.

The workload cap counts **every newly scheduled course**, including prerequisite-support courses, even when its units do not count toward Programme Requirements. This is a remaining Programme Requirements planner, not a complete graduation audit.

## Formal definition as a CSP

The instance is a finite constraint satisfaction problem:

$$
\mathcal{P}=(V,D,K)
$$

Here, $V$ is the set of variables, $D$ assigns each variable a finite domain, and $K$ is the set of constraints. A solution assigns a domain value to every variable and satisfies every constraint. There is **no objective function**: any satisfying schedule is acceptable.

### Inputs and notation

| Symbol | Meaning | Input source |
|---|---|---|
| $C$ | Courses in the frozen catalogue | data/courses.json |
| $T=\{1,\ldots,H\}$ | Remaining semester positions | Length of spec.semesters |
| $a_t\in\{1,2\}$ | Normal Semester 1 or 2 at position $t$ | spec.semesters |
| $u_c$ | Units carried by course $c$ | Catalogue units |
| $E\subseteq C$ | Already completed courses | spec.completed |
| $d_c\in\{0,1\}$ | Constant equal to 1 exactly when $c\in E$ | Derived from completed record |
| $A_c\subseteq\{1,2\}$ | Normal semesters offering course $c$ | Catalogue offered_semesters |
| $q_c\in\{0,1\}$ | Whether new enrolment is permitted | Catalogue selectable |
| $R\subseteq C$ | Required courses, including already completed requirements | spec.required |
| $F\subseteq C$ | Courses forbidden from new enrolment | spec.forbidden |
| $J\subseteq C\times T$ | Courses fixed to a remaining semester position | spec.fixed |
| $G$ | Requirement groups with memberships and bounds | spec.groups |
| $W$ | Maximum modelled units in a semester | spec.max_units; current examples use 16 |

Positions and normal-semester numbers are different: [2,1,2] means positions 1, 2, 3 correspond to normal Semesters 2, 1, 2. A fixed semester uses the **position**, not the normal-semester number. Specifications allow 1-12 remaining positions. The active schema rejects $W>16$; smaller caps are allowed for explicit restrictions and focused validation.

Course codes referenced by the request must exist in the catalogue. Invalid specifications are rejected before solving. Contradictory scheduling constraints are not silently repaired.

### Variables and domains

For every $c\in C$ and $t\in T$:

$$
x_{c,t}\in\{0,1\}
$$

$x_{c,t}=1$ means newly enrolling in course $c$ at remaining position $t$. Its generated name is `x_COURSE_POSITION`, for example `x_CS4246_2`.

For every $c\in C$:

$$
y_c\in\{0,1\}
$$

$y_c=1$ means the course is already completed or included in the new schedule. Its generated name is `y_COURSE`.

Additional Boolean variables represent completion before a semester and the truth of compound prerequisite expressions. They are created only when needed. All decision and logical auxiliary domains are $\{0,1\}$; backend constants have singleton domains.

### K1. Course selection, eligibility and completed credits

A course may be newly enrolled at most once:

$$
\sum_{t\in T}x_{c,t}\leq1 \qquad(c\in C).
$$

Completed and non-selectable courses cannot be newly enrolled:

$$
\sum_{t\in T}x_{c,t}=0
\qquad\text{if }d_c=1\text{ or }q_c=0.
$$

Completion/selection is linked to enrolment:

$$
y_c=d_c+\sum_{t\in T}x_{c,t}.
$$

The preceding constraints ensure this sum is Boolean. A completed course contributes its credits once, without being scheduled again. A non-selectable course may still receive historical completed credit.

### K2. Course offerings

$$
x_{c,t}=0 \qquad\text{if }a_t\notin A_c.
$$

Only a course's normal-semester offering pattern is modelled. Timetable clashes, quotas and future changes to actual offerings are not predicted.

### K3. Prerequisites and logical expressions

For a catalogue prerequisite course $p$, define:

$$
b_{p,t}=d_p+\sum_{s\lt t}x_{p,s}.
$$

Thus, $b_{p,t}=1$ exactly when $p$ was completed before the plan or in an earlier remaining semester. A prerequisite taken concurrently does **not** satisfy this expression. A missing prerequisite code evaluates to false; an OR expression can still use another available alternative.

Recursively translate the normalized prerequisite tree into $P_c(t)$:

- A course leaf $p$ becomes $b_{p,t}$.
- A satisfied admission assumption, true, or an explicitly absent prerequisite becomes 1.
- A blocked/false prerequisite becomes 0.
- AND requires all child expressions to be true.
- OR requires at least one child expression to be true.
- An n-of expression requires at least $k$ child expressions to be true.

For a compound expression with child Booleans $v_1,\ldots,v_n$, create a Boolean $z$ and enforce:

$$
z=1\iff\sum_{i=1}^{n}v_i\geq k.
$$

AND uses $k=n$, OR uses $k=1$, and n-of uses its specified threshold. Both implications are encoded, so $z$ exactly represents the expression.

Finally:

$$
x_{c,t}\leq P_c(t).
$$

Prerequisites restrict courses actually taken; an unselected course does not force its prerequisite chain to be completed. Admission conditions are resolved during normalization under the stated assumptions. Nonempty source prerequisites without a usable interpretation are flagged and blocked, rather than waived.

### K4. Co-requisites

For an ordinary catalogue co-requisite $p$ of $c$:

$$
x_{c,t}\leq b_{p,t}+x_{p,t}.
$$

The co-requisite must be completed earlier or taken concurrently. If it is unavailable in the catalogue, the dependent enrolment is blocked.

The explicitly modelled CS2101/CS2103T pair has the stricter rule:

$$
x_{\mathrm{CS2101},t}=x_{\mathrm{CS2103T},t}.
$$

They must be newly enrolled together. This constraint applies to new enrolments, while historical transcripts remain trusted.

### K5. Preclusions

For a precluded pair $(c,p)$, enforce:

$$
y_c+y_p\leq1.
$$

A preclusion listed in either course's data constrains the pair. If both courses are already completed, the historical record is not audited and this pair is skipped. Otherwise, a new course cannot conflict with a completed or newly selected course.

### K6. Semester workload

$$
\sum_{c\in C}u_c x_{c,t}\leq W \qquad(t\in T).
$$

The current programme examples use $W=16$. Completed courses consume no future workload. There is no minimum workload, so empty semesters are valid.

CP-SAT uses integer coefficients. Units and unit bounds are multiplied by 100: a 2.5-unit course becomes 250 and the 16-unit cap becomes 1600. The compiler rejects units that cannot be represented as nonnegative hundredths.

### K7. Required, forbidden and fixed courses

$$
y_c=1 \qquad(c\in R).
$$

$$
\sum_t x_{c,t}=0 \qquad(c\in F).
$$

$$
x_{c,t}=1 \qquad((c,t)\in J).
$$

Forbidden courses are prohibited only from **new enrolment**. Existing completed credit is retained. A required course already completed satisfies its requirement through $y_c=1$. A fixed course must be newly enrolled at the specified remaining position.

### K8. Programme requirement groups

For group $g$, let $M_g\subseteq C$ be its membership. Define:

$$
U_g=\sum_{c\in M_g}u_c y_c,\qquad
N_g=\sum_{c\in M_g}y_c.
$$

Enforce each non-null unit or course-count bound:

$$
L^u_g\leq U_g\leq H^u_g,\qquad
L^n_g\leq N_g\leq H^n_g.
$$

A null bound adds no corresponding constraint. Members count once within a group. A course can satisfy multiple distinct conditions, but overlapping groups' totals are not added together to calculate earned credits.

Foundation and Mathematics/Sciences courses are mandatory through $R$. The current group definitions are:

| Group | Membership | Bounds |
|---|---|---|
| breadth | AI breadth/depth electives and industry credit | At least 32 units |
| breadth_upper | Breadth members at level 4000 or above | At least 12 units |
| ai_primary | Available AI primary courses, including CS2109S | At least 3 courses |
| ai_upper | AI primaries at level 4000 or above | At least 1 course |
| industry | Industry Experience courses; CP3200 in this pathway | 6-12 units |
| cp_non_industry | Non-industry CP breadth courses; empty in this catalogue | At most 12 units |
| programme_lower | Programme courses at levels 1000-4000 | At least 64 units |

CS2109S contributes Foundation credits and an AI primary count, but is excluded from breadth credits. Foundation, mathematics and prerequisite-support courses do not earn breadth credits in this restricted model. CP3200 contributes six completed industry/breadth units. Four-unit elective increments may make breadth total 34 rather than exactly 32.

The lower-level bound is the project's interpretation of 80% of the fixed 80-unit Programme requirement: $0.8\times80=64$. It is not recalculated as 80% of all excess courses chosen by the solver.

### Solving and correctness

`build_csp()` instantiates $V,D,K$. `solve_csp()` asks OR-Tools CP-SAT for a satisfying assignment. The implementation has **no preference for earlier scheduling, fewer courses, or a shorter plan**. Different satisfying schedules can therefore be returned, including schedules containing extra permissible courses.

A feasible assignment is decoded into semester course lists. The independent checker then re-evaluates the original specification using Python sets, prerequisite-tree evaluation and credit arithmetic. It does not call the CSP builder or solver.

- feasible: a schedule was found; it must also pass the independent checker.
- infeasible: CP-SAT proved that no assignment satisfies this particular model.
- unknown: the search stopped without finding a schedule or proving impossibility.
- Invalid specifications/models are errors, not infeasibility results.

Solver feasibility concerns the simplified encoded rules. It does not establish that source interpretations match every official exception. See the [CP-SAT documentation](https://developers.google.com/optimization/cp/cp_solver).

## Small worked example

Take a hypothetical catalogue containing only A and B, each worth four units. A is a prerequisite for B; both are offered in normal Semesters 1 and 2. Neither is completed. Both are required, and two semesters remain.

The specification is:

~~~json
{
  "completed": [],
  "semesters": [1, 2],
  "max_units": 16,
  "required": ["A", "B"],
  "forbidden": [],
  "fixed": [],
  "groups": []
}
~~~

There are four enrolment variables and two selection variables. Required-course constraints force both courses to be taken exactly once. B cannot be taken in position 1, since A has not previously been completed. Taking B in position 2 requires A in position 1.

One satisfying assignment is:

- Position 1: A, four units.
- Position 2: B, four units.

This JSON assumes the hypothetical catalogue; real-course specifications use data/courses.json.

## Inspecting each stage

The intended pipeline is natural-language request -> JSON specification -> compiled CSP -> schedule -> independent validation. The two current specifications were assembled directly from the agreed rules for local validation; no fresh model translation was run.

| Artifact | What to inspect |
|---|---|
| request.txt | Human-readable scenario and its origin |
| spec.json | Exact completed, semester, workload, required, forbidden, fixed and group fields |
| csp.md | Variable/constraint counts, family counts, and group bounds |
| csp.json | Every variable/domain, logical rule and catalogue fact used by the compiler |
| model.pbtxt | Actual CP-SAT model; rule `backend_index` refers to its constraint position |
| plan.json | Machine-readable semester assignment |
| schedule.csv | Course codes, titles, units, remaining positions and normal semesters |
| validation.json | Individual pass/fail checks, prerequisite evidence, semester totals and matched group courses |
| report.md | Readable schedule and validation tables |
| manifest.json | Specification and implementation hashes; explicitly records zero model calls |

The example names are:

- foundation-remaining: seven semesters beginning in normal Semester 2; CS1101S, CS1231S and MA1521 are the only completed academic courses. CS2109S and the other outstanding Foundation/Mathematics courses, along with enough AI/breadth electives, must be newly scheduled.
- ai-remaining: four semesters beginning in normal Semester 1; twelve academic courses are completed after four simulated past semesters. CS2106 remains outstanding, along with the AI/breadth electives. CS3263 is fixed to remaining position 1 and CS4246 to position 2.

CS1101S is an explicit required course in both examples. It is classified as prerequisite support in the restricted Programme Requirements catalogue: its four units count toward semester workload, but do not add Foundation/breadth credits. Requiring it fixes the introductory programming pathway instead of allowing another catalogue alternative.

The completed CP3200 credit is a retained simplifying assumption, not a realistic first-year transcript. Academic course histories follow the study-stage policy below; internship scheduling remains outside the model.

They are inspection fixtures, not a statistically meaningful evaluation dataset.

## Local commands (PowerShell)

The existing project-local environment is ready. For another machine:

~~~powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip install -e . --no-deps
~~~

Construct and inspect a CSP without solving it:

~~~powershell
.venv\Scripts\python.exe -m degree_planner inspect-csp ai-remaining
~~~

Solve and save all inspection/validation stages:

~~~powershell
.venv\Scripts\python.exe -m degree_planner solve ai-remaining
.venv\Scripts\python.exe -m degree_planner solve foundation-remaining
~~~

Check a saved plan independently, including a manually edited plan:

~~~powershell
.venv\Scripts\python.exe -m degree_planner check data/examples/ai-remaining.json results/validation/ai-remaining/plan.json
~~~

Add --json to check for all detailed check records. The checker exits unsuccessfully if a plan is invalid; read its listed violations.

Run local validation:

~~~powershell
.venv\Scripts\python.exe -m degree_planner verify
.venv\Scripts\python.exe -m pytest -q
~~~

verify solves the two current examples and saves their reports under results/validation/. Tests validate feasible schedules and checker behavior without exhaustive enumeration or model calls.

Custom input: copy one example JSON, change its fields, and use solve PATH_TO_SPEC.json. --output can choose a directory inside results/validation/. Output paths are restricted to that area to protect source documents and historical experiments. The raw collector remains available, but refreshing source facts changes the interpretation being validated.

## Current benchmark

The active data/benchmark/ contains 24 development cases and 120 evaluation cases under the 16-unit feasibility model. Four remaining horizons (4-7) cross three designed difficulty levels. Every evaluation cell has seven feasible and three infeasible cases: **84 feasible and 36 infeasible evaluation cases**. Development has one of each label per cell.

Completed academic records come from checked past semester schedules, with progress ranges of 2-4 courses for seven remaining semesters, 5-7 for six, 8-9 for five, and 10-12 for four. Some early histories leave CS1101S outstanding and require the full introductory programming chain to be scheduled. The ranges do not overlap, so longer horizons always have fewer completed academic courses. The cases leave different foundation courses outstanding; they do not grant all foundations by default. CP3200 remains a separate internship-credit exception.

Completed-course sets are disjoint between development and evaluation. Histories recur within a split to support controlled comparisons; different cases add elective requirements, fixed positions, and forbidden alternatives. Cases remain correlated synthetic variants, not independent observations of real students. Constraint mechanisms can recur across splits, so this is not a claim of generalisation to entirely unseen templates.

Course facts, prerequisite expressions, programme bounds and the cap stay fixed. Easy feasible cases require one chosen elective without additional fixed/forbidden constraints; medium cases require three electives, two fixed enrolments and two forbidden alternatives; hard cases require six electives, five fixed enrolments and four forbidden alternatives. These are designed categories, not measured model difficulty. Infeasibility proof difficulty can differ from the surrounding request's designed level.

Every academic history and feasible reference schedule passes the independent checker. Every infeasible case has a solver proof, an arithmetically checked contradiction witness, and a separately checked feasible precursor. Source-rule correctness is distinct from correctness under the frozen model. There are no timeout-based infeasibility labels.

Browse [data/benchmark/README.md](data/benchmark/README.md), index.csv, or individual review/CASE_ID.md files. Each case has an editable specification in cases/CASE_ID.json. Gold labels, histories, reference plans and validation records are retained in gold.jsonl and excluded from model prompts. The first 12 development entries cover all horizon/difficulty cells with six feasible and six infeasible requests.

~~~powershell
# Rebuild and locally validate the benchmark, without model calls.
.venv\Scripts\python.exe -m degree_planner benchmark --seed 3263

# Solve one case by identifier and check its saved plan.
.venv\Scripts\python.exe -m degree_planner solve dev-h7-easy-01
.venv\Scripts\python.exe -m degree_planner check data/benchmark/cases/dev-h7-easy-01.json results/validation/dev-h7-easy-01/plan.json
~~~

Generation is seeded and specifications are reproducible for the same frozen facts and implementation. Reference schedules are any satisfying assignments; an OR-Tools/runtime change can produce a different schedule. Comparison commands check the validated input/source hashes before making model calls. A run cannot mix splits, selected cases or changed settings. The generated benchmark guide records construction without model calls; subsequent experiment results are saved separately.

The completed pilot used the first 12 development cases and one attempt per approach per case:

The recorded command was .venv\Scripts\python.exe -m degree_planner run --split dev --limit 12 --name csp16-pilot. The saved pilot outputs remain unchanged. The reporting-policy revision below changes the evaluator fingerprint, so the current implementation requires a separately named experiment rather than resuming or overwriting csp16-pilot. Its original evaluator is retained at [frozen_sources/evaluate.py](results/runs/csp16-pilot/frozen_sources/evaluate.py), matching the pilot manifest hash.

The run manifest freezes the selected case IDs. summary.csv retains all split cases with a selected flag; accuracy denominators include only completed selected attempts. Pending cases and execution failures are reported separately. analysis.md and metrics.json include paired results, horizon/difficulty breakdowns, canonical translation differences, runtime and usage. review.md records manual inspection, including equivalent translations and explanation errors. Raw responses, prompts, events and diagnostics are preserved under results/runs/csp16-pilot/. Source or prompt changes require a separately named experiment.

The prepared held-out experiment is **csp16-evaluation-v1**, selecting all 120 test cases for 240 planned attempts. Its [manifest](results/runs/csp16-evaluation-v1/manifest.json) freezes the current protocol; [freeze metadata](results/runs/csp16-evaluation-v1/freeze.json) records the review confirmation, runtime, passing 25-test suite, snapshot inventory and prepared prompt hashes. Exact copies of the dataset, prompts, configuration, implementation and tests are retained under results/runs/csp16-evaluation-v1/frozen/. Preparation made no model calls. The settings remain gpt-6.1-sol, medium reasoning effort, a 180-second process timeout, a 10-second solver limit and one attempt per approach per case.

To execute and then score this frozen experiment from the project root:

~~~powershell
.venv\Scripts\python.exe -m degree_planner run --split test --name csp16-evaluation-v1
.venv\Scripts\python.exe -m degree_planner evaluate --split test --name csp16-evaluation-v1
~~~

The existing fingerprint checks reject changed inputs, implementation, settings or case selection under this run name. Keep the primary scoring policy below fixed throughout the evaluation.

### Evaluation scoring policy

Policy outcome-v1-explanation-secondary retains the pilot's primary correctness rules. A feasible answer must pass the output schema and the independent checker against the original request. An infeasible answer must pass the output schema and agree with the validated gold label. Completed selected attempts form the accuracy denominator; execution failures, malformed outputs and unknown answers count as unsuccessful, while pending and unselected attempts are excluded.

Explanation content is a secondary manual finding and does not change the primary score. Output schema requirements still apply. Record incorrect numerical claims and unsupported reasoning separately; an infeasibility explanation may use any sufficient contradiction rather than reproducing the annotated witness. A witness annotation does not establish that the mechanism is the sole cause or that proof difficulty matches the designed request difficulty.

Translation auditing distinguishes a canonical field match from semantic fidelity. The revised summary.csv uses translation_canonical_match and translation_semantic_status instead of the ambiguous translation_faithful field. A difference receives review_required until separately reviewed as equivalent, non-equivalent or unresolved. An outcome that agrees with gold does not establish an equivalent translation. The policy is included in new metrics.json and analysis.md outputs. [manual_audit.json](results/csp16-pilot/manual_audit.json) records the pilot's two explanation-error cases and its equivalent redundant requirement, without altering existing scores; student-team review remains pending.

## Testcase study stage and completed courses

Programme evaluation cases should have **4-7 remaining normal semesters**. Under a stated eight-semester study timeline, the remaining horizon determines how many semesters have elapsed. Longer horizons should generally have fewer completed academic courses, rather than receiving credit for most foundations by default. This is a dataset-design policy; the general solver still supports other horizons for small constraint examples and custom investigations.

One prerequisite-valid synthetic academic history is:

| Past semester | Normal semester | Academic courses completed in that semester | Units |
|---:|---:|---|---:|
| 1 | 1 | CS1101S, CS1231S, MA1521 | 12 |
| 2 | 2 | CS2030S, CS2040S, MA1522 | 12 |
| 3 | 1 | CS2100, CS2109S, ST2334 | 12 |
| 4 | 2 | CS2101, CS2103T, CS3230 | 12 |

Take a prefix of this history to create a consistent profile:

| Remaining semesters | Stage at the start of the plan | Past semesters | First normal semester | Completed academic courses |
|---:|---|---:|---:|---:|
| 7 | Year 1 Semester 2 | 1 | 2 | 3 |
| 6 | Year 2 Semester 1 | 2 | 1 | 6 |
| 5 | Year 2 Semester 2 | 3 | 2 | 9 |
| 4 | Year 3 Semester 1 | 4 | 1 | 12 |

The counts exclude the separately assumed CP3200 internship credit. These are example profiles, not compulsory student transcripts or a fixed course-count formula. Future generated cases can use different legal academic histories, while keeping previous workload, prerequisites, offerings and co-requisites consistent with the stated study stage. Review completed **units and prerequisite depth**, not just course counts. Early-stage cases should leave substantial foundational work outstanding; later-stage cases can have more completed foundations while retaining AI/breadth work. Both feasible and deliberately infeasible remaining requests are useful; do not silently add completed courses merely to make a request feasible.

The current checker trusts the supplied completed record; it does not reconstruct its past semester order. The table above was separately checked as a four-semester schedule under the frozen catalogue and 16-unit cap. Custom completed records therefore need the author's review for historical plausibility.

## Writing and checking your own testcase

From the project root, copy the full early-stage specification:

~~~powershell
Copy-Item -LiteralPath data/examples/foundation-remaining.json -Destination data/examples/my-case.json
~~~

Edit data/examples/my-case.json in a text editor. The JSON must contain all seven specification fields, without comments or extra fields:

| Field | What to write |
|---|---|
| completed | Courses actually passed before the plan, including CP3200 under the current internship simplification. Use only catalogue codes; no duplicates. |
| semesters | One normal-semester number per remaining position, alternating 1 and 2. Seven starting in Semester 2 is [2,1,2,1,2,1,2]; four starting in Semester 1 is [1,2,1,2]. |
| max_units | Keep 16 for the programme testcases. |
| required | Keep the full mandatory list, including completed requirements, and add any elective you want to require. Completed courses satisfy their requirement through past credit. |
| forbidden | Courses that must not be newly enrolled; use [] if none. |
| fixed | Explicit enrolment positions, e.g. [{"course":"CS3263","semester":3}]. Position 3 means the third remaining semester, not normal Semester 3. Use [] if none. |
| groups | Keep the copied programme groups and bounds when testing the agreed degree model. Changing them creates a different planning problem. |

Find available codes and course facts in data/courses.json. For a six-semester profile from the table, set completed to ["CP3200","CS1101S","CS1231S","CS2030S","CS2040S","MA1521","MA1522"] and semesters to [1,2,1,2,1,2], leaving the other copied fields unchanged.

Solve the case and then run the independent checker:

~~~powershell
.venv\Scripts\python.exe -m degree_planner solve data/examples/my-case.json --output results/validation/my-case
.venv\Scripts\python.exe -m degree_planner check data/examples/my-case.json results/validation/my-case/plan.json
~~~

Read results/validation/my-case/report.md for the schedule, semester unit totals, group totals and validation result. schedule.csv includes course titles; validation.json lists every check. Add --json to the check command for detailed console output. To examine your own proposed schedule, copy plan.json to a separate filename, edit its semester course arrays, and pass that filename to check with the original testcase JSON.

Interpret status carefully: feasible with independent validation PASS is a checked schedule; infeasible is CP-SAT's conclusion for the supplied specification; unknown means neither a solution nor an infeasibility proof was found within the search limit. The checker validates feasible schedules only, so it cannot independently certify infeasible or unknown output. Those statuses make the solve command exit unsuccessfully even though the saved artifacts remain available. You can retry unknown with a longer --time-limit, without treating it as infeasible.

These commands test the symbolic solver and checker. They do not call a language model. request.txt is a generated description for inspection, not an input to solve, and assumes the standard programme groups. Adding a custom case to model evaluation requires a reviewed natural-language request and validated JSONL/gold entries; editing a convenience export alone does not change the active benchmark. Keep gold specifications and reference schedules out of model prompts. The 12-case development comparison is complete; the held-out evaluation remains pending.

## Sources and unresolved rules

Course facts come from the [NUSMods API](https://api.nusmods.com/v2/). Programme rules come from the [AY2026/27 CS cohort page](https://www.comp.nus.edu.sg/cug/per-cohort/cs/cs-26-27/) and [CS focus-area page](https://www.comp.nus.edu.sg/programmes/ug/focus/).

There are 86 NUSMods records plus one completed-credit-only CP3200 record from the official programme page. CP3200 is not a current-year offering. Missing curriculum-listed courses appear in data/sources.json. Unresolved wildcard prerequisites are recorded in data/review.json and blocked from new selection.

The 16-unit cap is a project policy and is stored separately from source facts in the requirements snapshot and policy.py. The user confirmed the source and assumption review complete on 11 October 2026, with no major problems found; the confirmation is retained in the evaluation freeze metadata.

## Historical experiment and deferred work

The original 6-development/24-evaluation benchmark and saved comparison records used a **32-unit cap** and an optimization objective. They remain historical evidence and have not been relabelled or re-scored.

All 30 historical cases pre-completed CS1101S and MA1521. Eight of the 24 evaluation cases pre-completed every mandatory Foundation/Mathematics course; the other 16 pre-completed either nine or three of those twelve courses. The earlier accuracy results therefore do not establish performance when the entire academic pathway remains to be planned.

- Original benchmark: results/historical/32-unit-inputs/data/benchmark/.
- Original records/results: results/runs/, results/pilot/, results/initial/.
- Exact original inputs and core solver sources: results/historical/32-unit-inputs/.
- Original Git commit: 468f5b79ddf2c8c363e354f3c5367431a7a0d8d7.

Those results do not describe the current 16-unit feasibility CSP. Changing the cap can change feasibility labels. The original benchmark was replaced in the active data/benchmark/ only after confirming the archived copies matched exactly. run and evaluate reject historical labels, changed source facts, or changed validated artifacts before making model calls or changing results. The current comparison uses the separately named csp16-pilot run.

The current 12-case model pilot is complete. The 120-case evaluation, further comparisons and preferences remain future work. The new 144-case benchmark has been generated and locally validated.

## Files and proposal mapping

| Component | Responsibility | Proposal sub-problems |
|---|---|---|
| collect.py, normalize.py | Source facts and explicit interpretations | 1-3 |
| policy.py, schemas.py | Workload policy and specification contracts | 1-3 |
| benchmark.py, histories.py, data/examples/ | Checked history generation, labelled benchmark, and local examples | 1-3 and Evaluation |
| csp.py | Variables, domains, constraints and their inspection record | 1-3 |
| solver.py | Feasibility search and schedule decoding | 1-3 |
| checker.py | Independent constraint checks and credit totals | 1-3 |
| inspection.py, __main__.py | Readable stage artifacts and inspect/solve/check commands | 1-3 |
| codex_runner.py, evaluate.py, protocol.py | Controlled comparison infrastructure and frozen-input checks | Evaluation |

docs/ is unchanged. Actual authoritative files are docs/CS3263_Project_Guidelines.md and docs/CS3263_Project_Proposal.md; the shorter names in AGENTS.md are stale references.

## Responsible AI and academic contribution

No private student transcripts were used. Distinguish official course facts, project assumptions, solver feasibility and independent human review. Outputs are not authoritative academic advice.

The user approved the scope and the 16-unit feasibility refactor. Codex supported source acquisition, implementation, example construction, validation and documentation. See CONTRIBUTIONS.md. Team members must record their actual reviews, modifications, analysis and academic writing, and understand the complete formulation. The course report remains the team's deliverable.
