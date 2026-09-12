# Known false-positive patterns

Check here FIRST during P7 falsification.

| Pattern | Why it died | Date | Source |
|---|---|---|---|
| 1-step Ownable EOA (even nonce 0, tiny ETH, not 7702) as permissionless protocol takeover | Admin rug is TRUST. Prior owner can configure then transferOwnership. Certora ACK confirms the trust model. | 2026-09-12 | umia L-053 |
| Gnosis Safe M-of-N (3/6, 3/7, 2/4) as 1-of-N or "the protocol is stolen" | Threshold is live; disjoint EOAs; no modules/guard does not lower M. Historical 1-of-2 bootstrap that closed is history. | 2026-09-12 | umia L-052 |
| EIP-7702 MetaMask EIP7702StatelessDeleGator on a Safe owner = extra vote | Delegator is the owner's signing path, not a new signer. Codesize > 0 on an owner is not a free vote. | 2026-09-12 | umia P1 owner |
| Vendored gate LOCKED / exit 3 on a hunt whose NOW.md says OPEN | Heading-regex / v2 reconstruction lock. Substance override. Do not restart P0–P5. | 2026-09-12 | umia / tessera-v |
| SURVIVOR or INCONCLUSIVE written into report.md | Report gate forbids it. Honest empty is the only legal non-finding report. | 2026-09-12 | ragnarok report_gate |
| "Audited" / Certora / Known Issues as proof of safety | Novelty prior, not a skip and not a stranger-path proof. | 2026-09-12 | umia |
| Temporary price/share wobble as Critical bank-run | iykes temporary-vs-persistent: must not restore. | 2026-08-25 | iykes |
| Decompiled bytecode function identity / invented keeper gate | Bytecode reversing is a hypothesis generator. Fork-replay the real selector. | 2026-08 | kensho 5.4.1 |
| Safe `require(extcodesize(multisig)==0)` inverted as a live steal | Often the original stuck-funds cause, not an attacker primitive. | 2026-08 | kensho 5.7 |
| SELFDESTRUCT hit in CBOR metadata trailer | Data, not code. | 2026-08 | kensho 5.7 |
