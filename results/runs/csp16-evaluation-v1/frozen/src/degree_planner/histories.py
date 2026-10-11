"""Proposal sub-problems 1-3: generate legal past academic schedules, not credits by fiat."""
from __future__ import annotations
import hashlib
import itertools
import json
from .checker import check, satisfied
from .policy import MAX_UNITS

HISTORY_COUNTS = {7: (2, 4), 6: (5, 7), 5: (8, 9), 4: (10, 12)}


def history_spec(horizon):
    return dict(completed=["CP3200"], semesters=[1 + t % 2 for t in range(8 - horizon)],
                max_units=MAX_UNITS, required=[], forbidden=[], fixed=[], groups=[])


def validate_history(history, courses, pairs):
    """Audit academic semesters; CP3200 is credited separately under the agreed exception."""
    plan = dict(status="feasible", semesters=history["academic_semesters"],
                explanation="Synthetic academic history; separate historical internship credit.")
    checked = check(plan, history_spec(history["remaining_semesters"]), courses, pairs)
    completed = sorted({c for semester in plan["semesters"] for c in semester} | {"CP3200"})
    if completed != history["completed"]:
        raise ValueError("History semesters do not match the completed record")
    if not checked["valid"]:
        raise ValueError(f"Illegal academic history: {checked['violations']}")
    return checked


def history_pool(courses, req, horizon, rng, trials=2500):
    mandatory = set(req["foundation"] + req["mathematics"] + ["CS1101S"])
    pair_members = {c for pair in req["corequisite_pairs"] for c in pair}
    bundles = [(c,) for c in sorted(mandatory - pair_members)]
    bundles += [tuple(pair) for pair in req["corequisite_pairs"]]
    pool = {}
    past_count = 8 - horizon
    for _ in range(trials):
        target = rng.randint(*HISTORY_COUNTS[horizon])
        done, semesters = set(), []
        for position in range(past_count):
            remaining = target - len(done)
            later = past_count - position - 1
            lo, hi = max(1, remaining - 4 * later), min(4, remaining - later)
            if lo > hi:
                break
            quota = rng.randint(lo, hi)
            season = 1 + position % 2
            eligible = [bundle for bundle in bundles if not done.intersection(bundle)
                        and all(courses[c]["selectable"] and season in courses[c]["offered_semesters"]
                                and satisfied(courses[c]["prerequisites"], done) for c in bundle)]
            choices = []
            for count in range(1, min(4, len(eligible)) + 1):
                for combination in itertools.combinations(eligible, count):
                    codes = sorted(c for bundle in combination for c in bundle)
                    if len(codes) != quota:
                        continue
                    if sum(courses[c]["units"] for c in codes) <= MAX_UNITS:
                        choices.append(codes)
            if not choices:
                break
            selected = rng.choice(choices)
            semesters.append(selected)
            done.update(selected)
        if len(semesters) != past_count or len(done) != target:
            continue
        key = tuple(sorted(done))
        if key in pool:
            continue
        digest = hashlib.sha256(json.dumps(key).encode()).hexdigest()[:12]
        history = dict(id=f"h{horizon}-{digest}", remaining_semesters=horizon,
                       past_semesters=past_count, academic_semesters=semesters,
                       completed=sorted(done | {"CP3200"}),
                       academic_course_count=len(done),
                       academic_units=sum(courses[c]["units"] for c in done),
                       internship_exception="CP3200 separately credited; eligibility is not simulated.")
        checked = validate_history(history, courses, req["corequisite_pairs"])
        history["validation"] = dict(valid=True, passed=len(checked["checks"]),
                                     semester_units=[s["units"] for s in checked["semesters"]])
        pool[key] = history
    values = sorted(pool.values(), key=lambda h: h["id"])
    if len(values) < 5:
        raise ValueError(f"Too few distinct legal histories for {horizon} remaining semesters")
    return values


def partition_histories(values, rng):
    """Keep completed-course sets disjoint between development and evaluation."""
    values = list(values)
    rng.shuffle(values)
    pending = [h for h in values if "CS2103T" not in h["completed"]]
    if len(pending) < 2:
        raise ValueError("Both splits need a history with the concurrent course pair outstanding")
    first = pending[0]
    candidates = [h for h in values if h is not first and h is not pending[1]]
    second = candidates[0]
    development = [first, second]
    evaluation = [h for h in values if h not in development]
    return development, evaluation
