"""Proposal evaluation: subscription-backed isolated direct and translation runs."""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from .collect import read_json, write_json
from .benchmark import load_jsonl
from .schemas import write_schemas
from .protocol import fingerprints, verify_manifest, require_current_benchmark

# Capabilities are disabled rather than relying on a 'read-only' shell alone.
DISABLED = ["shell_tool", "unified_exec", "apps", "plugins", "multi_agent", "memories",
            "browser_use", "browser_use_external", "computer_use", "image_generation",
            "view_image", "goals", "sleep_tool", "skill_search", "hooks",
            "code_mode", "code_mode_host", "remote_plugin", "workspace_dependencies",
            "in_app_browser", "in_app_chat", "in_app_local_automation",
            "skill_mcp_dependency_install"]

def context(root):
    courses = read_json(root / "data/courses.json")
    req = read_json(root / "data/requirements.json")
    # This contains domain facts only, never benchmark gold specifications or plans.
    rows = [{k: c[k] for k in ["code", "units", "level", "category", "ai_primary",
                              "offered_semesters", "prerequisites", "corequisites",
                              "preclusions", "selectable"]} for c in courses.values()]
    def members(predicate):
        return ", ".join(sorted(c for c, v in courses.items() if predicate(c, v))) or "(empty set)"
    foundation = ", ".join(req["foundation"])
    mathematics = ", ".join(req["mathematics"])
    rule_text = (
        f"Mandatory foundation courses: {foundation}. Mandatory mathematics courses: {mathematics}.\n"
        "Complete the AI focus area and Programme Requirements. Each passed course meets the D-grade threshold.\n"
        "A group counts completed plus newly selected distinct members. Listed groups are:\n"
        f"breadth: at least 32 units from {members(lambda c,v: v['category'] in ['breadth','industry'])}.\n"
        f"breadth_upper: at least 12 units from {members(lambda c,v: v['category'] in ['breadth','industry'] and v['level']>=4000)}.\n"
        f"ai_primary: at least 3 courses from {members(lambda c,v: v['ai_primary'])}.\n"
        f"ai_upper: at least 1 course from {members(lambda c,v: v['ai_primary'] and v['level']>=4000)}.\n"
        "industry: at least 6 and at most 12 units from CP3200, which is already completed.\n"
        f"cp_non_industry: at most 12 units from {members(lambda c,v: v['category']=='breadth' and c.startswith('CP'))}.\n"
        f"programme_lower: at least 64 units from {members(lambda c,v: v['category'] in ['foundation','mathematics','breadth','industry'] and v['level']<=4000)}.\n"
        "programme_lower represents 80% of the fixed 80-unit Programme requirement.\n"
        "Foundation CS2109S can satisfy the focus counts, but its credits do not count toward breadth.\n"
        "CS2101 and CS2103T must be newly enrolled together in the same semester.\n"
        "A course with selectable=false cannot be newly enrolled but may appear in the supplied completed record.\n"
        "Missing prerequisite codes cannot be newly taken in this catalogue; an OR branch using an available alternative may be used.\n"
        "Other focus-area courses are outside this benchmark catalogue. The catalogue includes level-5000 AI electives; the 64-unit lower-level rule still applies.\n"
        "Standard mathematics, English and CS programme-entry conditions are satisfied. Internship eligibility is historical and not audited.\n"
    )
    return rule_text + "\nCOURSE FACTS:\n" + json.dumps(rows, separators=(",", ":"))

def prepare_prompt(root, case, approach):
    instruction = (root / f"prompts/{'direct' if approach=='direct' else 'translate'}.txt").read_text(encoding="utf-8")
    return instruction + "\nDOMAIN:\n" + context(root) + "\nREQUEST:\n" + case["request"]

