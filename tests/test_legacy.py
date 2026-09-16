import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("legacy_claim", REPO / "scripts/claim_gate.py")
claim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(claim)


class LegacyRegressionTests(unittest.TestCase):
    def test_complete_six_gates_pass_and_one_blank_fails(self):
        rows = '\n'.join(f'| {g} | PASS | observed fixture evidence |' for g in claim.JAIL_GATES)
        self.assertTrue(claim.jail_all_pass(rows))
        self.assertFalse(claim.jail_all_pass(rows.replace('Reachability | PASS', 'Reachability | ')))
        self.assertFalse(claim.jail_all_pass(rows.replace('Reachability | PASS | observed fixture evidence', 'Reachability | PASS | ')))

    def test_missing_research_fails(self):
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run([sys.executable, str(REPO / 'scripts/claim_gate.py'), str(Path(td) / 'missing')], capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_fresh_scaffold_cannot_close_and_manifest_records_overall_failure(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / 'hunt'
            subprocess.run(['bash', str(REPO / 'scripts/scaffold.sh'), str(target)], check=True, capture_output=True)
            research = target / 'research'
            self.assertIn('Surfaces not covered', (research / 'coverage.md').read_text())
            result = subprocess.run(['bash', str(REPO / 'scripts/report_gate.sh'), str(research), '--write'], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Report gate: FAIL', (research / 'report-state.md').read_text())


if __name__ == '__main__':
    unittest.main()
