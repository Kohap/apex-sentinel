#!/usr/bin/env bash
# Apex Sentinel scaffold — ragnarok v4 plus Research layer field.
# Usage: ./scaffold.sh <target-dir>
# Idempotent: never overwrites existing files.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR="$HERE/vendor/ragnarok/scaffold.sh"
TARGET="${1:-$PWD}"
if [ -x "$VENDOR" ]; then
  bash "$VENDOR" "$TARGET"
else
  echo "apex scaffold: vendored ragnarok scaffold missing" >&2
  exit 1
fi
SCOPE="$TARGET/research/scope.md"
if [ -f "$SCOPE" ] && ! grep -q 'Research layer:' "$SCOPE"; then
  cat >> "$SCOPE" <<'EOF'

## Research layer (Apex v1.2 — REQUIRED)
- Research layer: EVM / APPLICATION / SOLANA   # <-- set one
- APPLICATION skips the EVM reconstruction gate (compose → policy → simulate → execute).
EOF
fi
echo
echo "Apex: after a thin map, run:  $HERE/gate_check.sh $TARGET/research"

RES="$TARGET/research"
HERE_DEFAULTS="$HERE/defaults"
for dst in handshake.md fp-kill.md; do
  if [ ! -f "$RES/$dst" ] && [ -f "$HERE_DEFAULTS/$dst" ]; then
    cp "$HERE_DEFAULTS/$dst" "$RES/$dst"
  fi
done
for f in intake.md recon.md auth-triage.md; do
  if [ ! -f "$RES/$f" ]; then
    printf "# %s\n\n(artifact-or-it-did-not-happen — fill from the owning component)\n" "${f%.md}" > "$RES/$f"
  fi
done
echo "Apex: each phase:             $HERE/load_card.sh P#"
echo "Apex: before any finding:     python3 $HERE/claim_gate.py $TARGET/research"
echo "Apex: APPLICATION targets: set Research layer: APPLICATION in scope.md"