def run_one(root, case, approach, config, destination):
    codex = shutil.which("codex")
    if not codex:
        raise RuntimeError("Codex CLI is not installed; no model call was made.")
    destination.mkdir(parents=True, exist_ok=True)
    record_path = destination / "record.json"
    if record_path.exists():
        raise RuntimeError("An attempt already exists. Choose a different run name; do not overwrite scored attempts.")
    prompt = prepare_prompt(root, case, approach)
    (destination / "prompt.txt").write_text(prompt, encoding="utf-8")
    response_path = destination / "response.json"
    schema = root / f"prompts/{'plan' if approach=='direct' else 'spec'}.schema.json"
    sessions = root / "results/.sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="case-", dir=sessions)).resolve()
    if not workspace.is_relative_to(sessions.resolve()):
        raise RuntimeError("Unexpected session directory")
    cmd = [codex, "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
           "--sandbox", "read-only", "--json", "--color", "never",
           "--model", config["model"], "--output-schema", str(schema),
           "--output-last-message", str(response_path), "--cd", str(workspace),
           "-c", f'model_reasoning_effort="{config["reasoning_effort"]}"',
           "-c", 'web_search="disabled"', "-c", "project_doc_max_bytes=0",
           "-c", "mcp_servers={}", "-"]
    for feature in DISABLED:
        cmd[2:2] = ["--disable", feature]
    started = time.monotonic()
    record = {"case_id": case["id"], "approach": approach, "model": config["model"],
              "reasoning_effort": config["reasoning_effort"],
              "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
              "status": "running", "usage": None, "tool_items": [], "attempt": 1}
    write_json(record_path, record)  # Reserve the attempt even if the process is interrupted.
    try:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(prompt.encode("utf-8"), timeout=config["timeout_seconds"])
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            record["status"] = "timeout"
        (destination / "events.jsonl").write_bytes(stdout)
        (destination / "stderr.txt").write_bytes(stderr)
        events = []
        for line in stdout.decode("utf-8", errors="replace").splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: continue
        for event in events:
            if event.get("type") == "turn.completed":
                record["usage"] = event.get("usage")
            item = event.get("item", {})
            if event.get("type") == "item.completed" and item.get("type") not in {"agent_message", "reasoning", "error"}:
                record["tool_items"].append(item.get("type", "unrecognised"))
        if record["tool_items"]:
            record["status"] = "tool_violation"
        elif record["status"] != "timeout":
            record["status"] = "ok" if process.returncode == 0 and response_path.exists() else "execution_error"
        record["exit_code"] = process.returncode
        if record["status"] == "ok":
            try: json.loads(response_path.read_text(encoding="utf-8"))
            except (ValueError, OSError): record["status"] = "invalid_json"
    except Exception as exc:
        record["status"] = "execution_error"
        record["error"] = str(exc)
    finally:
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        write_json(record_path, record)
        # Only remove the exact verified directory allocated for this case.
        shutil.rmtree(workspace)
    return record

def run(root, split="dev", limit=None, run_name="initial", approaches=("direct","assisted")):
    require_current_benchmark(root)
    config = read_json(root / "experiment.json")
    if config["attempts_per_case"] != 1:
        raise ValueError("Initial protocol allows one attempt per case")
    write_schemas(root)
    cases = load_jsonl(root / f"data/benchmark/{split}.jsonl")
    if limit is not None:
        if not 1 <= limit <= len(cases):
            raise ValueError("Limit must select at least one case and cannot exceed the split size")
        cases = cases[:limit]
    case_ids = [case["id"] for case in cases]
    base = root / "results/runs" / run_name
    if not base.resolve().is_relative_to((root / "results/runs").resolve()):
        raise ValueError("Run name must stay within results/runs")
    base.mkdir(parents=True, exist_ok=True)
    if not (base / "manifest.json").exists():
        write_json(base / "manifest.json", {
            "configuration": config, "split": split, "case_ids": case_ids,
            "artifact_sha256": fingerprints(root, split),
            "cli_version": subprocess.check_output([shutil.which("codex"), "--version"], text=True).strip(),
            "catalogue_sha256": hashlib.sha256((root / "data/courses.json").read_bytes()).hexdigest(),
            "requirements_sha256": hashlib.sha256((root / "data/requirements.json").read_bytes()).hexdigest(),
            "benchmark_sha256": hashlib.sha256((root / f"data/benchmark/{split}.jsonl").read_bytes()).hexdigest(),
            "protocol": "Fresh session; tools disabled and audited; no repairs or retries; subscription authentication."
        })
    manifest = read_json(base / "manifest.json")
    verify_manifest(root, manifest, split, config)
    if manifest.get("case_ids", case_ids) != case_ids:
        raise ValueError("Selected cases changed within a run; choose a separate run name")
    for case in cases:
        for approach in approaches:
            destination = base / f"{case['id']}-{approach}"
            if (destination / "record.json").exists():
                print(f"Existing attempt retained: {case['id']} {approach}", flush=True)
                continue
            record = run_one(root, case, approach, config, destination)
            print(f"{case['id']} {approach}: {record['status']} ({record['elapsed_seconds']}s)", flush=True)
            if record["status"] in {"execution_error","tool_violation"}:
                print("Batch stopped; inspect saved diagnostics before continuing.", flush=True)
                return False
    return True
