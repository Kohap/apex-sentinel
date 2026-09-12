# Heuristics

Ranked by field performance. Demote to Dead after two consecutive failures.

## Live

- Auth triage from `0xdead` on every state-changing admin/keeper fn (iykes step4). Hit: first-pass Criticals.
- Thin map = component graph table with real 0x / program ids + one composition trace, then SYNTHESIS OPEN. Do not write architecture novels first.
- Cheapest falsifier first: storage read, one `eth_call`, one unit test. Fork last.
- Representations table: token / shares / claim / settlement / actual. Divergence is a CX card, not a bug class.
- ERC-4626: first-depositor, donation, receiver==0x0, rounding direction.
- Policy/MCP/exec agents: kill switch (`false ?? env`), server-owned cooldown, simulate every write, compose-switch fallthrough, `Number()` vs wei-18, idempotency key, error redaction.
- Safe: tx-service is `api.safe.global` (308 from old hosts); checksum the address; fallback handler slot `keccak256("fallback_manager.handler.address")` = `0x6c9a6c4a39284e37ed1cf53d337577d14212a4870fb976a4366c693b939918d5`.
- Publicnode archive `eth_getLogs` 403 — chunk, other RPC, or don't claim the query ran.
- Ledger append-only. Never empty-StrReplace `killed.md` / `leads.md`.
- Grok skill root: `/workspace/.grok/skills/`. `rsync` may be missing; use `cp -a`.

## Dead

- (none yet)
