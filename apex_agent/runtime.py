"""Codex CLI adapter. Capture tool events outside the writable audit workspace."""

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

from .schema import RESPONSE, validate
from .storage import write_json


def resolve_codex(binary="codex"):
    resolved = shutil.which(binary)
    if not resolved:
        raise ValueError("Codex CLI not found. Install Codex, run codex login, then apex doctor.")
    return resolved


def doctor(binary="codex"):
    executable = resolve_codex(binary)
    result = subprocess.run([executable, "exec", "--help"], capture_output=True, text=True, timeout=20)
    required = ("--json", "--output-schema", "--output-last-message", "--sandbox", "--ignore-user-config")
    missing = [flag for flag in required if flag not in result.stdout]
    if result.returncode or missing:
        raise ValueError(f"Codex CLI is incompatible; update it. Missing options: {', '.join(missing)}")
    auth = subprocess.run([executable, "login", "status"], capture_output=True, text=True, timeout=20)
    if auth.returncode:
        raise ValueError("Codex is not logged in. Run codex login first.")
    return executable


def stop_process(process):
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=3)


def command_records(events_path):
    commands, usage, failed = [], {}, []
    for line in Path(events_path).read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "item.completed":
            item = event.get("item", {})
            if item.get("type") == "command_execution":
                commands.append({"id": item.get("id", ""), "command": item.get("command", ""),
                                 "output": item.get("aggregated_output", ""),
                                 "exit_code": item.get("exit_code"), "status": item.get("status", "")})
        if event.get("type") == "turn.completed":
            usage = event.get("usage", {})
        if event.get("type") == "turn.failed":
            failed.append(str(event.get("error", "Codex turn failed")))
    return commands, usage, failed


class CodexRuntime:
    def __init__(self, binary="codex"):
        self.binary = resolve_codex(binary)

    def run(self, workspace, round_dir, prompt, timeout, model=None):
        workspace, round_dir = Path(workspace), Path(round_dir)
        round_dir.mkdir(parents=True, exist_ok=False)
        schema_file, result_file = round_dir / "schema.json", round_dir / "response.json"
        write_json(schema_file, RESPONSE)
        (round_dir / "prompt.txt").write_text(prompt)
        command = [self.binary, "--ask-for-approval", "never", "exec", "--ignore-user-config",
                   "--sandbox", "workspace-write", "--skip-git-repo-check", "--ephemeral",
                   "--json", "--color", "never", "--cd", str(workspace),
                   "--output-schema", str(schema_file), "--output-last-message", str(result_file),
                   "-c", "sandbox_workspace_write.network_access=false",
                   "-c", "features.multi_agent=false",
                   "-c", 'shell_environment_policy.inherit="core"',
                   "-c", 'shell_environment_policy.include_only=["PATH","HOME","TMPDIR","LANG","PYTHONDONTWRITEBYTECODE"]']
        if model:
            command.extend(["--model", model])
        command.append("-")
        events_file = round_dir / "events.jsonl"
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        started = time.monotonic()
        with events_file.open("w") as events, (round_dir / "stderr.log").open("w") as errors:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=events, stderr=errors,
                                       text=True, env=env, start_new_session=True)
            try:
                first_wait = True
                while True:
                    remaining = timeout - (time.monotonic() - started)
                    if remaining <= 0:
                        raise TimeoutError(f"Round exceeded {timeout:g} seconds; captured progress is saved")
                    try:
                        process.communicate(input=prompt if first_wait else None, timeout=min(15, remaining))
                        break
                    except subprocess.TimeoutExpired:
                        first_wait = False
                        print("  Apex is investigating; command evidence is being recorded…", flush=True)
            except BaseException:
                stop_process(process)
                raise
            finally:
                if process.stdin and not process.stdin.closed:
                    try:
                        process.stdin.close()
                    except OSError:
                        pass
        commands, usage, failures = command_records(events_file)
        if process.returncode or failures:
            raise RuntimeError(f"Codex round failed (exit {process.returncode}); see {round_dir / 'stderr.log'}")
        if not result_file.is_file():
            raise RuntimeError("Codex produced no structured result; see the round event log")
        try:
            payload = json.loads(result_file.read_text())
            validate(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(f"Invalid agent response: {exc}") from exc
        return payload, commands, usage
