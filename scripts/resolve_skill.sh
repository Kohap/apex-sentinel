#!/usr/bin/env bash
# Resolve a component skill directory. Prints the first hit and exits 0.
# Usage: resolve_skill.sh <name>
set -eu
NAME="${1:-}"
[ -n "$NAME" ] || { echo "usage: resolve_skill.sh <name>" >&2; exit 2; }
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# If we are asking for apex-sentinel, prefer the tree that contains this script.
if [ "$NAME" = "apex-sentinel" ]; then
  echo "$(cd "$HERE/.." && pwd)"
  exit 0
fi
CANDIDATES=""
[ -n "${APEX_SKILLS:-}" ] && CANDIDATES="$CANDIDATES $APEX_SKILLS"
# Walk up from this script looking for a sibling skills root (.grok/skills etc.)
ROOT="$(cd "$HERE/../.." && pwd)"
CANDIDATES="$CANDIDATES $ROOT"
CANDIDATES="$CANDIDATES /workspace/.grok/skills"
CANDIDATES="$CANDIDATES $HOME/.grok/skills $HOME/.claude/skills $HOME/.codex/skills $HOME/.config/opencode/skills"
for d in $CANDIDATES; do
  [ -d "$d/$NAME" ] && [ -f "$d/$NAME/SKILL.md" ] && { echo "$d/$NAME"; exit 0; }
done
echo "resolve_skill.sh: $NAME not found" >&2
exit 1
