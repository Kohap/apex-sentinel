"""CLI runtime adapters. Capture tool events outside the writable audit workspace."""

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
from urllib.parse import quote

from .schema import RESPONSE, validate
from .storage import write_json

GROK_REQUIRED = (
    "--prompt-file", "--json-schema", "--output-format", "--always-approve", "--cwd", "--sandbox",
)
CODEX_REQUIRED = (
    "--json", "--output-schema", "--output-last-message", "--sandbox", "--ignore-user-config",
)


def resolve_codex(binary="codex"):
    resolved = shutil.which(binary)
    if not resolved:
        raise ValueError("Codex CLI not found. Install Codex, run codex login, then apex doctor.")
    return resolved


def resolve_grok(binary="grok"):
    resolved = shutil.which(binary)
    if not resolved:
        raise ValueError(
            "Grok CLI not found. Install @xai-official/grok, set XAI_API_KEY, then apex doctor --runtime grok."
        )
    return resolved


def doctor(binary="codex"):
    executable = resolve_codex(binary)
    result = subprocess.run([executable, "exec", "--help"], capture_output=True, text=True, timeout=20)
    missing = [flag for flag in CODEX_REQUIRED if flag not in result.stdout]
    if result.returncode or missing:
        raise ValueError(f"Codex CLI is incompatible; update it. Missing options: {', '.join(missing)}")
    auth = subprocess.run([executable, "login", "status"], capture_output=True, text=True, timeout=20)
    if auth.returncode:
        raise ValueError("Codex is not logged in. Run codex login first.")
    return executable


def doctor_grok(binary="grok"):
    executable = resolve_grok(binary)
    result = subprocess.run([executable, "--help"], capture_output=True, text=True, timeout=20)
    missing = [flag for flag in GROK_REQUIRED if flag not in (result.stdout + result.stderr)]
    if result.returncode or missing:
        raise ValueError(f"Grok CLI is incompatible; update it. Missing options: {', '.join(missing)}")
    models = subprocess.run([executable, "models"], capture_output=True, text=True, timeout=30)
    if models.returncode:
        raise ValueError("Grok is not authenticated. Set XAI_API_KEY or run grok login.")
    return executable


def doctor_auto(grok_binary="grok", codex_binary="codex"):
    """Prefer Grok CLI when it is installed and authenticated; otherwise Codex."""
    grok_error = codex_error = None
    try:
        return "grok", doctor_grok(grok_binary)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        grok_error = str(exc)
    try:
        return "codex", doctor(codex_binary)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        codex_error = str(exc)
    raise ValueError(
        "No usable audit runtime. "
        f"Grok: {grok_error or 'unavailable'}. Codex: {codex_error or 'unavailable'}."
    )


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


def grok_command_records(events_path):
    """Parse Grok streaming-json / session updates for completed bash tool calls."""
    commands, usage, failed, pending = [], {}, [], {}
    path = Path(events_path)
    if not path.is_file():
        return commands, usage, failed
    for line in path.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        event = _unwrap_session_update(event)
        kind = event.get("type") or event.get("sessionUpdate") or ""
        if kind == "usage":
            usage = event.get("usage") or usage
        elif kind == "tool_call":
            pending[event.get("toolCallId") or event.get("tool_call_id") or ""] = event
        elif kind == "tool_call_update":
            record = _grok_bash_record(event, pending)
            if record and event.get("status") == "completed":
                commands.append(record)
        elif kind in {"end", "turn_completed"}:
            usage = event.get("usage") or usage
        elif kind in {"error", "turn_failed"}:
            failed.append(str(event.get("error") or event.get("message") or "Grok turn failed"))
    return commands, usage, failed


def grok_session_commands(workspace, session_id, home=None):
    """Read completed bash calls from a Grok session transcript."""
    if not session_id:
        return []
    encoded = quote(str(Path(workspace).resolve()), safe="")
    session = Path(home or Path.home()) / ".grok" / "sessions" / encoded / session_id
    history = session / "chat_history.jsonl"
    updates = session / "updates.jsonl"
    if history.is_file():
        commands = _commands_from_chat_history(history)
        if commands:
            return commands
    if updates.is_file():
        commands, _, _ = grok_command_records(updates)
        return commands
    return []


def grok_session_events(workspace, session_id, home=None):
    if not session_id:
        return None
    encoded = quote(str(Path(workspace).resolve()), safe="")
    updates = Path(home or Path.home()) / ".grok" / "sessions" / encoded / session_id / "updates.jsonl"
    return updates if updates.is_file() else None


def _unwrap_session_update(event):
    params = event.get("params") if isinstance(event.get("params"), dict) else None
    update = (params or event).get("update")
    if isinstance(update, dict):
        merged = dict(update)
        if "type" not in merged and "sessionUpdate" in merged:
            merged["type"] = merged["sessionUpdate"]
        return merged
    return event


def _grok_bash_record(event, pending):
    raw = event.get("rawOutput") or event.get("raw_output") or {}
    if not isinstance(raw, dict):
        raw = {}
    tool_id = event.get("toolCallId") or event.get("tool_call_id") or ""
    origin = pending.get(tool_id) or {}
    raw_input = origin.get("rawInput") or origin.get("raw_input") or {}
    command = raw.get("command") or (raw_input.get("command") if isinstance(raw_input, dict) else "") or ""
    if raw.get("type") not in {None, "Bash"} and origin.get("toolName") not in {
        None, "run_terminal_command", "run_terminal_cmd",
    }:
        if not command:
            return None
    output = raw.get("output_for_prompt")
    if not output:
        content = event.get("content") or []
        texts = []
        for item in content:
            inner = item.get("content", item) if isinstance(item, dict) else {}
            if isinstance(inner, dict) and inner.get("text"):
                texts.append(inner["text"])
        output = "".join(texts)
    if event.get("status") != "completed" and not command:
        return None
    if not command:
        return None
    exit_code = raw.get("exit_code")
    if exit_code is None:
        exit_code = _exit_from_output(output or "")
    return {
        "id": tool_id,
        "command": command,
        "output": output or "",
        "exit_code": exit_code,
        "status": event.get("status") or "completed",
    }


