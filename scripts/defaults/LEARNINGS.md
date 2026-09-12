# Apex Sentinel — LEARNINGS

Append-only. `retro.py` writes here. Do not delete rows; supersede.

| ID | Date | Type | Target | One-line |
|----|------|------|--------|----------|
| L-1 | 2026-09-12 | method | umia | V2 reconstruction lock is retired; SYNTHESIS OPEN after thin map |
| L-2 | 2026-09-12 | fp | umia | Hub 1-step Ownable EOA is TRUST not permissionless JACKPOT |
| L-3 | 2026-09-12 | fp | umia | Safe 3/6 and EIP-7702 delegator are not extra votes |
| L-4 | 2026-09-12 | method | umia | Heading-regex gate LOCKED ≠ restart P0–P5 |
| L-5 | 2026-09-12 | method | general | "audit skill" means Apex Sentinel not the stub |
| L-6 | 2026-09-12 | method | general | investigate/continue after OPEN = residual P8 |
| L-7 | 2026-09-12 | finding | keeperhub-sky-exec | Client killSwitch:false overrode server KILL_SWITCH |
| L-8 | 2026-09-12 | finding | keeperhub-sky-exec | Client-omitted cooldown + 0x0 receiver + wrong dry-run |
| L-9 | 2026-09-12 | method | tessera-v | Honest empty report.md is a valid close |
| L-10 | 2026-09-12 | method | general | Brain must be bootstrapped; rsync is optional |

### L-1 | 2026-09-12 | method
TARGET: umia
CLASS: -
PRODUCT: launchpad
EVIDENCE: DEPLOYMENT
BODY: Apex 1.1 routed ragnarok v2 and forbade exploit analysis until reconstruction completed. Ragnarok v4 (ba08271, 2026-09-04) opens SYNTHESIS after Phase 0 + thin map. On Umia, vendored-gate exit 3 was treated as "restart P0–P5" while NOW.md already said OPEN and coverage ~90%. Rule: substance override; never restart an in-progress hunt.
TAGS: gate,ragnarok-v4

### L-2 | 2026-09-12 | fp
TARGET: umia
CLASS: AS-021
PRODUCT: launchpad
EVIDENCE: DEPLOYMENT
BODY: Hub owner 0x7ad8Bc2Ee86F6ee9c05ED7d4795C121Db374E705 is a codesize-0 EOA, nonce 0, ~0.0058 ETH, not 7702. Same key owns Hub UUPS + Venture beacon. 1-step Ownable, no timelock. Certora ACK platform owner. L-053 FALSIFIED as permissionless takeover. TRUST residual only. Do not ship as JACKPOT.
TAGS: false-positive,trust

### L-3 | 2026-09-12 | fp
TARGET: umia
CLASS: AS-029
PRODUCT: launchpad
EVIDENCE: DEPLOYMENT
BODY: Operating Acc Safe 3/6 0x04C412E9… isTeamMember. INC 3/7, P9 3/6, P1 2/4. No modules, no guard, disjoint EOAs. P1 owner 0x0Cc6C357… is MetaMask EIP7702StatelessDeleGator v1.3.0 — not a free extra vote. L-052 FALSIFIED.
TAGS: false-positive,safe,eip7702

### L-4 | 2026-09-12 | method
TARGET: umia
CLASS: -
PRODUCT: launchpad
EVIDENCE: SOURCE
BODY: v4 check_phase1 reported every architecture/asset-flows/trust-boundaries section as placeholder on a 7.8KB real map with live 0x addresses. section_body/heading-regex is brittle. Believe file substance (size + addresses + NOW.md), not the regex.
TAGS: gate,awk

### L-5 | 2026-09-12 | method
TARGET: general
CLASS: -
PRODUCT: -
EVIDENCE: SOURCE
BODY: User said "the audit skill". Operators loaded bug-ai-auditor (a stub) instead of Apex Sentinel. Stub routes to jailbreaker playbooks. "Audit skill" = this orchestrator.
TAGS: routing

### L-6 | 2026-09-12 | method
TARGET: general
CLASS: -
PRODUCT: -
EVIDENCE: SOURCE
BODY: Short orders after OPEN ("investigate Hub hot EOA", "keep hunting", "so no single reportable vulnerability") are residual P8 dives. Do not re-run intake or reconstruction.
TAGS: intent

### L-7 | 2026-09-12 | finding
TARGET: keeperhub-sky-exec
CLASS: AS-022
PRODUCT: policy
EVIDENCE: RUNTIME
BODY: Client killSwitch:false disabled server KILL_SWITCH because `false ?? env` treats false as present. Force ON only via env or overrides.killSwitch === true. HIGH. Patched and pushed 3798594.
TAGS: kill-switch,application
SEVERITY: High

### L-8 | 2026-09-12 | finding
TARGET: keeperhub-sky-exec
CLASS: AS-023
PRODUCT: policy
EVIDENCE: RUNTIME
BODY: Cooldown only applied when client sent lastExecuteAtMs; omit it and skip. Receiver defaulted to 0x0 (ERC-4626 mint/burn to zero). Dry-run withdraw simulated deposit; deposit graphs dry-ran approve only. Redeem prompt composed a deposit. Date.now() idempotency. Number() IEEE cap bypass. Error clipped API key 8 chars. All patched @ 3798594.
TAGS: cooldown,receiver,simulate,compose

### L-9 | 2026-09-12 | method
TARGET: tessera-v
CLASS: -
PRODUCT: other
EVIDENCE: SOURCE
BODY: Tessera-v and Umia both correctly kept report.md as the honest empty report. SURVIVOR/INCONCLUSIVE never enter report.md. Fabricating a finding after a long hunt is an anti-pattern.
TAGS: report-gate

### L-10 | 2026-09-12 | method
TARGET: general
CLASS: -
PRODUCT: -
EVIDENCE: SOURCE
BODY: ~/.apex-sentinel/ did not exist in the Grok sandbox so brief.py warned "upstreams never checked" and update_check.sh died on a missing manifest. rsync is also missing. init_brain.py + cp -a fallback. Grok skills live at /workspace/.grok/skills not ~/.claude/skills.
TAGS: brain,paths,rsync
