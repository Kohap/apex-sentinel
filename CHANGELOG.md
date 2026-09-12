# Changelog

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