def _commands_from_chat_history(path):
    commands, pending = [], {}
    for line in Path(path).read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for call in event.get("tool_calls") or []:
                if call.get("name") not in {"run_terminal_command", "run_terminal_cmd"}:
                    continue
                try:
                    args = json.loads(call.get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                pending[call.get("id") or ""] = args.get("command") or ""
        elif event.get("type") == "tool_result":
            tool_id = event.get("tool_call_id") or ""
            command = pending.get(tool_id, "")
            if not command:
                continue
            content = event.get("content") or ""
            if isinstance(content, list):
                content = "".join(
                    (part.get("text") if isinstance(part, dict) else str(part)) for part in content
                )
            content = content if isinstance(content, str) else str(content)
            commands.append({
                "id": tool_id,
                "command": command,
                "output": content,
                "exit_code": _exit_from_output(content),
                "status": "completed",
            })
    return commands


def _exit_from_output(output):
    first = (output or "").splitlines()[0] if output else ""
    if first.lower().startswith("exit:"):
        try:
            return int(first.split(":", 1)[1].strip().split()[0])
        except (ValueError, IndexError):
            return 0
    return 0


def _load_json_object(text):
    text = text.strip()
    if not text:
        raise json.JSONDecodeError("empty", text, 0)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


class CodexRuntime:
    def __init__(self, binary="codex"):
        self.binary = resolve_codex(binary)
        self.name = "codex"

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


class GrokRuntime:
    """Headless Grok CLI adapter (`grok -p` / `--prompt-file`)."""

    def __init__(self, binary="grok", sandbox="off", max_turns=40):
        self.binary = resolve_grok(binary)
        self.name = "grok"
        self.sandbox = sandbox
        self.max_turns = max_turns

    def run(self, workspace, round_dir, prompt, timeout, model=None):
        workspace, round_dir = Path(workspace), Path(round_dir)
        round_dir.mkdir(parents=True, exist_ok=False)
        schema_file, result_file = round_dir / "schema.json", round_dir / "response.json"
        prompt_file = round_dir / "prompt.txt"
        write_json(schema_file, RESPONSE)
        prompt_file.write_text(prompt)
        command = [
            self.binary, "--prompt-file", str(prompt_file), "--cwd", str(workspace),
            "--always-approve", "--permission-mode", "bypassPermissions",
            "--no-subagents", "--no-plan", "--disable-web-search", "--verbatim",
            "--sandbox", self.sandbox, "--max-turns", str(self.max_turns),
            "--json-schema", json.dumps(RESPONSE),
            "--output-format", "json",
            "--tools", "run_terminal_command,read_file,search_replace,list_dir,grep",
        ]
        if model:
            command.extend(["-m", model])
        env = dict(os.environ)
        env.pop("GROK_AGENT", None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["GROK_SANDBOX"] = self.sandbox
        started = time.monotonic()
        stdout_file = round_dir / "stdout.json"
        with stdout_file.open("w") as stdout, (round_dir / "stderr.log").open("w") as errors:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=errors,
                                       text=True, env=env, start_new_session=True)
            try:
                while True:
                    remaining = timeout - (time.monotonic() - started)
                    if remaining <= 0:
                        raise TimeoutError(f"Round exceeded {timeout:g} seconds; captured progress is saved")
                    try:
                        process.wait(timeout=min(15, remaining))
                        break
                    except subprocess.TimeoutExpired:
                        print("  Apex is investigating; command evidence is being recorded…", flush=True)
            except BaseException:
                stop_process(process)
                raise
        if process.returncode:
            raise RuntimeError(f"Grok round failed (exit {process.returncode}); see {round_dir / 'stderr.log'}")
        try:
            raw = _load_json_object(stdout_file.read_text())
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Grok produced no JSON result; see {stdout_file}") from exc
        payload = raw.get("structuredOutput")
        if payload is None:
            try:
                payload = json.loads(raw["text"]) if isinstance(raw.get("text"), str) else raw
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                raise RuntimeError(f"Grok produced no structured result: {exc}") from exc
        try:
            validate(payload)
        except ValueError as exc:
            raise RuntimeError(f"Invalid agent response: {exc}") from exc
        write_json(result_file, payload)
        session_id = raw.get("sessionId") or ""
        (round_dir / "session_id.txt").write_text(session_id)
        usage = raw.get("usage") or {}
        commands = grok_session_commands(workspace, session_id)
        events = grok_session_events(workspace, session_id)
        if events:
            (round_dir / "events.jsonl").write_text(events.read_text(errors="replace"))
            if not commands:
                commands, streamed_usage, failures = grok_command_records(events)
                usage = usage or streamed_usage
                if failures:
                    raise RuntimeError(f"Grok round failed: {failures[0]}")
        elif not (round_dir / "events.jsonl").exists():
            (round_dir / "events.jsonl").write_text("")
        return payload, commands, usage
