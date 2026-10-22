"""Autonomous loop mode: chain bounded invocations of run_agent until the audit settles.

Each pass is an ordinary run_agent call (same round, timeout, and budget limits), so
the engine's gates, evidence capture, and snapshot checks are unchanged. The loop only
decides whether to start another pass.
"""
import hashlib
import json
import time

TERMINAL = {"COMPLETE_SCOPED", "BLOCKED", "INTERRUPTED"}


def fingerprint(state):
    """Hash of what a pass can change: finding ids/statuses, coverage statuses, blockers."""
    view = {
        "findings": sorted((f["id"], f["status"]) for f in state.get("findings", [])),
        "coverage": sorted((c["surface"], c["file"], c["status"]) for c in state.get("coverage", [])),
        "blockers": sorted(state.get("blockers", [])),
    }
    return hashlib.sha256(json.dumps(view, sort_keys=True).encode()).hexdigest()


def run_loop(run_once, passes, stall=2, wall_budget=None, on_pass=None, log=print):
    """Call run_once() up to `passes` times.

    Stops on a terminal status, after `stall` consecutive passes with no state change,
    or when `wall_budget` seconds have elapsed. Returns (state, reason).
    """
    if passes <= 0 or stall <= 0:
        raise ValueError("Loop passes and stall limit must be positive")
    start = time.monotonic()
    state, last, idle = None, None, 0
    for number in range(1, passes + 1):
        if number > 1 and wall_budget is not None and time.monotonic() - start >= wall_budget:
            return state, "loop wall budget exhausted"
        state = run_once()
        if on_pass:
            on_pass(state)
        status = state["status"]
        if passes > 1:
            log(f"Apex loop pass {number}/{passes}: {status}", flush=True)
        if status in TERMINAL:
            return state, f"terminal status {status}"
        mark = fingerprint(state)
        idle = idle + 1 if mark == last else 0
        last = mark
        if idle >= stall:
            return state, f"no progress in {stall} consecutive pass(es)"
    return state, "loop pass limit reached"
