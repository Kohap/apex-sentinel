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
echo "Apex: APPLICATION targets: set Research layer: APPLICATION in scope.md"
