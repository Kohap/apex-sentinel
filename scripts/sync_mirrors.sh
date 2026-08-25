#!/usr/bin/env bash
# Sync canonical Apex Sentinel install -> mirror copies (keeps all loaders identical).
# Canonical is wherever this script lives (..). Mirrors: ~/.codex/skills, ~/.config/opencode/skills.
set -eu
CANON="$(cd "$(dirname "$0")/.." && pwd)"
NAME=$(basename "$CANON")
MIRRORS="$HOME/.codex/skills $HOME/.config/opencode/skills"
for M in $MIRRORS; do
  DEST="$M/$NAME"
  [ "$DEST" = "$CANON" ] && continue
  mkdir -p "$DEST"
  rsync -a --delete --exclude '.git/' "$CANON/" "$DEST/"
  echo "synced: $DEST"
done
echo "mirrors in sync with $CANON"
