# Anti-hallucination / anti-false-positive

LLMs are biased toward seeing bugs and filling templates. Apex treats that as a
defect in the operator, not a feature of the hunt.

Load with `handshake.md`. This file is the "never" list.

## Never

1. **Cite a file, selector, line, CVE, inbox, TVL, or RPC result you did not read or run this session.** If the number came from a prior turn's chat, re-read the disk artifact or re-query. Chat is not a source.
2. **Mark RUNTIME_VERIFIED because the code "would" do it.** RUNTIME means a harness, `eth_call`, or fork test produced the transition. "Would revert" without a run is SOURCE.
3. **Write SURVIVOR / INCONCLUSIVE / Potential into `report.md`.** Honest empty sentence, or CONFIRMED-REPORTABLE after `claim_gate.py` PASS. Nothing else.
4. **Call TRUST a permissionless exploit.** Owner, admin, 1-step Ownable EOA (any nonce), Safe M-of-N, EIP-7702 delegator-as-vote, keeper, signer, Certora ACK of platform owner. Label TRUST. Do not JACKPOT.
5. **Start from a vulnerability category.** Ragnarok v4: invent the impossible state first. "Check for reentrancy" is the wrong generator.
6. **Invent a component run.** If `auth-triage.md` / `fp-kill.md` / `experiments/` is missing, you did not run iykes / jailbreaker / the harness.
7. **Guess `security@` or a DM handle.** iykes 10A: URL + quote or do not send.
8. **Overwrite `killed.md` / `leads.md` / `hypotheses.md`.** Append. Unique old_string. Disk is memory.
9. **Treat a 403 / empty log / failed RPC as "no events exist."** Record BLOCKED. Publicnode archive `eth_getLogs` 403 is a known FP of "quiet chain."
10. **Promote because the hunt was long.** Empty report after a week is the correct output. Fabrication is the failure.

## Six + five + five (P7 gauntlet)

Every H-### that is still alive at P7 gets one section in `fp-kill.md`. Copy
`scripts/defaults/fp-kill.md`. Unanswered line = FAIL `claim_gate.py`.

**Jailbreaker six gates — all PASS or it is a false positive:**

| Gate | Pass |
|---|---|
| Process | Evidence for every prior step is on disk |
| Reachability | Attacker-controlled path to the sink, confirmed |
| Real Impact | Value moves / freezes / is stolen. Not "looks unsafe" |
| PoC Validation | Harness or `eth_call` showed control + trigger + impact |
| Math Bounds | The condition is algebraically possible |
| Environment | No live guard / hook / token behavior fully blocks it |

**Iykes second-opinion:** gas-feasible? access control already blocks? production-reachable? mitigating path elsewhere? temporary-vs-persistent killed?

**Kensho §5.5:** unprivileged over the wire? exact upstream check (go read it)? permissionless vs designed trust? duplicate of audit/Known Issues? honest bound?

**Brain:** quote matching `false-positives.md` rows or write `none matched`.

**Ragnarok `kill.md`:** at least one mutation in the same harness that tried to make it die.

## Verdict vocabulary (do not invent new labels)

| Label | Meaning | May enter `report.md`? |
|---|---|---|
| KILLED / FALSE POSITIVE | Gauntlet failed | No. `killed.md` only |
| NEEDS MORE WORK | Missing evidence | No |
| SURVIVOR | Alive, not proven | No. `survivors.md` / `final.md` |
| TRUST | Admin/role-by-design | No as JACKPOT. Optional note in `final.md` |
| CONFIRMED-INTERNAL | Proven but Med/Low or unquantified | `final.md` + Brain only |
| CONFIRMED-REPORTABLE | Crit/High + permissionless + quantified + PoC + gauntlet PASS | Yes, after claim_gate |

## Rationalizations to reject (jailbreaker 1.4)

- "This pattern looks dangerous, so it's a vuln."
- "Skip full verification for efficiency."
- "Similar code was vulnerable elsewhere."
- "This is clearly Critical."
- "The hunt needs a finding."
- "The owner key has nonce 0 so it's abandoned" (still TRUST).
- "Safe has no guard so threshold doesn't count" (still M-of-N).
- "7702 code on an owner is an extra vote" (it is their signing path).
- "I used jailbreaker internally" (no `fp-kill.md` = you did not).

## Pre-ship commands

```
python3 $APEX/scripts/component_check.py research/
python3 $APEX/scripts/claim_gate.py research/
bash $APEX/scripts/report_gate.sh research/
```

Any FAIL → do not disclose. Fix the artifact or demote the claim.
