# Apex Sentinel

Unified self-learning Web3 audit engine. Orchestrates kensho + ragnarok v4 +
jailbreaker + iykes-web3-bughunt. The `bug-ai-auditor` slot is a routing stub.

**v1.3.0** — component handshake + claim gate. See `CHANGELOG.md`,
`references/handshake.md`, `references/anti-hallucination.md`.

## Install

Drop this directory into a skills loader:

- Grok: `.grok/skills/apex-sentinel`
- Claude: `~/.claude/skills/apex-sentinel`
- Codex: `~/.codex/skills/apex-sentinel`

Then:

```bash
python3 scripts/init_brain.py
python3 scripts/brief.py --product-type vault
bash scripts/load_card.sh P7              # load those files; do not improvise
python3 scripts/claim_gate.py research/   # blocks false CONFIRMED
```

The brain lives at `~/.apex-sentinel/` (outside the skill dir so updates never
clobber learned state).

## Invoke

- `run apex` / `apex sentinel` / `full audit` → lifecycle P0–P10 + retro
- `investigate X` on an OPEN hunt → residual dive, do not restart
- `update the suite` → `scripts/update_check.sh`

## License

Copyright (c) 2026 Gift. All rights reserved. See `LICENSE`.
