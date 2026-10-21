import json
import tempfile
import unittest
from pathlib import Path

from apex_agent import ledger
from apex_agent.engine import prompt_for


def f(title, status="confirmed", line=2):
    return {"id": "APEX-001", "title": title, "file": "app.py", "line": line,
            "severity": "medium", "status": status}


class LedgerTest(unittest.TestCase):
    def test_merge_across_runs(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ledger.json"
            self.assertEqual(ledger.update(p, {"findings": [f("Missing owner check")]}, Path(d) / "run1"), 1)
            # same defect, different id/whitespace/case, later run; plus a new one
            ledger.update(p, {"findings": [f("missing  OWNER check", "unverified", 3), f("Rounding leak")]}, Path(d) / "run2")
            entries = json.loads(p.read_text())["entries"]
            self.assertEqual(len(entries), 2)
            e = entries["app.py::missing owner check"]
            self.assertEqual(len(e["runs"]), 2)
            self.assertEqual(e["last_status"], "unverified")
            self.assertEqual(e["line"], 3)

    def test_prompt_includes_known_findings(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ledger.json"
            base = {"focus": "x", "summary": "", "findings": [], "coverage": [], "blockers": [], "next_steps": []}
            self.assertNotIn("Known findings", prompt_for(dict(base, ledger=str(p)), "explore"))
            ledger.update(p, {"findings": [f("Missing owner check")]}, Path(d) / "run1")
            text = prompt_for(dict(base, ledger=str(p)), "explore")
            self.assertIn("Known findings", text)
            self.assertIn("Missing owner check", text)

    def test_rejects_corrupt_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ledger.json"
            p.write_text("[]")
            with self.assertRaises(ValueError):
                ledger.load(p)


if __name__ == "__main__":
    unittest.main()
