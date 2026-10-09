"""Meaningful protocol checks without spending any model calls."""
import copy
from pathlib import Path
import pytest
from degree_planner.collect import read_json
from degree_planner.protocol import fingerprints, verify_manifest
from degree_planner.codex_runner import prepare_prompt
from degree_planner.benchmark import load_jsonl
from degree_planner.evaluate import evaluate

ROOT = Path(__file__).resolve().parents[1]

def test_manifest_rejects_changed_settings_and_wrong_split():
    config=read_json(ROOT/"experiment.json")
    manifest={"split":"test","configuration":config,"artifact_sha256":fingerprints(ROOT,"test")}
    verify_manifest(ROOT,manifest,"test",config)
    modified=copy.deepcopy(config)
    modified["reasoning_effort"]="high"
    with pytest.raises(ValueError): verify_manifest(ROOT,manifest,"test",modified)
    with pytest.raises(ValueError): verify_manifest(ROOT,manifest,"dev",config)

def test_manifest_rejects_changed_input():
    manifest={"split":"test","configuration":{},
              "artifact_sha256":fingerprints(ROOT,"test")}
    manifest["artifact_sha256"]["data/courses.json"]="changed"
    with pytest.raises(ValueError): verify_manifest(ROOT,manifest,"test")

def test_model_prompt_excludes_gold_label_and_reference():
    case=load_jsonl(ROOT/"data/benchmark/test.jsonl")[0]
    for approach in ("direct","assisted"):
        prompt=prepare_prompt(ROOT,case,approach)
        assert case["request"] in prompt
        assert "reference_plan" not in prompt
        assert "label_rationale" not in prompt
        assert "gold.jsonl" not in prompt
