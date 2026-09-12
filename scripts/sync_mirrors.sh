#!/usr/bin/env bash
# Sync canonical Apex Sentinel install -> mirror copies (keeps all loaders identical).
# Canonical is wherever this script lives (..).
# Mirrors: ~/.claude/skills, ~/.codex/skills, ~/.config/opencode/skills, ~/.grok/skills.
# Uses cp -a (rsync optional). Never deletes SOURCE.md-only extras at dest .git.
set -eu
CANON="$(cd "$(dirname "$0")/.." && pwd)"
NAME=$(basename "$CANON")
MIRRORS="$HOME/.claude/skills $HOME/.codex/skills $HOME/.config/opencode/skills $HOME/.grok/skills"
for M in $MIRRORS; do
  DEST="$M/$NAME"
  [ "$DEST" = "$CANON" ] && continue
  # skip if parent skills dir doesn't exist (don't create unused loaders)
  [ -d "$M" ] || continue
  mkdir -p "$DEST"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete --exclude '.git/' --exclude 'SOURCE.md' "$CANON/" "$DEST/"
  else
    find "$DEST" -mindepth 1 -maxdepth 1 ! -name '.git' ! -name 'SOURCE.md' -exec rm -rf {} +
    cp -a "$CANON"/. "$DEST"/
    rm -rf "$DEST/.git"
  fi
  echo "synced: $DEST"
done
echo "mirrors in sync with $CANON"
