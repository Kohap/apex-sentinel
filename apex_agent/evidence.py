"""Bind proposed findings to this round's actual tool results and unchanged source."""

import re
import shlex
from pathlib import Path

from .schema import GATES
from .storage import contained, digest


def inner_command(command):
    try:
        parts = shlex.split(command)
    except ValueError:
        return command.strip()
    if len(parts) >= 3 and Path(parts[0]).name in {"bash", "sh", "zsh"} and parts[1] in {"-c", "-lc"}:
        return parts[2].strip()
    return command.strip()


def assess(finding, workspace, commands, phase):
    errors, binding = [], None
    f = dict(finding)
    if not re.fullmatch(r"APEX-\d{3,}", f["id"]):
        errors.append("Finding ID must be APEX-001 or a higher numeric ID")
    if f["status"] != "confirmed":
        if f["status"] == "unverified" and not f["next_action"].strip():
            errors.append("Unverified finding needs a specific next action")
        if f["status"] == "dismissed" and not f["falsification"].strip():
            errors.append("Dismissal needs a falsification explanation")
        f["validation_errors"], f["evidence_binding"] = errors, binding
        return f
    if phase == "explore":
        errors.append("Requires a follow-up verification round before confirmation")
    for field in ("title", "preconditions", "expected", "actual", "impact", "falsification", "fix", "regression_test"):
        if len(f[field].strip()) < 12:
            errors.append(f"Missing substantive {field}")
    if not f["reproduction_steps"] or any(not x.strip() for x in f["reproduction_steps"]):
        errors.append("Reproduction steps are required")
    try:
        source = contained(Path(workspace) / "source", f["file"])
        lines = source.read_text(errors="replace").splitlines()
        excerpt = f["source_excerpt"]
        if f["line"] < 1 or not excerpt.strip() or not "\n".join(lines[f["line"] - 1:]).startswith(excerpt):
            errors.append("Source excerpt does not match the cited line")
    except (ValueError, OSError):
        errors.append("Source location is missing or outside the snapshot")
    for name in GATES:
        gate = f["gates"][name]
        if gate["result"] != "PASS" or len(gate["evidence"].strip()) < 12:
            errors.append(f"Gate {name} needs PASS and supporting evidence")
    proof = f["proof"]
    artifact_hash = None
    try:
        artifact = contained(workspace, proof["artifact"])
        if not proof["artifact"].startswith("artifacts/") or not artifact.is_file() or artifact.stat().st_size == 0:
            errors.append("Proof must reference a nonempty test under artifacts/")
        elif artifact.suffix not in {".py", ".js", ".mjs", ".cjs", ".ts", ".sh", ".sol", ".rs", ".go", ".rb", ".php", ".java"}:
            errors.append("Proof artifact must be executable test source, not a note or log")
        else:
            artifact_hash = digest(artifact.read_bytes())
    except (ValueError, OSError):
        errors.append("Proof artifact is missing or outside the workspace")
    matched = [c for c in commands if inner_command(c["command"]) == inner_command(proof["command"])]
    valid = [c for c in matched if c["exit_code"] == proof["exit_code"] == 0
             and len(proof["observation"].strip()) >= 12 and len(proof["control_observation"].strip()) >= 12
             and proof["observation"] != proof["control_observation"]
             and proof["observation"] in c["output"] and proof["control_observation"] in c["output"]]
    if not proof["artifact"] or proof["artifact"] not in proof["command"]:
        errors.append("The recorded reproduction command must name its test artifact")
    if not valid:
        errors.append("No successful captured command proves both the failure and legitimate-use control")
    elif artifact_hash:
        c = valid[-1]
        binding = {"command_id": c["id"], "command": c["command"], "exit_code": c["exit_code"],
                   "output_sha256": digest(c["output"].encode()), "artifact_sha256": artifact_hash}
    if errors:
        f["status"] = "unverified"
        f["next_action"] = "; ".join(errors)
    f["validation_errors"], f["evidence_binding"] = errors, binding
    return f
