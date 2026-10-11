"""Proposal sub-problems 1-3: resolve cohort rules and preserve review decisions."""
from __future__ import annotations
import re
from .collect import CODE, COHORT_URL, read_json, write_json

def resolve(tree, cohort=2026):
    if tree is None or isinstance(tree, bool):
        return tree
    if isinstance(tree, str):
        code, *grade = tree.split(":")
        if not CODE.fullmatch(code):
            raise ValueError(f"Non-course prerequisite leaf: {tree}")
        if grade and grade[0] != "D":
            raise ValueError(f"Grade-specific prerequisite needs review: {tree}")
        return code
    if not isinstance(tree, dict):
        raise ValueError(f"Unsupported prerequisite node: {tree}")
    for op in ("and", "or"):
        if op in tree:
            return {op: [resolve(t, cohort) for t in tree[op]]}
    if "nOf" in tree:
        n, children = tree["nOf"]
        return {"nOf": [n, [resolve(t, cohort) for t in children]]}
    if "cohort" in tree:
        cond = tree["cohort"]
        low, high = None, None
        for token in cond["years"]:
            bound, year = token.split(":", 1)
            value = int(year[:4])
            if bound == "S": low = value
            elif bound == "E": high = value
            else: raise ValueError("Unknown cohort bound")
        inside = (low is None or cohort >= low) and (high is None or cohort <= high)
        rule = cond["rule"]
        matches = inside if rule in {"IF_IN", "MUST_BE_IN"} else not inside
        if rule.startswith("MUST") and not matches: return False
        return resolve(tree["then"], cohort) if matches and "then" in tree else (True if "then" in tree else matches)
    if "programType" in tree:
        cond = tree["programType"]
        inside = "Undergraduate Degree" in cond["types"]
        if cond["rule"] == "MUST_BE_IN" and not inside: return False
        return resolve(tree["then"], cohort) if inside else True
    raise ValueError(f"Unsupported prerequisite operator: {list(tree)}")

def normalize(root):
    req = read_json(root / "data/requirements.json")
    records = read_json(root / "data/raw/course_records.json")
    foundation, math = set(req["foundation"]), set(req["mathematics"])
    ai = set(req["ai_primaries"] + req["ai_electives"])
    result, review = {}, []
    # Explicit standard-pathway assumptions, not guessed from a missing tree.
    overrides = {
        "CS1231S": (True, "Assume qualifying pre-university mathematics; documented alternative to MA1301/X."),
        "MA1521": (True, "Assume qualifying pre-university mathematics; documented alternative to MA1301/X."),
        "MA1522": (True, "Assume qualifying pre-university mathematics for standard CS admission."),
        "CS1101S": (True, "Assume qualifying mathematics for standard CS admission."),
        "CS2101": (True, "Assume CS programme eligibility and the English proficiency prerequisite are satisfied.")
    }
    for code, raw in sorted(records.items()):
        flags, decisions = [], []
        tree = raw.get("prereqTree")
        text = raw.get("prerequisite", "").strip()
        if code in overrides:
            tree, note = overrides[code]
            decisions.append(note)
        else:
            if tree is None and text and text.lower() not in {"nil", "none", "na", "n.a.", "not applicable"}:
                flags.append("Nonempty prerequisite text without a machine-readable tree")
            try: tree = resolve(tree)
            except ValueError as exc:
                flags.append(str(exc))
                tree = False
            if re.search(r"\b(permission|approval|consent|GPA|CAP)\b|\d+\s*(?:units|MCs)\b", text, re.I):
                flags.append("Non-course eligibility condition requires review")
        if code == "CS2103T":
            decisions.append("CS programme and English proficiency assumed satisfied; course prerequisites retained.")
        category = ("foundation" if code in foundation else "mathematics" if code in math
                    else "industry" if code == "CP3200" else "breadth" if code in ai
                    else "prerequisite_support")
        result[code] = {
            "code": code, "title": raw["title"], "units": float(raw["moduleCredit"]),
            "level": int(re.search(r"\d", code).group()) * 1000,
            "category": category, "ai_primary": code in req["ai_primaries"],
            "offered_semesters": sorted({s["semester"] for s in raw["semesterData"] if s["semester"] in [1, 2]}),
            "prerequisites": tree,
            "corequisites": sorted(set(CODE.findall(raw.get("corequisite", "")))),
            "preclusions": sorted(set(CODE.findall(raw.get("preclusion", ""))) - {code}),
            "raw_prerequisite": text, "raw_corequisite": raw.get("corequisite", ""),
            "raw_preclusion": raw.get("preclusion", ""),
            "selectable": not flags and tree is not False and category != "industry",
            "review_flags": flags, "interpretation_notes": decisions,
            "source": f"https://api.nusmods.com/v2/2026-2027/modules/{code}.json"
        }
        if flags or decisions:
            review.append({"course": code, "flags": flags, "decisions": decisions, "text": text})
    if "CP3200" not in result:
        result["CP3200"] = {
            "code": "CP3200", "title": "Internship (completed credit only)", "units": 6,
            "level": 3000, "category": "industry", "ai_primary": False,
            "offered_semesters": [], "prerequisites": None, "corequisites": [],
            "preclusions": [], "raw_prerequisite": "", "raw_corequisite": "", "raw_preclusion": "",
            "selectable": False, "review_flags": [],
            "interpretation_notes": ["Credit value from official programme page; no claim of current-year offering."],
            "source": COHORT_URL
        }
    write_json(root / "data/courses.json", result)
    write_json(root / "data/review.json", {
        "status": "AI source-audited; team review still required before submission",
        "assumptions": ["Passed courses meet D-grade prerequisite thresholds.",
                        "Standard CS student has qualifying mathematics and English proficiency.",
                        "Programme-specific preclusion conditions resolved for single-degree CS; listed course preclusions retained."],
        "entries": review
    })
    blocked = sum(bool(c["review_flags"]) for c in result.values())
    print(f"Normalized {len(result)} courses; {blocked} blocked pending review.")
    return result
