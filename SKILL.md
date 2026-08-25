---
name: apex-sentinel
description: >-
  Unified self-learning Web3 audit engine. Orchestrates kensho + ragnarok +
  jailbreaker + bug-ai-auditor + iykes-web3-bughunt into one gated engagement
  lifecycle, then learns from every audit via a persistent brain at
  ~/.apex-sentinel/ so it never goes stale. Use when asked to "run apex",
  "apex sentinel", a full audit, or any bug-hunt engagement.
metadata:
  version: 1.1.0
  created: 2026-08-24
  author: Gift (https://github.com/Kohap)
  copyright: "Copyright (c) 2026 Gift. All rights reserved. See LICENSE."
  components: [kensho, ragnarok, jailbreaker, bug-ai-auditor, iykes-web3-bughunt-skill]
  brain: ~/.apex-sentinel/
---

# APEX SENTINEL — Unified Adaptive Audit Engine

One engagement lifecycle, five methodologies, zero duplicated work, permanent learning.

Apex Sentinel does NOT replace the component skills — it orchestrates them. Depth is
routed to the component that owns it; this file holds only the merged spine, the gates,
and the self-learning protocol. If a component skill is missing from the machine, fall
back to the references in the surviving skills; never silently skip a phase.

## Component routing

| Need | Route to | Base dir |
|---|---|---|
| Intake template, contract discovery, auth triage commands, severity rubric, report/disclosure templates | **kensho** Parts 1–4, 7–9 | `~/.claude/skills/kensho` |
| Full reconstruction → hypothesis → experiment discipline with two mechanical gates and evidence levels | **ragnarok v2** core loop (`references/phases/`) | `~/.claude/skills/ragnarok` (scripts/gate_check.sh, scaffold.sh, report_gate.sh) |
| Attack-first recheck, false-positive killing, JACKPOT confirmation, blackhat orchestrator | **jailbreaker** (`references/viktor-blackhat-orchestrator.md`, `bughunter-workflow.md`) | `~/.codex/skills/jailbreaker` |
| AI audit-tool chaining, APK/mobile pipeline, Solana bounty playbook, Sherlock drafting | **bug-ai-auditor** references | `~/.claude/skills/bug-ai-auditor` |
| Mechanical recon tools (step1–7, step9–10), coverage tracking, multi-angle pass, dual-ledger vault hunt, contact hunt | **iykes-web3-bughunt-skill** SKILL.md steps 1–10 + `tools/` | `~/.claude/skills/iykes-web3-bughunt-skill` |
| Rust/Solana consensus & validator targets | **kensho** Part 10 (+ jailbreaker solana playbook) | — |

## The Brain (`~/.apex-sentinel/`)

Persistent, global, outside all skill dirs so updates never clobber learned state:

| File | Purpose |
|---|---|
| `LEARNINGS.md` | Append-only lessons ledger (findings, kills, timings, method notes) |
| `taxonomy.json` | Bug-class vocabulary merged from every source + field hit counters |
| `false-positives.md` | FP patterns — check here FIRST during falsification |
| `heuristics.md` | Grep passes / detection tricks ranked by field performance |
| `targets.json` | Per-target history: what was audited, what was found/killed, commit pinned |
| `upstreams.json` | Tracked upstream repos + freshness manifest |

## Non-negotiable rules (strictest of all components)

1. Default env `READ_ONLY_PRODUCTION`. Fork / `eth_call` / local-fork PoC ONLY. Never
   move real funds or broadcast live exploits. Live state-changing activity needs
   explicit authorization (ragnarok env classification, recorded in scope.md).
2. Every claim carries an evidence level: SOURCE < DEPLOYMENT < RUNTIME < ECONOMIC.
   A hypothesis is CONFIRMED only at RUNTIME + ECONOMIC. Unproven = `Potential`.
3. Mechanical phase gate: no exploit analysis until reconstruction artifacts are
   complete on disk (`gate_check.sh` exit 0). A compelling lead never unlocks the gate.
4. Coverage honesty (iykes): maintain `coverage.md` incrementally; never imply a full
   audit below ~50% traced coverage of value-moving paths.
5. Temporary-vs-persistent kill rule (iykes): a transient manipulation that restores is
   not theft; prove persistence before claiming Critical bank-run.
6. Honest severity with stated bounds; trust/centralization labeled separately from
   permissionless exploits; never inflate because a pattern looks scary.
7. Private disclosure only, verified official inbox (iykes Step 10A contact hunt),
   researcher attribution per operator identity configured at intake. Ask, never threaten.
8. Kill your own findings. Disproving yourself is the job. Say `JACKPOT 🚨` only on
   confirmed critical reproducible loss.
9. Token-conservative execution (iykes): mechanical probes go to scripts/subagents;
   primary model reserved for judgment-heavy steps. One finding path at a time.
10. Learn or it didn't happen: Phase R (retro) is mandatory before an engagement closes.

## UNIFIED LIFECYCLE

Run once, in order. Each phase names its owner component — load only that section.

### P0 — Authorize · Scope · Brief  *(kensho Part 1–3 + ragnarok phases/00-scope)*
- Fill kensho intake sheet; verify audit status (fresh vs picked-over) BEFORE investing.
- Classify environment: READ_ONLY_PRODUCTION | LOCAL_FORK | AUTHORIZED_LIVE; record in
  `research/scope.md`. Default: authorization UNKNOWN, read-only, live=NO.
- Catalog prior scrutiny (audits, program Known Issues) — a novelty prior, not a skip.
- **Inject the Brain:** run `scripts/brief.py --product-type <T> [--chain C] [--keywords ...]`
  → get relevant past classes (with hit counts), matching FP patterns, target history,
  and a freshness warning if upstreams haven't been checked in >14 days.

### P1 — Ground truth & surface mapping  *(iykes Steps 1–4 + kensho Part 4)*
- `tools/step1_ground_truth.sh` → dead RPC/scam = STOP.
- Locate core contracts: creator trace → bundle grep → browser network tab → explorer
  (`tools/step2_*`). Verify source / map selectors (`tools/step3_surface_map.sh`).
- Auth triage first: `tools/step4_auth_triage.sh` — unguarded admin fn = likely Critical.
- Start `coverage.md` (template in iykes). Update it as files are opened and paths traced.

### P2 — Reconstruct reality  *(ragnarok phases/01-map · 02-deployment)*
- Scaffold `research/` (`ragnarok/scripts/scaffold.sh`). Build architecture, asset-flows,
  trust-boundaries (with ≥1 cross-contract composition trace), deployment verification
  (bytecode vs source, ACTIVE/INACTIVE/UNKNOWN, dependency behavior not just address match).
- Queue every suspicious observation in `leads.md` (OBSERVED) — do NOT chase yet.

### P3 — Invariants & assumptions  *(ragnarok phases/03-invariants · 04-assumptions)*
- Derive the invariant ledger (INV-###) with enforcement points; mine cross-boundary
  assumptions with provenance. No empty invariants.md — explicit rationale if N/A.

### ⛔ GATE — `ragnarok/scripts/gate_check.sh research/`
Exit != 0 → return to the named phase. Hypothesis work stays LOCKED until OPEN.
V2 adds a second mechanical gate: `ragnarok/scripts/report_gate.sh research/` before any
disclosure leaves the workspace (P9/P10). Both gates live in apex `scripts/` (vendored v2).

### P4 — Hypothesis generation  *(ragnarok "Rank before you fork" + iykes Step 5.5 + jailbreaker)*
- Architecture-derived hypotheses (never SWC checklist dumps); promote leads only after
  the 9 anti-anchoring questions.
- Run iykes multi-angle adversarial pass per chunk (malicious actor / economic-math /
  state-access / edges / integrations). For vaults add dual-ledger hunt (principal book
  vs NAV vs cash returned, iykes Step 5.6).
- Cross-check the Brain: taxonomy classes for this product type; false-positives.md.

### P5 — Experiment-first proof  *(ragnarok "One fixture, many mutations" + iykes Step 7)*
- Smallest falsifiable experiment first; fork PoCs via `tools/step7_poc_scaffold.sh`;
  assert impact in numbers; record kills with reasons in killed.md; mutate before burying.

### P6 — Composition · Temporal · Economic  *(ragnarok core loop: expand + economic validation)*
- Systematic pairing pass; state-machine transitions; THEN economic validation
  (attacker/protocol before-after, capital, gas, repeatability). No severity before this.

### P7 — Falsification & FP kill  *(jailbreaker + iykes second-opinion gate)*
- Assume the finding is wrong: hidden auth? impossible preconditions? deployment drift?
  mitigations elsewhere? Check false-positives.md first. 5-question gate →
  CONFIRMED / FALSE POSITIVE / NEEDS MORE WORK.

### P8 — Expansion & novelty  *(ragnarok core loop: primitive families + novelty pass)*
- Expand survivors into primitive families (every consumer hunted); second-pass novelty
  research including fresh-skepticism revisit of SELF_RESOLVED leads.

### P9 — Rate · Report  *(kensho Parts 7–8 + iykes Steps 8–9)*
- Severity with bounds against the program's own table; report template with plain-language
  section, exact root cause, PoC command, coverage statement. CONFIRMED findings only in
  the disclosure report; everything else lives in final.md.

#### REPORTABILITY GATE (hard filter before P10)
Only findings that pass ALL of the following leave the workspace:
1. Severity is **Critical or High** (Medium/Low stay in final.md and the Brain).
2. **Quantified loss** is stated in asset terms: reachable TVL / capital at risk on the
   vulnerable path, max per-tx loss, attacker cost, and frequency. A finding that cannot
   be quantified is not reportable — quantify it, scope it down, or keep it internal.
3. Root cause at file:line (or bytecode offset for unverified targets) + reproducible PoC.
4. Not a duplicate of prior audits / program Known Issues.
Never spend a team's attention (or your reputation) on Low/QA noise. Internal ledgers are
for learning; outbound channels are for material, quantified risk only.

### P10 — Disclose  *(kensho Part 9 + iykes Step 10)*
- Contact hunt with cited sources (reports/contacts.md) BEFORE any DM; verified inbox or
  verified org X or do not send. Short first DM; private repo; number after confirmation;
  help fix; never bundle payment with silence.

### PR — RETRO (mandatory, self-learning capture)
Before closing the engagement, feed the Brain:
```bash
python3 "$APEX/scripts/retro.py" \
  --target "<project>" --product-type "<type>" --chain "<chain>" \
  --finding --class <AS-XXX|new> --text "<what was learned / what killed it>" \
  --evidence RUNTIME --severity <sev>            # repeatable, one per lesson
python3 "$APEX/scripts/retro.py" --fp --pattern "<FP shape>" --why "<how it died>"
python3 "$APEX/scripts/retro.py" --register-target --target "<p>" --commit "<sha>" \
  --summary "<one line>"
```
Also append manually to heuristics.md when a grep/detection trick proved or died.
An engagement without a retro is incomplete — reopen it.

## Freshness protocol (anti-stagnation)

1. `scripts/update_check.sh` git-fetches every repo in `~/.apex-sentinel/upstreams.json`,
   fast-forwards installs (backs up local edits first), syncs mirrors, prints changelog deltas.
2. Run it at P0 when brief.py warns staleness (>14 days), and whenever the user asks
   "update the suite".
3. New external intel (postmortems, DeFiHackLabs entries, new bug classes seen on X):
   submit through retro.py `--type intel`; taxonomy grows via `--class new --name ...`.
4. Ledger hygiene: entries carry dates; supersede rather than delete. Demote heuristics
   that fail twice consecutively to the Dead list.

## Anti-patterns (union of all components)

Skipping the gate on a hot lead · reporting SOURCE-level findings as confirmed ·
treating admin power as permissionless exploit · claiming temporary manip as persistent
theft · implying full audit under low coverage · re-running phases another component owns ·
fabricating a finding to fill a report · closing without Phase R · trusting conversation
history over disk artifacts · guessing security@ inboxes · public discussion of live bugs.

## Quick start

```
APEX=~/.claude/skills/apex-sentinel
1. python3 $APEX/scripts/brief.py --product-type vault          # load the Brain
2. Follow P0→P10 above, routing depth to component skills
3. End every engagement with retro.py                            # teach the Brain
```
