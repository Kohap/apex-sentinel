## On-chain mode (opt-in by the operator)

The operator started a LOCAL fork and gave its loopback RPC below. This is the only
network endpoint you may use, and only to read state and run simulations on the fork.
Never use any other RPC, broadcast to a live chain, use real keys, or touch user funds.
Fork-only transactions (anvil impersonation, cheatcodes, `vm.createSelectFork`) are fine.

1. Verify before hunting. For each listed address, compare its deployed runtime bytecode
   (`cast code <addr> --rpc-url <fork>`) with the bytecode built from source/, masking
   immutable references and metadata. Record each match or mismatch with byte counts in
   coverage. A mismatch means the source may not be what is deployed, so record it as a
   blocker rather than auditing the wrong code. If source/ is a known canonical upstream
   and bytecode matches, say so and move effort to the deployment-specific surface
   (configuration, oracles, parameters, roles).
2. Read live state that changes severity: roles and owners, oracle wiring and freshness,
   balances vs liabilities (solvency), caps, pool depth, and debt per market. Rank
   hypotheses by value at risk against attacker cost.
   Field-tested checks (from live engagements):
   - Solvency by event replay: rebuild each pool's liability from its own
     Deposit/Withdraw/EmergencyWithdraw logs (net of deposit fees) and compare to
     `balanceOf(contract)` to the wei. A gap names the exact pool to investigate.
   - Fee-on-transfer and rebasing collateral: where a contract credits the stated
     `_amount` instead of the balance delta, find the transfer that short-paid it and
     check whether outbound transfers are taxed too. Size the gap in USD before you
     escalate it; one taxed inbound transfer is usually dust.
   - Owner-posted prices and caps are a trust assumption, not a manipulation path.
     Hunt the arithmetic, the decimals, and cap enforcement instead.
   - Pot and cap exhaustion: read the remaining payout and each per-asset cap. Once a
     bounded pot is spent, a hypothesis that needs a future payout is moot.
3. Reproduce state-dependent claims with Foundry tests against the fork
   (`forge test --fork-url <fork> --fork-block-number <block>`), or with `cast`
   scripts that call the deployed contracts. A reproduction must execute the deployed
   contract or the source/ build, never a rewritten model.
4. Quantify. Put concrete numbers in impact: the attacker's capital and cost (swaps,
   fees, waiting time) and the value extracted or bad debt created, all measured on the
   fork. The control case must show the same call succeeding for a legitimate user.
5. If the fork is unreachable, lacks the needed historical state, or a required tool
   (forge, cast, anvil) is missing, record the exact blocker. Do not fall back to a
   remote RPC.
