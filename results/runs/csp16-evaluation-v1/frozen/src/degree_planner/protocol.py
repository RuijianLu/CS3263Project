"""Proposal evaluation: freeze input artifacts so runs cannot mix protocols."""
from __future__ import annotations
import hashlib
import json
from .policy import MAX_UNITS
from .collect import read_json

def fingerprints(root, split):
    paths = ["data/courses.json", "data/requirements.json", f"data/benchmark/{split}.jsonl",
             "data/benchmark/gold.jsonl", "prompts/direct.txt", "prompts/translate.txt",
             "prompts/plan.schema.json", "prompts/spec.schema.json", "data/benchmark/manifest.json",
             "src/degree_planner/csp.py", "src/degree_planner/solver.py", "src/degree_planner/checker.py",
             "src/degree_planner/schemas.py", "src/degree_planner/policy.py",
             "src/degree_planner/codex_runner.py", "src/degree_planner/evaluate.py",
             "src/degree_planner/protocol.py"]
    return {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths}

def verify_manifest(root, manifest, split, config=None):
    if manifest["split"] != split:
        raise ValueError("A run name cannot mix development and evaluation cases")
    current = fingerprints(root, split)
    if "artifact_sha256" in manifest:
        if current != manifest["artifact_sha256"]:
            raise ValueError("Frozen inputs changed; prepare a separately named experiment")
    else:
        # Initial pilot predated the extended manifest; its three original hashes remain checked.
        for key, path in [("catalogue_sha256","data/courses.json"),
                          ("requirements_sha256","data/requirements.json"),
                          ("benchmark_sha256",f"data/benchmark/{split}.jsonl")]:
            if current[path] != manifest[key]:
                raise ValueError("Pilot input snapshot changed")
    if config is not None and config != manifest["configuration"]:
        raise ValueError("Experiment settings changed within a run")


def require_current_benchmark(root):
    """Refuse to reuse historical labels after changing the workload policy."""
    answers = [json.loads(line) for line in (root / "data/benchmark/gold.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not answers or any(a["spec"]["max_units"] != MAX_UNITS for a in answers):
        raise ValueError("The saved benchmark is historical and uses the previous workload cap. A new 16-unit benchmark is required before comparison or relabelling. Use verify for local CSP validation.")
    from .benchmark import VERSION, source_hashes
    manifest = read_json(root / "data/benchmark/manifest.json")
    if manifest.get("version") != VERSION or not manifest.get("local_validation", {}).get("valid"):
        raise ValueError("The current benchmark has no completed local validation")
    if manifest["source_sha256"] != source_hashes(root):
        raise ValueError("Benchmark source facts or solver implementation changed; revalidate before comparison")
    for path, digest in manifest["artifact_sha256"].items():
        if hashlib.sha256((root / "data/benchmark" / path).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Validated benchmark artifact changed: {path}")
