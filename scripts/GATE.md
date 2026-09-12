# Apex Sentinel phase gate — ragnarok v4 + substance override

Run: `scripts/gate_check.sh research/` before inventing states (and any time you
need to know whether SYNTHESIS / CAMPAIGN is open).

This wrapper:

1. Skips the EVM gate when `scope.md` records `Research layer: APPLICATION`.
2. Runs vendored ragnarok v4 (`scripts/vendor/ragnarok/gate_check.sh`).
3. Applies a **substance override**: if the regex gate is LOCKED or exit 3 but
   the research dir already holds a real map / NOW.md / killed or hypotheses
   ledger, treat SYNTHESIS as OPEN and do **not** restart P0–P5.

V4 semantics (from Godwin-web3/ragnarok @ ba08271):

| Gate | Opens when | Unlocks |
|---|---|---|
| SYNTHESIS | Phase 0 + thin map (graph + one trace) | contradiction cards + cheapest probe |
| CAMPAIGN | Phases 0–5 complete | full reconstruction; not a lock on imagination |
| Report | CONFIRMED + RUNTIME + ECONOMIC + kill attempt, or honest empty `report.md` | `scripts/report_gate.sh` |

Exit codes (wrapper): 0 SYNTHESIS OPEN (including override / APPLICATION skip),
1 SYNTHESIS LOCKED (thin map really missing), 3 violation only when there is
no substance on disk.

Do not treat a v2-era "hypothesis gate LOCKED" as a hunt restart.

v1.3 also runs `component_check.py` and `claim_gate.py` inside `report_gate.sh`.
A finding with no `fp-kill.md` (jailbreaker six gates, iykes 5, kensho 5.5,
quoted brain FPs) cannot ship. Naming a component in chat is not using it.

