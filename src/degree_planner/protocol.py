"""Proposal evaluation: freeze input artifacts so runs cannot mix protocols."""
from __future__ import annotations
import hashlib
from .collect import read_json

def fingerprints(root, split):
    paths = ["data/courses.json", "data/requirements.json", f"data/benchmark/{split}.jsonl",
             "data/benchmark/gold.jsonl", "prompts/direct.txt", "prompts/translate.txt",
             "prompts/plan.schema.json", "prompts/spec.schema.json"]
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
