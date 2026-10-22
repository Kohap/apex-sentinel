import unittest

from apex_agent.cli import parser
from apex_agent.loop import fingerprint, run_loop


def state(status, findings=(), coverage=(), blockers=()):
    return {"status": status, "findings": [{"id": i, "status": s} for i, s in findings],
            "coverage": [{"surface": a, "file": b, "status": c} for a, b, c in coverage],
            "blockers": list(blockers)}


class LoopTests(unittest.TestCase):
    def drive(self, states, **kw):
        calls = iter(states)
        seen = []
        result, reason = run_loop(lambda: next(calls), on_pass=seen.append, log=lambda *a, **k: None, **kw)
        return result, reason, len(seen)

    def test_single_pass_is_default_behaviour(self):
        _, reason, n = self.drive([state("PARTIAL")], passes=1)
        self.assertEqual(n, 1)
        self.assertIn("pass limit", reason)

    def test_stops_on_complete(self):
        _, reason, n = self.drive([state("PARTIAL", [("F1", "unverified")]), state("COMPLETE_SCOPED")], passes=5)
        self.assertEqual(n, 2)
        self.assertIn("COMPLETE_SCOPED", reason)

    def test_stops_on_blocked(self):
        _, reason, n = self.drive([state("BLOCKED")], passes=5)
        self.assertEqual(n, 1)
        self.assertIn("BLOCKED", reason)

    def test_progress_resets_stall(self):
        seq = [state("PARTIAL", [("F1", "unverified")]), state("PARTIAL", [("F1", "confirmed")]),
               state("PARTIAL", [("F1", "confirmed")]), state("PARTIAL", [("F1", "confirmed")])]
        _, reason, n = self.drive(seq, passes=10, stall=2)
        self.assertEqual(n, 4)
        self.assertIn("no progress", reason)

    def test_wall_budget(self):
        _, reason, n = self.drive([state("PARTIAL")] * 3, passes=3, wall_budget=0.0000001)
        self.assertEqual(n, 1)
        self.assertIn("wall budget", reason)

    def test_rejects_bad_limits(self):
        with self.assertRaises(ValueError):
            run_loop(lambda: state("PARTIAL"), 0)

    def test_fingerprint_ignores_order(self):
        a = state("PARTIAL", [("A", "confirmed"), ("B", "dismissed")])
        b = state("PARTIAL", [("B", "dismissed"), ("A", "confirmed")])
        self.assertEqual(fingerprint(a), fingerprint(b))

    def test_cli_flags(self):
        args = parser().parse_args(["resume", "run", "--loop", "4", "--stall", "3", "--loop-budget", "60"])
        self.assertEqual((args.loop, args.stall, args.loop_budget), (4, 3, 60))
        args = parser().parse_args(["resume", "run"])
        self.assertEqual((args.loop, args.stall, args.loop_budget), (1, 2, None))


if __name__ == "__main__":
    unittest.main()
