#!/usr/bin/env bash
# Apex Sentinel freshness engine (v1.2).
#
# Updates every skill tracked in ~/.apex-sentinel/upstreams.json from its upstream
# repo. Bootstraps the brain + manifest if missing. Works without rsync (cp -a).
# Does NOT overwrite the intentional bug-ai-auditor routing stub.
#
# Usage:   update_check.sh [--dry-run]
# Exit 0 on success (or nothing to do), 1 on any failed update.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

copy_tree() {
  # copy_tree SRC DEST  — replace DEST contents, keep DEST/.git if present
  local SRC="$1" DEST="$2"
  mkdir -p "$DEST"
  local KEEP_GIT=""
  if [ -d "$DEST/.git" ]; then
    KEEP_GIT=$(mktemp -d)
    mv "$DEST/.git" "$KEEP_GIT/.git"
  fi
  # delete dest files except we just moved .git
  find "$DEST" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  cp -a "$SRC"/. "$DEST"/
  rm -rf "$DEST/.git"
  if [ -n "$KEEP_GIT" ]; then
    mv "$KEEP_GIT/.git" "$DEST/.git"
    rm -rf "$KEEP_GIT"
  fi
}

# bootstrap brain + default manifest
python3 "$HERE/init_brain.py" --brain "$BRAIN" || true
[ -f "$MANIFEST" ] || { echo "manifest still missing after init: $MANIFEST"; exit 1; }

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
  printf '%b\n' "$(printf '%s' "$INSTALLS" | tr '\037' '\n')" | while IFS= read -r DEST; do
    [ -n "$DEST" ] || continue
    LABEL=${DEST/#$HOME/'~'}
    # never clobber the intentional stub
    if [ "$(basename "$DEST")" = "bug-ai-auditor" ]; then
      echo "  skip stub: $LABEL (bug-ai-auditor is a routing stub; not overwritten)"
      continue
    fi
    # preserve SOURCE.md across copy installs
    SAVE_SRC=""
    if [ -f "$DEST/SOURCE.md" ]; then
      SAVE_SRC=$(mktemp)
      cp "$DEST/SOURCE.md" "$SAVE_SRC"
    fi
    if [ ! -d "$DEST" ]; then
      echo "  NEW install -> $LABEL (head $LOCAL_HEAD)"
      [ "$DRY" = 0 ] && { mkdir -p "$(dirname "$DEST")"; cp -a "$SRC"/. "$DEST"/; rm -rf "$DEST/.git"; }
      [ -n "$SAVE_SRC" ] && [ "$DRY" = 0 ] && mv "$SAVE_SRC" "$DEST/SOURCE.md"
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
      mkdir -p "$DEST.bak-$DATE"
      cp -a "$DEST"/. "$DEST.bak-$DATE"/ 2>/dev/null || true
      copy_tree "$SRC" "$DEST"
      [ -n "$SAVE_SRC" ] && cp "$SAVE_SRC" "$DEST/SOURCE.md"
    fi
    [ -n "$SAVE_SRC" ] && rm -f "$SAVE_SRC"
  done
done <<< "$LINES"

[ "$DRY" = 1 ] && { echo "(dry run — nothing written)"; exit $((FAILURES > 0)); }

python3 - "$MANIFEST" <<'PY'
import json, sys
from datetime import date
from pathlib import Path
p = Path(sys.argv[1]); m = json.loads(p.read_text())
m["last_checked"] = date.today().isoformat()
p.write_text(json.dumps(m, indent=2) + "\n")
print(f"manifest updated: last_checked={m['last_checked']}")
PY

# mirrors of Apex itself
if [ -x "$HERE/sync_mirrors.sh" ]; then
  bash "$HERE/sync_mirrors.sh" || true
fi

echo "== done ($FAILURES failure(s)) =="
exit $((FAILURES > 0))
