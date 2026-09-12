# Field lessons (Umia, Tessera-v, KeeperHub) — 2026-09-12

Errors and hallucinations from live Apex engagements. Folded into v1.2.0 rules.
Do not re-learn these the hard way.

## Orchestration

1. **V2 reconstruction lock caused a deadlock.** Apex 1.1.0 said "no exploit analysis
   until reconstruction is complete." Ragnarok v4 (2026-09-04) opens SYNTHESIS after a
   thin map. On Umia, `gate_check.sh` exit 3 ("work ahead of gate") was treated as a
   reason to restart P0–P5 while NOW.md already said OPEN and coverage ~90%. **Never
   restart an in-progress hunt because a newly vendored gate is LOCKED.** Substance
   override in `scripts/gate_check.sh`.
2. **"Investigate X" is residual P8**, not a new lifecycle. "Keep hunting" / "continue"
   / "Hub hot EOA" after OPEN = cheapest unfalsified CX or a named residual dive.
3. **"Audit skill" means Apex Sentinel**, not `bug-ai-auditor`. That directory is a
   routing stub (no public upstream). Saying so in chat and then loading the stub is a
   hallucination.
4. **Grok loads `/workspace/.grok/skills/`**, not only `~/.claude/skills/`. Path
   resolver is `scripts/resolve_skill.sh`. Quick-start snippets that hardcode Claude's
   path fail silently here.
5. **Brain missing was a silent fail.** `brief.py` printed "upstreams never checked"
   and `update_check.sh` exited 1 on a missing manifest. Bootstrap with
   `init_brain.py`. Do not hunt without a brain.
6. **Phase R was skipped** on Umia and KeeperHub. Retro is the close. Honest empty
   `report.md` is a valid close.
7. **`rsync` is not on the Grok PATH.** Freshness/mirror scripts must `cp -a` fallback.

## Evidence / TRUST vs permissionless

8. **1-step Ownable EOA is TRUST**, even when the key has nonce 0, ~0.0058 ETH, and is
   not EIP-7702. Prior owner can `transferOwnership` after configuring. Certora "ACK
   platform owner" confirms the trust model; it is not a stranger takeover. Umia L-053
   FALSIFIED as permissionless Hub takeover. Do not ship Hub EOA as JACKPOT.
9. **Safe M-of-N is TRUST.** Umia OP 3/6, INC 3/7, P9 3/6, P1 2/4. Disjoint EOAs, no
   modules, no guard, no protocol-key overlap. Historical 1-of-2 bootstrap that closed
   is history, not the live threshold.
10. **EIP-7702 MetaMask `EIP7702StatelessDeleGator` on a Safe owner is not an extra
    vote.** P1 owner `0x0Cc6C357…` is a delegator contract, not a free signer. L-052
    FALSIFIED.
11. **SURVIVOR / INCONCLUSIVE never enter `report.md`.** Honest empty is the only
    legal non-finding report. Both Umia and Tessera-v correctly kept it empty; do not
    "fill the report" after a long hunt.

## Application layer (KeeperHub Sky Exec)

EVM reconstruction gate does not apply. Hunt the exec path:

`compose → policy → simulate → execute`

Confirmed and patched (repo `Kohap/keeperhub-sky-exec` @ `3798594`):

12. **Client `killSwitch: false` disabled the server kill switch** (`false ?? env`).
    Client false must not override env ON. HIGH.
13. **Cooldown bypass:** policy only checked `lastExecuteAtMs` if the client sent it.
    Omit the field, skip the cooldown. Server must own the clock.
14. **Dry-run simulated the wrong function.** Withdraw dry-ran deposit; deposit graphs
    dry-ran approve only. Simulate **every** write node (approve then vault).
15. **ERC-4626 `receiver` defaulted to `0x0`.** Mint/burn to zero. Resolve org wallet;
    reject zero address on deposit/withdraw/redeem.
16. **Redeem prompt composed a deposit workflow.** Falling through a switch is a
    fund-routing bug, not a UX bug.
17. **`Date.now()` idempotency keys** double-exec across retries. Bucket by cooldown
    window.
18. **`Number()` vs wei-18** IEEE rounding at the cap boundary. Parse decimal strings;
    reject scientific notation; compare in wei.
19. **Error paths leaked API key prefix** (8 chars). Redact.

## Ledger / RPC / Safe tooling

20. **Never overwrite `killed.md` / `leads.md` with empty StrReplace.** Twice on Umia
    this destroyed H-002… history. Append only. Unique old_string when editing.
21. **Publicnode archive `eth_getLogs` 403.** Chunk, switch RPC, or don't pretend the
    log query ran.
22. **Safe tx-service 308 → `api.safe.global`.** Checksum the address. Fallback handler
    slot is `keccak256("fallback_manager.handler.address")` =
    `0x6c9a6c4a39284e37ed1cf53d337577d14212a4870fb976a4366c693b939918d5` — not a typed
    hash you invented.
23. **Heading-regex gates false-LOCK filled artifacts.** Umia architecture.md is a
    real 7.8KB component graph with 0x addresses; v4 still reported "placeholder
    section" when `section_body` returned empty under this awk. Believe the files, not
    the regex.

## What is not a finding

- Admin can rug by design (Hub UUPS + Venture beacon, same EOA).
- Safe 3/6 spending $120k/mo as `isTeamMember`.
- Test-only remnants (Umia H-014 on V1/V2/V4 test ventures).
- `winningThreshold` 2% that still needs `marketCreationSigner` (L-041).
- Org Turnkey EOA compromise (KeeperHub) — TRUST.


## Component use (v1.3)

24. **Naming a skill is not using it.** Apex 1.2 routed to jailbreaker / iykes /
    kensho in a table and the operator improvised from memory. False positives
    and fabricated reports follow. v1.3: `load_card.sh` → load that file →
    produce the artifact → `component_check.py` / `claim_gate.py`.
25. **P7 skipped = FP shipped.** Jailbreaker six gates, iykes 5, kensho 5.5,
    and quoted brain FPs all belong in `fp-kill.md`. "I killed it in chat" is
    not a kill attempt.
26. **CONFIRMED without a harness is SOURCE**, not RUNTIME. claim_gate fails it.
