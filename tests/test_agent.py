import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from apex_agent.engine import create_run, run_agent
from apex_agent.evidence import assess
from apex_agent.runtime import command_records
from apex_agent.schema import GATES, validate
from apex_agent.storage import contained, load_json, snapshot, snapshot_unchanged


SOURCE = 'def get_invoice(user, invoice):\n    return invoice\n'
COMMAND = "python3 artifacts/reproduce.py"
OUTPUT = "unauthorized access reproduced\nlegitimate owner access succeeds\n"


def finding():
    return {
        "id": "APEX-001", "title": "Invoice access does not enforce ownership", "status": "confirmed",
        "severity": "medium", "file": "app.py", "line": 2, "source_excerpt": "    return invoice",
        "preconditions": "Two separate customer accounts and one private invoice exist.",
        "expected": "Only the invoice owner can read its contents.",
        "actual": "A different account can read the private invoice.",
        "impact": "One other customer's invoice was exposed in the local fixture.",
        "reproduction_steps": ["Create two test accounts.", "Run the reproduction against the real function."],
        "proof": {"artifact": "artifacts/reproduce.py", "command": COMMAND, "exit_code": 0,
                  "observation": "unauthorized access reproduced", "control_observation": "legitimate owner access succeeds"},
        "falsification": "Checked whether an ownership guard exists before the function returns.",
        "fix": "Check the authenticated caller against the invoice owner before returning it.",
        "regression_test": "Reject non-owner reads and continue allowing the real owner's reads.",
        "next_action": "", "gates": {g: {"result": "PASS", "evidence": "The fixture output and source establish this condition."} for g in GATES},
    }


def payload(findings=None, done=True):
    return {"summary": "Scoped invoice access review.", "done": done,
            "findings": [finding()] if findings is None else findings,
            "coverage": [{"surface": "invoice reads", "file": "app.py", "status": "tested", "details": "Exercised owner and non-owner paths."}],
            "blockers": [], "next_steps": []}


def commands():
    return [{"id": "item_1", "command": f"/bin/zsh -lc '{COMMAND}'", "exit_code": 0,
             "output": OUTPUT, "status": "completed"}]


