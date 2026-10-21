# Pashov-derived lenses (source notes)

Adapted from pashov/skills `solidity-auditor` v4.1 (senior-auditor SOP, 12 hacking agents, judging gates). The runtime text is in `apex_agent/methodology.md` → "Hunting discipline". This file records origin and follow-ups.

## Mapping to Apex v2 gates
| Pashov gate | Apex gate |
|---|---|
| Attack execution (no guard interrupts) | existing_protections |
| Reachability | reachability, scope |
| Unprivileged trigger / admin amplifier | reachability + impact evidence |
| Material impact | impact |
| (proof required) | reproduction, control_case |

## Proposed follow-ups (not implemented here)
1. Optional `confidence` field (start 100; -20 partial path, -15 bounded impact, -10 specific state; <75 = no fix block). Needs schema + report change.
2. Optional on-chain mode for live targets: bytecode match vs canonical source (mask immutables), then a pinned Foundry fork (`--fork-block-number head-5` on RPCs without archive state) for state-dependent PoCs. Conflicts with today's offline-only rule; needs an explicit opt-in flag.
3. Loop mode: carry a known-findings ledger across `apex resume` so later rounds hunt new ground.
