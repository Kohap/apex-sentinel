# Operator card — how you drive Apex

You do not run the lifecycle yourself. You **name Apex, name the hunt dir, and
give one order**. The agent loads this skill, then `load_card.sh` for the current
phase. Short orders without those two names are how the stub/ragnarok/kensho
get invoked instead of Apex.

## First line of every message (copy)

New hunt:

```
run apex on <github-or-address>
layer: EVM | APPLICATION | SOLANA
product-type: vault | launchpad | lending | perps | policy | other
env: READ_ONLY_PRODUCTION
hunt dir: hunts/<slug>
```

Resume (this is the one you under-use):

```
apex residual hunts/<slug>
read research/NOW.md first
do not restart P0–P5
<one residual order>
```

Application-layer (TS policy / MCP / CLI / agent exec):

```
run apex layer APPLICATION on <repo>
hunt compose → policy → simulate → execute
skip the EVM reconstruction gate
```

Close:

```
apex close hunts/<slug>
honest empty report.md is valid
run retro.py --register-target
```

Freshness:

```
update the suite
```

## What to type instead of what you have been typing

| You typed | What the agent did | Type this instead |
|---|---|---|
| keep hunting / continue | Ambiguous. May restart P0 or ignore Apex | `apex residual hunts/umia` + one target |
| investigate Hub hot EOA | Residual if NOW.md is OPEN; else a new P0 | `apex residual hunts/umia — Hub owner EOA, TRUST vs stranger path only` |
| audit skill / the audit skill | Risk of loading `bug-ai-auditor` stub | `run apex` or `apex sentinel` |
| audit this + a GitHub URL | May skip handshake | `run apex on <url> layer: … hunt dir: hunts/<slug>` |
| so no single reportable vulnerability | Agent may invent a finding to fill the report | `apex close hunts/umia — honest empty is the correct output` |
| fix the changes / push | Out of hunt scope unless you say so | Separate: `patch <repo> from the CONFIRMED finding` |

One hunt per conversation. Do not mix Umia residual with a new KeeperHub audit
in the same thread unless you name both dirs and which order is active.

## How to know the agent is actually using Apex

Ask for the artifacts, not a narrative.

```
quote research/NOW.md (phase + gate)
show scripts/load_card.sh output for the current phase
show component_check.py and claim_gate.py
```

| If they say | Require |
|---|---|
| used jailbreaker | `research/fp-kill.md` section with six gates |
| ran auth triage | `research/auth-triage.md` |
| CONFIRMED / JACKPOT | `claim_gate.py` PASS + `PERMISSIONLESS: YES` |
| no bugs | honest empty `report.md` + retro, not a vibe |

If those files are missing, they hallucinated the skill. Tell them:

```
stop. load apex-sentinel SKILL.md. run load_card.sh P#.
do not continue from memory.
```

## Depth knobs (you pick; the agent does not)

| You want | Say |
|---|---|
| Full lifecycle | `run apex` / `full audit` |
| Cheap residual | `apex residual` + one CX or one address |
| Kill this H-id | `P7 fp-kill.md on H-0XX — assume it is wrong` |
| Ship or close | `P9 claim_gate then report_gate` |
| Patch the target | `out of hunt: patch <repo> from CONFIRMED-REPORTABLE` |

Do not ask for "keep going until you find something." That is how empty reports
get filled. The 48-hour rule is: one fork/harness probe after SYNTHESIS OPEN,
then kill or expand that probe — not architecture novels.

## Workspace layout the agent should use

```
hunts/<slug>/
  src/                 # clone, optional
  research/            # disk is memory (NOW.md, handshake.md, fp-kill.md, …)
  research/experiments/
```

Pin in `scope.md`: chain, RPC, commit, `Research layer`, authorization.

Brain is global: `~/.apex-sentinel/`. You never edit it by hand except to read
`false-positives.md` / `LEARNINGS.md` after a close.

## Triggers that auto-load this skill

The frontmatter `description` is what Grok matches. Prefer these words at the
start of the message: `run apex`, `apex sentinel`, `apex residual`, `full audit`,
`web3 audit`, `bug hunt`, `bounty hunt`, `ragnarok`.
