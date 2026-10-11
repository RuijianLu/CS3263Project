"""Proposal sub-problems 1-3: collect real course facts and their provenance."""
from __future__ import annotations
from .policy import MAX_UNITS
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, NavigableString, Tag

YEAR = "2026-2027"
COHORT_URL = "https://www.comp.nus.edu.sg/cug/per-cohort/cs/cs-26-27/"
FOCUS_URL = "https://www.comp.nus.edu.sg/programmes/ug/focus/"
FOUNDATION = ["CS1231S", "CS2030S", "CS2040S", "CS2100", "CS2101",
              "CS2103T", "CS2106", "CS2109S", "CS3230"]
MATH = ["MA1521", "MA1522", "ST2334"]
CODE = re.compile(r"\b[A-Z]{2,3}\d{4}[A-Z]{0,2}\b")

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def fetch(url: str) -> bytes:
    with urlopen(Request(url, headers={"User-Agent": "CS3263-degree-planning-course-project"}), timeout=30) as response:
        return response.read()

def leaf_codes(tree):
    if isinstance(tree, str):
        return {tree.split(":")[0]} if CODE.fullmatch(tree.split(":")[0]) else set()
    if isinstance(tree, list):
        return set().union(*(leaf_codes(t) for t in tree)) if tree else set()
    if isinstance(tree, dict):
        return set().union(*(leaf_codes(t) for t in tree.values()))
    return set()

def ai_codes(html: bytes):
    soup = BeautifulSoup(html, "html.parser")
    heading = next(h for h in soup.find_all(["h3", "h4"])
                   if h.get_text(strip=True) == "Artificial Intelligence")
    parts = []
    for element in heading.next_elements:
        if isinstance(element, Tag) and element.name in {"h3", "h4"} and element is not heading:
            break
        if isinstance(element, NavigableString):
            parts.append(str(element))
    section = "\n".join(parts)
    primary_text, elective_text = section.split("Primaries", 1)[1].split("Electives", 1)
    return sorted(set(CODE.findall(primary_text))), sorted(set(CODE.findall(elective_text)))

def collect(root: Path, refresh: bool = False):
    raw = root / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    provenance = {}
    def snapshot(url, name):
        path = raw / name
        if refresh or not path.exists():
            path.write_bytes(fetch(url))
        payload = path.read_bytes()
        provenance[name] = {"url": url, "file": path.relative_to(root).as_posix(),
                            "sha256": hashlib.sha256(payload).hexdigest()}
        return payload

    snapshot(COHORT_URL, "cs-26-27.html")
    primaries, electives = ai_codes(snapshot(FOCUS_URL, "focus.html"))
    summaries = json.loads(snapshot(f"https://api.nusmods.com/v2/{YEAR}/moduleList.json", "moduleList.json"))
    available = {m["moduleCode"] for m in summaries}
    wanted = set(FOUNDATION + MATH + primaries + electives + ["CP3200"])
    records, missing = {}, set()
    while wanted:
        batch = sorted(wanted - records.keys() - missing)
        if not batch:
            break
        missing.update(set(batch) - available)
        batch = [c for c in batch if c in available]
        def get(code):
            url = f"https://api.nusmods.com/v2/{YEAR}/modules/{code}.json"
            return code, json.loads(snapshot(url, code + ".json"))
        with ThreadPoolExecutor(max_workers=4) as pool:
            for code, record in pool.map(get, batch):
                records[code] = record
        wanted = set()
        for record in records.values():
            wanted.update(leaf_codes(record.get("prereqTree")))
            wanted.update(CODE.findall(record.get("corequisite", "")))
        wanted -= records.keys() | missing
        print(f"Collected {len(records)} course records; {len(wanted)} dependencies pending.", flush=True)

    requirements = {
        "schema_version": 1, "admission_cohort": 2026, "academic_year": YEAR,
        "foundation": FOUNDATION, "mathematics": MATH,
        "ai_primaries": primaries, "ai_electives": electives,
        "breadth_min_units": 32, "breadth_level4000_min_units": 12,
        "ai_primary_min_courses": 3, "ai_primary_level4000_min_courses": 1,
        "industry_min_units": 6, "industry_max_units": 12,
        "non_industry_cp_max_units": 12,
        "programme_level1000_4000_min_fraction": 0.8,
        "corequisite_pairs": [["CS2101", "CS2103T"]],
        "max_units_per_semester": MAX_UNITS,
        "sources": [COHORT_URL, FOCUS_URL],
        "interpretation": [
            "Foundation and mathematics credits cannot also earn breadth credits.",
            "A foundation course in AI primaries may satisfy the focus count without additional credits.",
            "The 12 upper-level units are within breadth/depth, including credited industry courses.",
            "Initial pathway: completed CP3200 (6 units), no dissertation substitution.",
            "Plan normal Semesters 1 and 2; repeat AY2026/27 offerings.",
            "Common Curriculum and Unrestricted Electives are not audited."
        ]
    }
    write_json(root / "data/requirements.json", requirements)
    write_json(root / "data/raw/course_records.json", records)
    write_json(root / "data/sources.json", {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": sorted(provenance.values(), key=lambda p: p["file"]),
        "missing_course_codes": sorted(missing),
        "review_status": "Programme groups transcribed from official page; course review recorded in courses.json."
    })
    print(f"Saved {len(records)} real courses. Missing current-year codes: {sorted(missing)}")

if __name__ == "__main__":
    collect(Path.cwd())
