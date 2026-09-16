---
name: apex-sentinel
description: >-
  Unified self-learning Web3 audit engine (Apex Sentinel). Orchestrates kensho +
  ragnarok v4 + jailbreaker + iykes-web3-bughunt with a component handshake and
  claim gate. THIS is the audit skill — not bug-ai-auditor. Invoke on: run apex,
  apex sentinel, apex residual, audit skill, full audit, web3 audit, smart contract
  audit, DeFi hunt, bug hunt, bounty hunt, ragnarok, hunt this, audit this, audit
  the repo, find bugs, JACKPOT, fork PoC, keep hunting, continue the hunt,
  investigate (a contract/EOA/Safe/function). After NOW.md is OPEN, short orders
  are residual P8 — do not restart P0. Operator card: references/operator.md.
metadata:
  version: 1.3.1
  created: 2026-08-24
  updated: 2026-09-12
  claim_gate: scripts/claim_gate.py
  author: Gift (https://github.com/Kohap)
  copyright: "Copyright (c) 2026 Gift. All rights reserved. See LICENSE."
  components: [kensho, ragnarok, jailbreaker, bug-ai-auditor, iykes-web3-bughunt-skill]
  ragnarok: v4
  brain: ~/.apex-sentinel/
---

# APEX SENTINEL — Unified Adaptive Audit Engine

One engagement lifecycle, five methodologies, zero duplicated work, permanent learning.

Apex Sentinel does NOT replace the component skills — it orchestrates them. Depth is
routed to the component that owns it; this file holds the merged spine, the gates,
intent routing, and the self-learning protocol. If a component skill is missing from
the machine, fall back to the references in the surviving skills; never silently skip
a phase.

`bug-ai-auditor` is a **routing stub**. When the user says "audit skill" they mean
**this file**, not the stub.


## On invoke (do this before anything else)

1. `APEX=$(bash scripts/resolve_skill.sh apex-sentinel)` and load **this file**.
2. If the user named a hunt (`hunts/<slug>`) or exactly one `hunts/*/research/NOW.md`
   exists, **read NOW.md**. If it says OPEN / residual / Phase 6–8, this is
   `apex residual` — do not restart P0–P5.
3. Else new hunt: `scaffold.sh hunts/<slug>` then `brief.py`.
4. `bash "$APEX/scripts/load_card.sh" <current-phase>` and load those files.
5. Human driving this skill: `references/operator.md`.

## Intent routing (read first)

| User says | Do |
|---|---|
| `run apex` / `apex sentinel` / `full audit` | P0 → P10 + Phase R |
| `audit skill` / `the audit skill` | **this skill**, never the bug-ai-auditor stub |
| `investigate X` / `keep hunting` / `continue` after SYNTHESIS or CAMPAIGN OPEN (or NOW.md says residual/OPEN) | residual P8 dive on X. **Do not restart P0–P5.** |
| Application-layer target (TS policy, MCP, CLI, agent exec) | Skip the EVM reconstruction gate. Hunt `compose → policy → simulate → execute`. |
| `update the suite` / this freshness pass | `scripts/update_check.sh` then Phase R into the Brain |

A vendored-gate `LOCKED` / exit 3 on a hunt that already has a filled map, killed.md,
and coverage.md is a **tooling mismatch**, not a reason to restart. Continue residual.
See `references/field-lessons.md`.

## Skill paths

Resolve a component directory with `scripts/resolve_skill.sh <name>`. Search order:

1. `$APEX_SKILLS/<name>`
2. `/workspace/.grok/skills/<name>` (Grok sandbox)
3. `~/.grok/skills/<name>`
4. `~/.claude/skills/<name>`
5. `~/.codex/skills/<name>`
6. `~/.config/opencode/skills/<name>`

Canonical Apex install is wherever this SKILL.md lives. Do not assume `~/.claude/skills/`
is the only loader — Grok loads `.grok/skills/`.

## Component routing

| Need | Route to | Notes |
|---|---|---|
| Intake template, contract discovery, auth triage, severity rubric, report/disclosure | **kensho** Parts 1–4, 7–9 | |
| Contradiction-driven hunt, thin-map imagination gate, fork probes, report gate | **ragnarok v4** (`references/phases/`, `seams.md`, `kill.md`) | Not v2/v3. SYNTHESIS OPEN after thin map. |
| Attack-first recheck, FP kill, JACKPOT confirmation | **jailbreaker** (viktor-blackhat alias) | Upstream stale since 2026-07-02; still the attack layer. |
| AI/LLM app, APK/mobile, Solana bounty, Sherlock drafting | **bug-ai-auditor stub** → jailbreaker playbooks + kensho Part 10 / 7–9 | Do not invent a fake auditor. |
| Mechanical recon tools (step1–7, 9–10), coverage.md, dual-ledger vault hunt | **iykes-web3-bughunt-skill** | step4 from `0xdead` |
| Rust/Solana consensus | **kensho** Part 10 | |


## Component handshake (v1.3 — this is how you use a skill)

A component that is only named in chat was **not used**. Artifact-or-it-didn't-happen.

Full table: `references/handshake.md`. Never list: `references/anti-hallucination.md`.

At every phase:

```
bash "$APEX/scripts/load_card.sh" P7
# load ONLY those files (not the whole skill, not memory)
# produce the artifact, tick research/handshake.md
python3 "$APEX/scripts/component_check.py" research/
```

| Claim in chat | Required on disk or it is a hallucination |
|---|---|
| ran iykes auth triage | `research/auth-triage.md` (per-sig guarded/OPEN) |
| used jailbreaker / killed FPs | `research/fp-kill.md` section with six gates answered |
| kensho quality gate | five §5.5 answers in that section |
| checked the brain | quoted rows from `~/.apex-sentinel/false-positives.md` |
| fork PoC / RUNTIME | file under `research/experiments/` that ran |
| permissionless Critical | `PERMISSIONLESS: YES` + `claim_gate.py` PASS |

P7 is **not optional**. Jailbreaker + iykes second-opinion + kensho §5.5 + brain FPs
+ ragnarok `kill.md` all write into the **same** `fp-kill.md` section. Skipping any
owner is how false positives ship.

P9: `claim_gate.py` then `report_gate.sh`. CONFIRMED without a passing claim gate
does not exist.

## The Brain (`~/.apex-sentinel/`)

Persistent, global, outside all skill dirs so updates never clobber learned state.

If the directory is missing, **bootstrap it** — never warn and hunt blind:

```
python3 "$APEX/scripts/init_brain.py"
```

`brief.py` and `update_check.sh` call this automatically. `rsync` is optional; the
scripts fall back to `cp -a` (Grok sandbox has no rsync).

| File | Purpose |
|---|---|
| `LEARNINGS.md` | Append-only lessons ledger |
| `taxonomy.json` | Bug-class vocabulary + field hit counters |
| `false-positives.md` | FP patterns — check FIRST during falsification |
| `heuristics.md` | Grep / RPC / ledger tricks ranked by field performance |
| `targets.json` | Per-target history |
| `upstreams.json` | Tracked upstream repos + freshness manifest |

## Non-negotiable rules

1. Default env `READ_ONLY_PRODUCTION`. Fork / `eth_call` / local-fork PoC ONLY. Never
   move real funds or broadcast live exploits. Live writes need explicit authorization
   recorded in `scope.md`.
2. Every claim carries an evidence level: SOURCE < DEPLOYMENT < RUNTIME < ECONOMIC.
   CONFIRMED only at RUNTIME + ECONOMIC. Unproven = `Potential`. SURVIVOR never enters
   `report.md`.
3. **Imagination gate (ragnarok v4):** SYNTHESIS OPEN after Phase 0 + a thin map
   (component graph + one trace). Then invent contradiction cards and run the cheapest
   probe. **CAMPAIGN OPEN** = Phases 0–5 complete — it widens the hunt; it is **not** a
   lock on imagination. Do **not** wait for full reconstruction to start probing.
   48-hour rule: after SYNTHESIS OPEN, a fork/harness probe must exist within two days
   of wall-clock hunt time or you are writing architecture novels.
4. **Substance override:** if `scripts/gate_check.sh` reports LOCKED / VIOLATION but
   NOW.md plus architecture/deployment/killed already hold real content, treat SYNTHESIS
   as OPEN for residual work. Heading-regex gates are a check, not reality. Never restart
   P0–P5 on an in-progress hunt.
5. Coverage honesty (iykes): maintain `coverage.md` incrementally; never imply a full
   audit below ~50% traced coverage of value-moving paths.
6. Temporary-vs-persistent kill rule (iykes): a transient manipulation that restores is
   not theft; prove persistence before claiming Critical bank-run.
7. Honest severity with stated bounds. **Trust/centralization is not a permissionless
   exploit.** 1-step Ownable EOA, Safe M-of-N, Certora "ACK platform owner", EIP-7702
   MetaMask delegator on a Safe owner — all TRUST unless a stranger path is proven.
   JACKPOT / P9–P10 require Crit/High + quantified permissionless loss + fork PoC.
8. Private disclosure only, verified official inbox (iykes Step 10A), researcher
   attribution at intake. Ask, never threaten.
9. Kill your own findings. `JACKPOT` only on confirmed critical reproducible loss.
10. Token-conservative execution: mechanical probes to scripts/subagents; primary model
    for judgment. One finding path at a time.
11. Learn or it didn't happen: Phase R is mandatory before an engagement closes.
    `retro.py --register-target` is the close. An honest empty `report.md` is a valid
    close. Do not fabricate a finding to fill a report.
12. **Ledger hygiene:** append-only on `killed.md` / `leads.md` / `hypotheses.md`. Never
    overwrite a ledger with empty `StrReplace`. Disk is memory. Conversation is not.
13. **Artifact-or-it-didn't-happen.** Did not load the file / run the tool this session
    → do not cite it. Conversation is not evidence.
14. **P7 gauntlet is blocking.** No `fp-kill.md` section → the finding is not CONFIRMED.
15. **claim_gate.py PASS** before any finding enters `report.md`. Honest empty is the
    only legal alternative.

## UNIFIED LIFECYCLE

Run once, in order. Each phase names its owner — load only that section.

At P0, record in `scope.md`:

```
Research layer: EVM | APPLICATION | SOLANA
```

APPLICATION skips the EVM reconstruction gate (still runs policy/compose/simulate
discipline). EVM follows ragnarok v4.

### P0 — Authorize · Scope · Brief  *(kensho Part 1–3 + ragnarok 00-scope + bounty.md)*
- Fill kensho intake; verify audit status (fresh vs picked-over) BEFORE investing.
- Classify environment + layer; default authorization UNKNOWN, read-only, live=NO.
- Catalog prior scrutiny — a novelty prior, not a skip.
- **Inject the Brain:** `python3 "$APEX/scripts/brief.py" --product-type <T> [--chain C] [--target N] [--layer EVM|APPLICATION]`
  Bootstraps the brain if missing. Freshness warning if upstreams >14 days stale.

### P1 — Ground truth & thin map  *(iykes Steps 1–4 + ragnarok 01-map)*
- `tools/step1_ground_truth.sh` → dead RPC/scam = STOP.
- Locate core contracts (`tools/step2_*`, `step3_surface_map.sh`).
- Auth triage first: `tools/step4_auth_triage.sh` (from `0xdead`).
- Thin map = component graph table + **one** real trace. Queue leads OBSERVED. Do not
  dive yet. Start `coverage.md`.

### ⛔ GATE — `scripts/gate_check.sh research/`
Apex wraps ragnarok v4 and applies the substance override.

| Result | Meaning | Action |
|---|---|---|
| SYNTHESIS OPEN | Phase 0 + thin map | Invent CX cards. Cheapest probe. Do not wait for campaign. |
| CAMPAIGN OPEN | Phases 0–5 on disk | Widen the hunt from the model. Still not a lock. |
| SYNTHESIS LOCKED | No thin map yet | Finish graph + one trace. |
| TOOLING LOCKED (override) | Regex gate disagrees with filled artifacts | Residual work. Do not restart. |
| APPLICATION SKIP | Layer is APPLICATION | Hunt compose → policy → simulate → execute. |

V2-era rule "no exploit analysis until reconstruction is complete" is **retired**.

### P2 — Deployment reality  *(ragnarok 02-deployment)*
Bytecode vs source, ACTIVE/INACTIVE/UNKNOWN, dependency **behavior** not just address match.

### P3 — Invariants & assumptions  *(ragnarok 03 + 04)*
INV-### with enforcement points; ASM-### with provenance. Grow these as the hunt needs
them — they are not a prerequisite for the first probe.

### P4 — Invent states · rank  *(ragnarok 05-synthesis + 05-hypotheses + seams.md + jailbreaker)*
- Invent the impossible state first (`contradictions.md`). Primitive is discovered from
  how it was reached. Do not start from a SWC/bug-class checklist.
- Representations table (`representations.md`) for the current seam.
- iykes multi-angle pass; vaults get dual-ledger hunt (Step 5.6).
- Cross-check Brain taxonomy + `false-positives.md`.

### P5 — Experiment-first proof  *(ragnarok 06 + iykes Step 7 + probe_evm.sh)*
- Smallest falsifiable experiment first. One harness (`harness_init.sh`).
- Record kills with reasons in `killed.md`; mutate before burying (`kill.md`).

### P6 — Composition · Temporal · Economic  *(ragnarok 08–10)*
Pairing pass; state-machine; THEN economic validation. No severity before this.

### P7 — Falsification & FP kill  *(jailbreaker + iykes + kensho + brain — ALL of them)*
`bash "$APEX/scripts/load_card.sh" P7` and load those files. Copy
`scripts/defaults/fp-kill.md` into `research/fp-kill.md`. One section per live H-###.

Assume the finding is wrong. Fill, do not summarize:
- Jailbreaker six gates (Process, Reachability, Real Impact, PoC, Math, Environment)
- Iykes 5-question second-opinion
- Kensho §5.5 quality gate
- Quoted brain FP rows (or "none matched" + date)
- Ragnarok `kill.md` mutation table

Verdict vocabulary (do not invent labels): FALSE POSITIVE | NEEDS MORE WORK |
SURVIVOR | TRUST | CONFIRMED-INTERNAL | CONFIRMED-REPORTABLE.

Unanswered line = the claim is not CONFIRMED. "I used jailbreaker internally" is a
hallucination.

### P8 — Expansion, novelty, residual  *(ragnarok 12–14)*
Expand survivors into primitive families. Revisit SELF_RESOLVED. Short user orders
("investigate X") land here when the hunt is already OPEN.

### P9 — Rate · Report  *(kensho 7–8 + iykes 8–9 + claim_gate)*
```
python3 "$APEX/scripts/component_check.py" research/
python3 "$APEX/scripts/claim_gate.py" research/
bash "$APEX/scripts/report_gate.sh" research/
```
CONFIRMED-REPORTABLE only in `report.md`. Everything else in `final.md`. Honest empty
report is valid. Any FAIL → do not disclose.

#### REPORTABILITY GATE (hard filter before P10)
Only findings that pass ALL of the following leave the workspace:
1. Severity is **Critical or High** (Medium/Low stay in final.md and the Brain).
2. **Quantified loss** in asset terms: reachable TVL, max per-tx, attacker cost, frequency.
3. Root cause at file:line (or bytecode offset) + reproducible PoC.
4. Not a duplicate of prior audits / Known Issues.
5. **Permissionless.** Owner rug, Safe M-of-N, 1-step Ownable EOA, EIP-7702 delegator ≠
   extra vote — TRUST, not reportable as JACKPOT.

### P10 — Disclose  *(kensho 9 + iykes Step 10)*
Contact hunt with cited sources before any DM. Verified inbox or verified org X or
do not send.

### PR — RETRO (mandatory)
Before closing:

```bash
python3 "$APEX/scripts/init_brain.py"   # no-op if present
python3 "$APEX/scripts/retro.py" \
  --target "<project>" --product-type "<type>" --chain "<chain>" \
  --finding --class <AS-XXX|new> --text "<what was learned / what killed it>" \
  --evidence RUNTIME --severity <sev>
python3 "$APEX/scripts/retro.py" --fp --pattern "<FP shape>" --why "<how it died>"
python3 "$APEX/scripts/retro.py" --register-target --target "<p>" --commit "<sha>" \
  --summary "<one line>"
```

An engagement without a retro is incomplete — reopen it.

## Freshness protocol

1. `scripts/update_check.sh` fetches every repo in `~/.apex-sentinel/upstreams.json`,
   fast-forwards installs (backs up local edits), syncs mirrors. Bootstraps the brain
   and the manifest if missing. Works without `rsync`.
2. Run it at P0 when brief.py warns staleness (>14 days), and when the user asks
   "update the suite" / "review the skills".
3. New intel through `retro.py --type intel`. Taxonomy grows via `--class new --name`.
4. Ledger hygiene: date entries; supersede rather than delete.

Pinned HEADs at 2026-09-12 freshness pass: see CHANGELOG.md.

## Anti-patterns

Skipping SYNTHESIS OPEN to write architecture novels · treating CAMPAIGN LOCKED or a
heading-regex LOCKED as "restart P0" · reporting SOURCE-level findings as confirmed ·
treating admin / 1-step Ownable EOA / Safe M-of-N / EIP-7702 delegator as permissionless
exploit · claiming temporary manip as persistent theft · implying full audit under low
coverage · routing "audit skill" to the stub · **naming a component without producing its
artifact** · **CONFIRMED without fp-kill.md** · re-running phases another component owns ·
fabricating a finding to fill a report · closing without Phase R · trusting conversation
over disk · overwriting killed.md/leads.md · guessing security@ inboxes · public discussion
of live bugs · citing unread files / unrun tools · using `Number()` for wei caps · letting
a client `killSwitch:false` override a server kill switch · defaulting ERC-4626 `receiver`
to `0x0` · dry-running the wrong function · `false ?? env` / client-supplied cooldown as
the policy clock.

## Quick start

```
APEX=$(dirname "$(readlink -f "$0")")   # or scripts/resolve_skill.sh apex-sentinel
python3 $APEX/scripts/init_brain.py
python3 $APEX/scripts/brief.py --product-type vault
# each phase:  bash $APEX/scripts/load_card.sh P#
#              load those files, produce the artifact, tick handshake.md
# P7: fill research/fp-kill.md from scripts/defaults/fp-kill.md
# P9: component_check.py && claim_gate.py && report_gate.sh
# End every engagement with retro.py
```
