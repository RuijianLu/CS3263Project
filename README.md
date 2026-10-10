# CS3263 - NUS CS / AI Programme Planning

**Current version: a feasibility CSP with a maximum of 16 modelled units per normal semester.** There is no scheduling or course-count objective. The implementation addresses proposal sub-problems (1) course selection, (2) prerequisites, and (3) semester allocation. Preferences are deferred.

Current work is local CSP construction and solution validation. No new model calls, comparison experiments, exhaustive enumeration, or large benchmark generation have been performed for this version. Programme interpretations still require student-team review.

Start with the readable results:

- [AI-remaining example: solution and checks](results/validation/ai-remaining/report.md)
- [Foundation-remaining example: solution and checks](results/validation/foundation-remaining/report.md)
- [AI-remaining example: compiled CSP overview](results/validation/ai-remaining/csp.md)

## Scope and assumptions

- NUS BComp(Computer Science), AY2026/27 admission cohort, Artificial Intelligence focus area.
- Programme Requirements only: 36 Foundation units, 32 Breadth/Depth units, and 12 Mathematics/Sciences units.
- **At most 16 units of modelled courses per normal semester; no minimum.** This is the project's workload policy, not a claim about an official NUS enrolment limit. It reserves room for courses outside our model and other study commitments.
- Completed courses, the first normal semester, and the number of remaining semesters are inputs.
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

- foundation-remaining: eight semesters; an early completed record with CS1101S, CS1231S, MA1521, MA1522 and CP3200.
- ai-remaining: three semesters; Foundation/Mathematics already completed, with CS3263 fixed to position 1 and CS4246 to position 2.

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

## Sources and unresolved rules

Course facts come from the [NUSMods API](https://api.nusmods.com/v2/). Programme rules come from the [AY2026/27 CS cohort page](https://www.comp.nus.edu.sg/cug/per-cohort/cs/cs-26-27/) and [CS focus-area page](https://www.comp.nus.edu.sg/programmes/ug/focus/).

There are 86 NUSMods records plus one completed-credit-only CP3200 record from the official programme page. CP3200 is not a current-year offering. Missing curriculum-listed courses appear in data/sources.json. Unresolved wildcard prerequisites are recorded in data/review.json and blocked from new selection.

The 16-unit cap is a project policy and is stored separately from source facts in the requirements snapshot and policy.py. All programme interpretations and synthetic completed records still need student-team review.

## Historical experiment and deferred work

The original 6-development/24-evaluation benchmark and saved comparison records used a **32-unit cap** and an optimization objective. They remain historical evidence and have not been relabelled or re-scored.

- Original benchmark: data/benchmark/.
- Original records/results: results/runs/, results/pilot/, results/initial/.
- Exact original inputs and core solver sources: results/historical/32-unit-inputs/.
- Original Git commit: 468f5b79ddf2c8c363e354f3c5367431a7a0d8d7.

Those results do not describe the current 16-unit feasibility CSP. Changing the cap can change feasibility labels. run and evaluate therefore reject the historical benchmark before making model calls or changing results. Benchmark generation is deferred. A future comparison will require deliberately constructed 16-unit cases, fresh labels and a new run name.

Larger testcase generation, further model comparisons and preferences remain future work.

## Files and proposal mapping

| Component | Responsibility | Proposal sub-problems |
|---|---|---|
| collect.py, normalize.py | Source facts and explicit interpretations | 1-3 |
| policy.py, schemas.py | Workload policy and specification contracts | 1-3 |
| benchmark.py, data/examples/ | Specification helpers and two local examples | 1-3 |
| csp.py | Variables, domains, constraints and their inspection record | 1-3 |
| solver.py | Feasibility search and schedule decoding | 1-3 |
| checker.py | Independent constraint checks and credit totals | 1-3 |
| inspection.py, __main__.py | Readable stage artifacts and inspect/solve/check commands | 1-3 |
| codex_runner.py, evaluate.py, protocol.py | Retained comparison infrastructure; new benchmark required | Evaluation |

docs/ is unchanged. Actual authoritative files are docs/CS3263_Project_Guidelines.md and docs/CS3263_Project_Proposal.md; the shorter names in AGENTS.md are stale references.

## Responsible AI and academic contribution

No private student transcripts were used. Distinguish official course facts, project assumptions, solver feasibility and independent human review. Outputs are not authoritative academic advice.

The user approved the scope and the 16-unit feasibility refactor. Codex supported source acquisition, implementation, example construction, validation and documentation. See CONTRIBUTIONS.md. Team members must record their actual reviews, modifications, analysis and academic writing, and understand the complete formulation. The course report remains the team's deliverable.
