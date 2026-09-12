# FP kill book

One section per H-### that is SURVIVOR or proposed CONFIRMED.
Copy the template. Unanswered question = `claim_gate.py` FAIL.
Do not promote on chat. Jailbreaker six gates + iykes 5 + kensho 5.5 + brain FPs + ragnarok kill.

Verdict vocabulary: FALSE POSITIVE | NEEDS MORE WORK | SURVIVOR | TRUST | CONFIRMED-INTERNAL | CONFIRMED-REPORTABLE

---

## H-000 — <title> (TEMPLATE — delete or replace; never promote)

### Restate (jailbreaker 1.1)
- Claim:
- Root cause (file:line OR bytecode offset):
- Trigger (who, call, state):
- Impact (asset, amount, persist?):
- Threat model (stranger / role / admin):
- Bug class:

### Permissionless
- PERMISSIONLESS: YES / NO
- Stranger with no key, no Safe seat, no 7702-as-extra-vote, no keeper/signer:
- If NO → TRUST. Stop. Do not CONFIRMED-REPORTABLE.

### Jailbreaker six gates
| Gate | PASS/FAIL | Evidence (file, cmd, or revert selector) |
|---|---|---|
| Process |  | |
| Reachability |  | |
| Real Impact |  | |
| PoC Validation |  | |
| Math Bounds |  | |
| Environment |  | |

Any FAIL → FALSE POSITIVE. Write why in `killed.md`.

### Iykes second-opinion
1. Gas-feasible?
2. Access control actually blocks it?
3. State reachable in production config?
4. Mitigating path elsewhere?
5. Temporary condition killed (restores = not theft)?

### Kensho 5.5
1. Unprivileged trigger over the wire?
2. Exact upstream check that might stop it (quote file:line — go read it)?
3. Permissionless vs centralization-by-design?
4. Duplicate of published audit / Known Issues?
5. Honest severity and bound?

### Brain
- FP patterns checked: <quote matching rows from ~/.apex-sentinel/false-positives.md, or "none matched YYYY-MM-DD">
- Taxonomy class: AS-XXX

### Ragnarok kill mutations
| Mutation (one variable) | Result |
|---|---|
| caller / entry / amount / timing / token | |

### Harness
- Experiment file:
- Command:
- Observed effect (numbers):

### Verdict
VERDICT: FALSE POSITIVE | NEEDS MORE WORK | SURVIVOR | TRUST | CONFIRMED-INTERNAL | CONFIRMED-REPORTABLE
