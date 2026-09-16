import json
from pathlib import Path
import sys
import tempfile
from urllib.parse import quote
import unittest

from apex_agent.runtime import (
    GrokRuntime, grok_command_records, grok_session_commands, _exit_from_output,
)


RESPONSE = {
    "summary": "Grok adapter fixture only",
    "done": False,
    "coverage": [],
    "findings": [],
    "blockers": [],
    "next_steps": [],
}


class GrokRuntimeAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.binary = self.root / "fixture-grok"
        self._old_home = None

    def executable(self, body):
        self.binary.write_text(f"#!{sys.executable}\n" + body)
        self.binary.chmod(0o755)
        return GrokRuntime(str(self.binary))

    def test_streaming_bash_events_become_command_records(self):
        events = self.root / "events.jsonl"
        events.write_text("\n".join([
            json.dumps({"type": "usage", "usage": {"input_tokens": 4}}),
            json.dumps({
                "type": "tool_call", "toolCallId": "call-1", "toolName": "run_terminal_command",
                "rawInput": {"command": "python3 artifacts/check.py"},
            }),
            json.dumps({
                "type": "tool_call_update", "toolCallId": "call-1", "status": "completed",
                "rawOutput": {
                    "type": "Bash", "command": "python3 artifacts/check.py",
                    "output_for_prompt": "exit: 0\nok\n", "exit_code": 0,
                },
                "content": [{"type": "content", "content": {"type": "text", "text": "ok\n"}}],
            }),
            json.dumps({"type": "end", "stopReason": "end_turn"}),
        ]))
        commands, usage, failed = grok_command_records(events)
        self.assertEqual(commands[0]["command"], "python3 artifacts/check.py")
        self.assertEqual(commands[0]["exit_code"], 0)
        self.assertIn("ok", commands[0]["output"])
        self.assertEqual(usage["input_tokens"], 4)
        self.assertEqual(failed, [])

    def test_session_chat_history_becomes_command_records(self):
        encoded = quote(str(self.workspace.resolve()), safe="")
        session = self.home / ".grok" / "sessions" / encoded / "sess-1"
        session.mkdir(parents=True)
        (session / "chat_history.jsonl").write_text("\n".join([
            json.dumps({
                "type": "assistant",
                "tool_calls": [{
                    "id": "call-9", "name": "run_terminal_command",
                    "arguments": json.dumps({"command": "python3 hello.py"}),
                }],
            }),
            json.dumps({"type": "tool_result", "tool_call_id": "call-9", "content": "exit: 0\nok\n"}),
        ]))
        commands = grok_session_commands(self.workspace, "sess-1", home=self.home)
        self.assertEqual(commands[0]["command"], "python3 hello.py")
        self.assertEqual(commands[0]["exit_code"], 0)
        self.assertEqual(_exit_from_output("exit: 2\nfail"), 2)

    def test_process_adapter_reads_structured_result_and_session_command(self):
        runtime = self.executable(r'''
import json, os, sys
from pathlib import Path
from urllib.parse import quote
args = sys.argv[1:]
prompt = Path(args[args.index("--prompt-file") + 1]).read_text()
assert "adapter fixture prompt" in prompt
cwd = Path(args[args.index("--cwd") + 1])
assert args[args.index("--sandbox") + 1] == "off"
assert "--json-schema" in args
home = Path(os.environ["HOME"])
session_id = "11111111-1111-1111-1111-111111111111"
session = home / ".grok" / "sessions" / quote(str(cwd.resolve()), safe="") / session_id
session.mkdir(parents=True)
(session / "chat_history.jsonl").write_text("\n".join([
    json.dumps({"type": "assistant", "tool_calls": [{"id": "c1", "name": "run_terminal_command",
        "arguments": json.dumps({"command": "python3 artifacts/check.py"})}]}),
    json.dumps({"type": "tool_result", "tool_call_id": "c1", "content": "exit: 0\nadapter fixture output\n"}),
]) + "\n")
payload = {"summary": "Adapter fixture only", "done": False, "coverage": [],
           "findings": [], "blockers": [], "next_steps": []}
print(json.dumps({"text": json.dumps(payload), "sessionId": session_id, "structuredOutput": payload,
                  "usage": {"input_tokens": 3}}))
''')
        import os
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = str(self.home)

        def restore_home():
            if old_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = old_home

        self.addCleanup(restore_home)
        result, commands, usage = runtime.run(self.workspace, self.root / "round", "adapter fixture prompt", 10)
        self.assertEqual(result["summary"], "Adapter fixture only")
        self.assertEqual(commands[0]["output"], "exit: 0\nadapter fixture output\n")
        self.assertEqual(usage, {"input_tokens": 3})

    def test_process_timeout_is_enforced(self):
        runtime = self.executable("import time\ntime.sleep(10)\n")
        with self.assertRaises(TimeoutError):
            runtime.run(self.workspace, self.root / "round", "prompt", .15)
        self.assertTrue((self.root / "round/stderr.log").exists())

    def test_invalid_structured_result_is_rejected(self):
        runtime = self.executable('''import json
print(json.dumps({"structuredOutput": {"done": True}, "sessionId": ""}))
''')
        with self.assertRaisesRegex(RuntimeError, "Invalid agent response"):
            runtime.run(self.workspace, self.root / "round", "prompt", 10)

    def test_nonzero_process_exit_cannot_complete(self):
        runtime = self.executable("import sys\nsys.exit(7)\n")
        with self.assertRaisesRegex(RuntimeError, "exit 7"):
            runtime.run(self.workspace, self.root / "round", "prompt", 10)


if __name__ == "__main__":
    unittest.main()