class FakeRuntime:
    def __init__(self, result=None, failure=None, mutate=False):
        self.result = result or payload()
        self.failure, self.mutate, self.calls = failure, mutate, 0

    def run(self, workspace, round_dir, prompt, timeout, model):
        self.calls += 1
        round_dir.mkdir(parents=True)
        if self.failure:
            raise self.failure
        if self.mutate:
            (workspace / "source/app.py").write_text("changed source")
        (workspace / "artifacts/reproduce.py").write_text("print('test fixture')\n")
        return copy.deepcopy(self.result), commands(), {"input_tokens": 10, "output_tokens": 20}


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "app.py").write_text(SOURCE)
        self.run = self.root / "audit"

    def init(self):
        return create_run(self.repo, self.run, "invoice access")

    def evidence_workspace(self):
        self.init()
        workspace = self.run / "workspace"
        (workspace / "artifacts/reproduce.py").write_text("print('test fixture')\n")
        return workspace

    def test_snapshot_excludes_credentials_symlinks_and_preserves_original(self):
        (self.repo / ".env").write_text("fake secret")
        (self.repo / "outside.py").symlink_to(self.root / "unrelated.py")
        state = self.init()
        self.assertEqual(set(state["snapshot"]["files"]), {"app.py"})
        self.assertEqual((self.repo / "app.py").read_text(), SOURCE)
        self.assertEqual(state["status"], "NOT_STARTED")

    def test_git_snapshot_includes_uncommitted_and_untracked_changes(self):
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "add", "app.py"], check=True)
        (self.repo / "app.py").write_text(SOURCE + "# uncommitted\n")
        (self.repo / "new.py").write_text("# untracked\n")
        state = self.init()
        self.assertIn("new.py", state["snapshot"]["files"])
        self.assertIn("uncommitted", (self.run / "workspace/source/app.py").read_text())

    def test_output_inside_source_rejected(self):
        with self.assertRaises(ValueError):
            create_run(self.repo, self.repo / "audit", "scope")

    def test_schema_rejects_missing_fields_and_bool_as_line(self):
        p = payload()
        validate(p)
        p["findings"][0]["line"] = True
        with self.assertRaises(ValueError):
            validate(p)
        with self.assertRaises(ValueError):
            validate({"done": True})

    def test_all_six_pass_gates_can_confirm(self):
        f = assess(finding(), self.evidence_workspace(), commands(), "verify")
        self.assertEqual(f["status"], "confirmed")
        self.assertEqual(f["validation_errors"], [])
        self.assertTrue(f["evidence_binding"]["output_sha256"])

    def test_each_gate_must_have_evidence_and_pass(self):
        workspace = self.evidence_workspace()
        for gate in GATES:
            with self.subTest(gate=gate):
                f = finding()
                f["gates"][gate]["result"] = "UNRESOLVED"
                self.assertEqual(assess(f, workspace, commands(), "verify")["status"], "unverified")
                f["gates"][gate] = {"result": "PASS", "evidence": ""}
                self.assertEqual(assess(f, workspace, commands(), "verify")["status"], "unverified")

    def test_exploration_cannot_self_confirm(self):
        f = assess(finding(), self.evidence_workspace(), commands(), "explore")
        self.assertEqual(f["status"], "unverified")

    def test_fabricated_or_failed_runtime_evidence_rejected(self):
        workspace = self.evidence_workspace()
        for recorded in ([], [{**commands()[0], "exit_code": 1}], [{**commands()[0], "output": "import failed"}]):
            self.assertEqual(assess(finding(), workspace, recorded, "verify")["status"], "unverified")

    def test_other_findings_command_cannot_supply_evidence(self):
        workspace = self.evidence_workspace()
        unrelated = [{**commands()[0], "command": "python3 artifacts/unrelated.py"}]
        self.assertEqual(assess(finding(), workspace, unrelated, "verify")["status"], "unverified")

    def test_note_file_and_wrong_source_line_rejected(self):
        workspace = self.evidence_workspace()
        (workspace / "artifacts/note.txt").write_text("ordinary prose")
        f = finding()
        f["proof"]["artifact"] = "artifacts/note.txt"
        f["line"] = 1
        result = assess(f, workspace, commands(), "verify")
        self.assertEqual(result["status"], "unverified")
        self.assertTrue(any("Source excerpt" in x for x in result["validation_errors"]))

    def test_missing_fix_or_control_cannot_confirm(self):
        workspace = self.evidence_workspace()
        f = finding()
        f["fix"] = ""
        f["proof"]["control_observation"] = f["proof"]["observation"]
        self.assertEqual(assess(f, workspace, commands(), "verify")["status"], "unverified")

    def test_escaping_and_symlink_evidence_rejected(self):
        workspace = self.evidence_workspace()
        (workspace / "artifacts/link.py").symlink_to(self.repo / "app.py")
        for name in ("../repo/app.py", "/etc/passwd", "artifacts/link.py"):
            with self.assertRaises(ValueError):
                contained(workspace, name)

    def test_two_round_agent_finishes_and_has_actionable_report(self):
        self.init()
        fake = FakeRuntime()
        state = run_agent(self.run, fake, max_rounds=2)
        self.assertEqual(state["status"], "COMPLETE_SCOPED")
        self.assertEqual(fake.calls, 2)
        self.assertEqual(state["findings"][0]["status"], "confirmed")
        report = (self.run / "report.md").read_text()
        self.assertIn("**Repair:**", report)
        self.assertIn("**Regression check:**", report)
        self.assertIn("rounds/002/commands.json", report)

    def test_single_round_stays_partial_and_resume_verifies(self):
        self.init()
        first = run_agent(self.run, FakeRuntime(), max_rounds=1)
        self.assertEqual(first["status"], "PARTIAL")
        self.assertEqual(first["findings"][0]["status"], "unverified")
        resumed = run_agent(self.run, FakeRuntime(), max_rounds=1)
        self.assertEqual(resumed["status"], "COMPLETE_SCOPED")
        self.assertEqual(len(resumed["rounds"]), 2)

    def test_no_finding_audit_needs_coverage_and_verification(self):
        self.init()
        p = payload(findings=[])
        p["coverage"] = []
        state = run_agent(self.run, FakeRuntime(p), max_rounds=2)
        self.assertEqual(state["status"], "PARTIAL")
        self.assertEqual(run_agent(self.run, FakeRuntime(payload(findings=[])), max_rounds=1)["status"], "COMPLETE_SCOPED")

    def test_blocked_coverage_does_not_finish(self):
        self.init()
        p = payload(findings=[])
        p["coverage"][0]["status"] = "blocked"
        p["blockers"] = ["Test dependency unavailable"]
        self.assertEqual(run_agent(self.run, FakeRuntime(p), max_rounds=2)["status"], "PARTIAL")

    def test_timeout_saves_blocked_state_and_error(self):
        self.init()
        state = run_agent(self.run, FakeRuntime(failure=TimeoutError("test timeout")))
        self.assertEqual(state["status"], "BLOCKED")
        self.assertEqual(load_json(self.run / "state.json")["error"], "test timeout")

    def test_interruption_is_resumable(self):
        self.init()
        state = run_agent(self.run, FakeRuntime(failure=KeyboardInterrupt()))
        self.assertEqual(state["status"], "INTERRUPTED")
        self.assertEqual(run_agent(self.run, FakeRuntime(), max_rounds=2)["status"], "COMPLETE_SCOPED")

    def test_source_mutation_rejects_round(self):
        self.init()
        state = run_agent(self.run, FakeRuntime(mutate=True))
        self.assertEqual(state["status"], "BLOCKED")
        self.assertIn("modified", state["error"])
        self.assertEqual((self.repo / "app.py").read_text(), SOURCE)

    def test_resume_rejects_changed_snapshot(self):
        self.init()
        (self.run / "workspace/source/app.py").write_text("changed")
        runtime = FakeRuntime()
        state = run_agent(self.run, runtime)
        self.assertEqual(state["status"], "BLOCKED")
        self.assertEqual(runtime.calls, 0)

    def test_prior_findings_cannot_be_silently_dropped(self):
        self.init()
        run_agent(self.run, FakeRuntime(), max_rounds=1)
        state = run_agent(self.run, FakeRuntime(payload(findings=[])), max_rounds=1)
        self.assertEqual(state["status"], "BLOCKED")
        self.assertIn("dropped", state["error"])

    def test_event_parser_binds_completed_commands_only(self):
        events = self.root / "events.jsonl"
        events.write_text('\n'.join(json.dumps(e) for e in [
            {"type": "item.started", "item": {"type": "command_execution", "command": "not completed"}},
            {"type": "item.completed", "item": {"id": "item_2", "type": "command_execution", "command": COMMAND,
                                                  "aggregated_output": OUTPUT, "exit_code": 0, "status": "completed"}},
            {"type": "turn.completed", "usage": {"input_tokens": 42}},
        ]))
        records, usage, failures = command_records(events)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["output"], OUTPUT)
        self.assertEqual(usage["input_tokens"], 42)
        self.assertEqual(failures, [])

    def test_no_command_blocker_is_preserved(self):
        self.init()
        class BlockedRuntime(FakeRuntime):
            def run(self, *args):
                p, _, usage = super().run(*args)
                p['findings'] = []
                p['blockers'] = ['Nested sandbox could not initialize']
                return p, [], usage
        state = run_agent(self.run, BlockedRuntime())
        self.assertEqual(state['status'], 'BLOCKED')
        self.assertIn('Nested sandbox', state['error'])
        self.assertEqual(state['blockers'], ['Nested sandbox could not initialize'])

    def test_coverage_cannot_silently_disappear(self):
        self.init()
        run_agent(self.run, FakeRuntime(), max_rounds=1)
        p = payload()
        p['coverage'] = []
        state = run_agent(self.run, FakeRuntime(p), max_rounds=1)
        self.assertEqual(state['status'], 'BLOCKED')
        self.assertIn('dropped prior coverage', state['error'])


if __name__ == "__main__":
    unittest.main()
