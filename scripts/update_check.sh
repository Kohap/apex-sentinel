#!/usr/bin/env bash
# Apex Sentinel freshness engine.
#
# Updates every skill tracked in ~/.apex-sentinel/upstreams.json from its upstream repo:
#   - installs that are git clones : stash local edits -> fast-forward pull -> restore
#   - plain-copy installs          : rsync --delete from a fresh upstream clone,
#                                    previous version backed up to <dir>.bak-<date>/
# Special case: "bug-ai-auditor" directories get their SKILL.md / agents/openai.yaml
# from the newest commit that still carried the bug-ai-auditor identity (the upstream
# repo later renamed its SKILL.md to jailbreaker).
#
# Usage:   update_check.sh [--dry-run]
# Exit 0 on success (or nothing to do), 1 on any failed update.
set -u

BRAIN="${APEX_BRAIN:-$HOME/.apex-sentinel}"
MANIFEST="$BRAIN/upstreams.json"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1
DATE=$(date +%Y%m%d)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
FAILURES=0

command -v git >/dev/null || { echo "git required"; exit 1; }
command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
command -v rsync >/dev/null || { echo "rsync required"; exit 1; }

[ -f "$MANIFEST" ] || { echo "manifest missing: $MANIFEST"; exit 1; }

# manifest -> lines of: url<TAB>branch<TAB>space-separated-installs
LINES=$(python3 - "$MANIFEST" <<'PY'
import json, sys, os
m = json.load(open(sys.argv[1]))
for r in m.get("repos", []):
    print("\t".join([r["url"], r["branch"], "\x1f".join(os.path.expanduser(p) for p in r["installs"])]))
PY
)

echo "== Apex Sentinel update check $(date +%F) =="
while IFS=$'\t' read -r URL BRANCH INSTALLS; do
  [ -n "$URL" ] || continue
  NAME=$(basename "$URL" .git)
  SRC="$TMP/$NAME"
  echo "--- $NAME ($URL)"
  git clone -q --depth 50 -b "$BRANCH" "$URL" "$SRC" 2>/dev/null \
    || { echo "  ERROR: clone failed (offline? bad branch?)"; FAILURES=$((FAILURES+1)); continue; }
  LOCAL_HEAD=$(git -C "$SRC" rev-parse --short HEAD)
  # installs are \x1f-separated (paths may contain spaces); %b\n ensures the
  # final path still terminates as a readable line for the `while read` below
  printf '%b\n' "$(printf '%s' "$INSTALLS" | tr '\037' '\n')" | while IFS= read -r DEST; do
    [ -n "$DEST" ] || continue
    LABEL=${DEST/#$HOME/'~'}
    if [ ! -d "$DEST" ]; then
      echo "  NEW install -> $LABEL"
      [ "$DRY" = 0 ] && { mkdir -p "$(dirname "$DEST")"; rsync -a --exclude '.git/' "$SRC/" "$DEST/"; }
      continue
    fi
    if [ -d "$DEST/.git" ]; then
      DIRTY=$(git -C "$DEST" status --porcelain | head -5)
      UPD=$(git -C "$DEST" fetch -q origin "$BRANCH" 2>&1 && git -C "$DEST" rev-list --count HEAD..origin/"$BRANCH")
      if [ "${UPD:-0}" = "0" ]; then echo "  up-to-date: $LABEL"; continue; fi
      echo "  updating $LABEL (${UPD} new commits, remote head $LOCAL_HEAD)"
      [ "$DRY" = 1 ] && continue
      if [ -n "$DIRTY" ]; then
        git -C "$DEST" diff > "$DEST.local-changes-$DATE.patch"
        echo "    local edits saved to $LABEL.local-changes-$DATE.patch"
        git -C "$DEST" checkout -q -- . || true
        git -C "$DEST" reset -q --hard HEAD || true
      fi
      git -C "$DEST" merge -q --ff-only origin/"$BRANCH" 2>/dev/null \
        || echo "    WARN: non-fast-forward at $LABEL, left untouched"
    else
      echo "  syncing copy -> $LABEL (backup: $LABEL.bak-$DATE/)"
      [ "$DRY" = 1 ] && continue
      mkdir -p "$DEST"
      rsync -a --delete --exclude '.git/' \
            --backup --backup-dir="$DEST.bak-$DATE" "$SRC/" "$DEST/"
    fi
  done
  # bug-ai-auditor identity repair
  printf '%s' "$INSTALLS" | tr '\037' '\n' | grep '/bug-ai-auditor$' | while IFS= read -r DEST; do    [ -d "$DEST" ] || continue
    SHA=""
    for C in $(git -C "$SRC" log --format=%h -- SKILL.md); do
      N=$(git -C "$SRC" show "$C":SKILL.md 2>/dev/null | sed -n 's/^name:[[:space:]]*//p' | head -1)
      if [ "$N" = "bug-ai-auditor" ]; then SHA="$C"; break; fi
    done
    [ -n "$SHA" ] || continue
    [ "$DRY" = 0 ] && {
      git -C "$SRC" show "$SHA":SKILL.md > "$DEST/SKILL.md"
      git -C "$SRC" show "$SHA":agents/openai.yaml > "$DEST/agents/openai.yaml" 2>/dev/null
      echo "  restored bug-ai-auditor identity in ${DEST/#$HOME/'~'} (from $SHA)"
    }
  done
done <<< "$LINES"

[ "$DRY" = 1 ] && { echo "(dry run — nothing written)"; exit $((FAILURES > 0)); }

python3 - "$MANIFEST" <<'PY'
import json, sys
from datetime import date
from pathlib import Path
p = Path(sys.argv[1]); m = json.loads(p.read_text())
m["last_checked"] = date.today().isoformat()
p.write_text(json.dumps(m, indent=2))
print(f"manifest updated: last_checked={m['last_checked']}")
PY

echo "== done ($FAILURES failure(s)) =="
exit $((FAILURES > 0))
