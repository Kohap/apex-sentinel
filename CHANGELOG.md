# Changelog

## 2.0.0 — 2026-09-16

Convert Apex into a local repository audit agent powered by Codex CLI.

- Add `apex audit`, `resume`, `status`, `report`, and `doctor` commands.
- Add source snapshots, bounded explore/verify rounds, captured command evidence,
  structured finding validation, actionable repair reports, and persistent run state.
- Separate confirmed findings from unverified leads; preserve partial and blocked
  outcomes rather than reporting completion from an empty scaffold.
- Fix legacy six-gate validation, missing-input handling, per-finding evidence labels,
  aggregate report-state output, reportable-status compatibility, and coverage scaffolding.
- Include the original v1.3.1 review and reproductions, migration guidance, a synthetic
  invoice target, automated tests, and macOS/Linux CI.
- Archive the v1 skill and make the main skill entrypoint route to the agent.
- Document that live Codex smoke testing was blocked by the enclosing macOS sandbox;
  no successful end-to-end model-driven audit is claimed for this validation run.

## 1.3.1 — 2026-09-12

Operator card so the human can actually drive Apex.

- `references/operator.md` — copy-paste first lines for new / residual / APPLICATION / close
- Wider auto-load triggers (audit this, bounty hunt, ragnarok, investigate, keep hunting)
- On-invoke: read NOW.md first; OPEN means residual, not a new P0
- "audit skill" in the description so it does not load the stub


## 1.3.0 — 2026-09-12

Stop hallucinated component use and false-positive reports.

Apex 1.2 named five owners and then let the model improvise. False reports
shipped when jailbreaker / iykes / kensho never wrote an artifact. v1.3 makes
**artifact-or-it-didn't-happen** mechanical.

- `references/handshake.md` — load card per phase (exact file from the owning skill)
- `references/anti-hallucination.md` — never-cite-unread, never TRUST-as-JACKPOT
- `scripts/load_card.sh P#` — prints the one-phase load list
- `scripts/component_check.py` — FAIL if a required owner has no artifact
- `scripts/claim_gate.py` — CONFIRMED-REPORTABLE needs `fp-kill.md` (jailbreaker
  six gates + iykes 5 + kensho 5.5 + brain FPs + kill mutations + permissionless YES)
- `scripts/report_gate.sh` wraps ragnarok report_gate + claim_gate + handshake
- `scripts/defaults/fp-kill.md` + `handshake.md` copied by scaffold
- Verdict vocabulary: FALSE POSITIVE | NEEDS MORE WORK | SURVIVOR | TRUST |
  CONFIRMED-INTERNAL | CONFIRMED-REPORTABLE
- Honest empty `report.md` still PASSes. A finding without the gauntlet FAILS.


## 1.2.0 — 2026-09-12

Field update after Umia (Base TGE, residual OPEN, no permissionless JACKPOT),
Tessera-v (honest empty report), and KeeperHub Sky Exec (application-layer audit
+ patches at `Kohap/keeperhub-sky-exec@3798594`).

### Skills freshness (this pass)

| Component | Local pin | Upstream HEAD | Date | Action |
|---|---|---|---|---|
| apex-sentinel | 7e0edc78 v1.1.0 | 7e0edc78 | 2026-08-25 | **this release** |
| ragnarok | v3 | `ba08271` v4 | 2026-09-04 | **synced** |
| kensho | hood.fun placeholder | `e308a84` | 2026-09-02 | **intake placeholder synced** |
| iykes-evm-bughunt | current | `e057fae` | 2026-08-15 | current |
| viktor-blackhat / jailbreaker | current | `ebf3193` | 2026-07-02 | stale, 2 commits, no update |
| bug-ai-auditor | stub | none | — | keep stub; "audit skill" = Apex |

### Behavior

- Route **ragnarok v4**: SYNTHESIS OPEN after thin map; CAMPAIGN OPEN is not a lock
  on imagination; 48-hour probe rule.
- **Substance override** on `gate_check.sh`: filled hunts are not restarted when a
  heading-regex gate reports LOCKED / exit 3.
- **Intent routing**: investigate/continue = residual P8; "audit skill" = this file.
- **APPLICATION layer** skips the EVM reconstruction gate.
- **Brain bootstrap** (`init_brain.py`); `brief.py` / `update_check.sh` no longer
  fail silent when `~/.apex-sentinel/` is missing.
- Skill path resolver includes Grok `.grok/skills/`.
- `update_check.sh` / `sync_mirrors.sh` work without `rsync` (`cp -a` fallback).
- TRUST vs permissionless spelled out (1-step Ownable EOA, Safe M-of-N, EIP-7702
  delegator). Reportability gate requires permissionless + quantified loss.
- Ledger append-only rule. Honest empty `report.md` is a valid close.
- New taxonomy classes AS-022–AS-030 from KeeperHub / Umia FPs.
- Vendored ragnarok v4 scripts under `scripts/vendor/ragnarok/` plus
  `probe_evm.sh` / `harness_init.sh`.
- Phase R is the mechanical close.

### Files

- `SKILL.md` v1.2.0
- `references/field-lessons.md`
- `scripts/init_brain.py`, `resolve_skill.sh`, wrapper `gate_check.sh`
- `scripts/defaults/*` brain seed
- `scripts/vendor/ragnarok/*`

## 1.1.0 — 2026-08-25

Initial public release. Gated engagement lifecycle, self-learning brain,
ragnarok-v2 gates, reportability gate.
