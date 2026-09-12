# Component handshake

Apex names five owners. Naming them is not using them. **Artifact-or-it-didn't-happen.**

At each phase: run `scripts/load_card.sh P#`, load **only** the listed file, produce
the listed artifact, tick `research/handshake.md`. Do not reconstruct a methodology
from memory. Do not cite a skill you did not load this session.

`bug-ai-auditor` is never an owner. If the user said "audit skill", the owner is Apex.

## Load cards

| Phase | Owner | Load (exact) | Produce | Do not |
|---|---|---|---|---|
| P0 | kensho | `SKILL.md` Part 3 (intake + audit-status) | `intake.md`, `scope.md` | Invent inboxes, invent chain ids |
| P0 | ragnarok | `references/phases/00-scope.md` + `references/bounty.md` if bounty | env/auth/layer fields in `scope.md` | Skip authorization |
| P0 | apex | `scripts/brief.py` (run) | stdout in notes; brain present | Hunt with no brain |
| P1 | iykes | **run** `tools/step1_ground_truth.sh` … `step4_auth_triage.sh` | `recon.md`, `auth-triage.md`, `coverage.md` | Rewrite the bash from memory |
| P1 | ragnarok | `references/phases/01-map.md` | thin `architecture.md` (graph + one trace) | Deep-dive a lead |
| P2 | ragnarok | `references/phases/02-deployment.md` + adapter | `deployment.md` | Address match as behavior check |
| P3 | ragnarok | `references/phases/03-invariants.md`, `04-assumptions.md` | `invariants.md`, `assumptions.md` | Empty INV/ASM with no rationale |
| P4 | ragnarok | `references/phases/05-synthesis.md`, `seams.md`, `05-hypotheses.md` | `contradictions.md`, `representations.md`, `hypotheses.md` | Start from SWC/bug-class list |
| P5 | ragnarok + iykes | `references/phases/06-experiments.md`, `kill.md`; **run** `step7_poc_scaffold.sh` / `probe_evm.sh` | `experiments/`, kills in `killed.md` | "Would revert" without a run |
| P6 | ragnarok | `references/phases/10-economic.md` | quantified delta on the H-row | Severity before numbers |
| P7 | jailbreaker | `references/verification-and-reporting.md` §1 (six gates) | `fp-kill.md` section per H- | Promote on vibes |
| P7 | iykes | SKILL.md "Second-opinion gate" (5 questions) | same `fp-kill.md` section | Skip because "obvious" |
| P7 | kensho | SKILL.md §5.5 quality gate | same `fp-kill.md` section | Skip duplicate check |
| P7 | apex brain | `~/.apex-sentinel/false-positives.md` | named rows in `fp-kill.md` | "I checked FPs" with no quote |
| P8 | ragnarok | `references/phases/13-novelty.md`, `14-residual.md` | `survivors.md`, coverage update | Re-open killed H- without new evidence |
| P9 | kensho | Parts 7–8 (rate + report template) | `report.md` via claim_gate | Fill report with SURVIVOR |
| P9 | iykes | Steps 8–9 | bound + coverage sentence | Imply full audit under 50% |
| P9 | apex | **run** `claim_gate.py` then `report_gate.sh` | `report-state.md` | Ship on chat consensus |
| P10 | kensho + iykes | kensho Part 9; **run** `step10_contact_hunt.sh` | `contacts.md` with URL+quote | Guess `security@` |
| PR | apex | **run** `retro.py` | brain L-### + target row | Close without retro |

APPLICATION layer: skip iykes step1–4 and ragnarok 01–02. Still run P0, P4–P7 on
`compose → policy → simulate → execute`, and still fill `fp-kill.md`.

## `research/handshake.md` row format

```
Phase | Owner | Loaded (path or SKIP) | Artifact | Evidence (cmd / file:line) | Status
P1 | iykes | iykes-web3-bughunt-skill/tools/step4_auth_triage.sh | auth-triage.md | ran 2026-09-12, 12 sigs guarded | DONE
P7 | jailbreaker | jailbreaker/references/verification-and-reporting.md | fp-kill.md#H-014 | six gates FAIL Reachability | DONE
```

Status is `DONE` | `SKIP` | `BLOCKED`. SKIP needs a one-line reason in Evidence.
A SKIP without a reason is a skip you invented — `component_check.py` fails it.

## What "used the component" means

| Claim in chat | Required on disk |
|---|---|
| "ran auth triage" | `auth-triage.md` with per-sig `guarded` / `OPEN` |
| "checked jailbreaker" | `fp-kill.md` section with all six gates answered |
| "kensho quality gate" | five §5.5 answers in that section |
| "checked the brain FPs" | quoted pattern rows, or "none matched" plus the date |
| "fork PoC" | file under `experiments/` that ran (output or assert) |
| "permissionless Critical" | `PERMISSIONLESS: YES` + stranger trigger + claim_gate PASS |

Conversation, tool-call memory, and "I used the skill internally" are not evidence.
