#!/usr/bin/env python3
"""Bootstrap ~/.apex-sentinel/ from scripts/defaults/ if missing.

Idempotent: never overwrites a non-empty LEARNINGS.md or a taxonomy that
already has classes. Safe to run at every P0 / brief.py / update_check.sh.

Usage:
  init_brain.py [--brain ~/.apex-sentinel]
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULTS = HERE / "defaults"


def copy_if_missing(src: Path, dest: Path) -> bool:
    if dest.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def merge_upstreams(src: Path, dest: Path) -> None:
    seed = json.loads(src.read_text())
    if not dest.exists():
        dest.write_text(json.dumps(seed, indent=2) + "\n")
        return
    live = json.loads(dest.read_text())
    have = {(r.get("url"), r.get("branch")) for r in live.get("repos", [])}
    for r in seed.get("repos", []):
        if (r.get("url"), r.get("branch")) not in have:
            live.setdefault("repos", []).append(r)
    dest.write_text(json.dumps(live, indent=2) + "\n")


def merge_taxonomy(src: Path, dest: Path) -> None:
    seed = json.loads(src.read_text())
    if not dest.exists():
        dest.write_text(json.dumps(seed, indent=2) + "\n")
        return
    live = json.loads(dest.read_text())
    have = {c.get("id") for c in live.get("classes", [])}
    added = 0
    for c in seed.get("classes", []):
        if c.get("id") not in have:
            live.setdefault("classes", []).append(c)
            added += 1
    if added:
        live.setdefault("_meta", {})["last_updated"] = date.today().isoformat()
        dest.write_text(json.dumps(live, indent=2) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brain", default="~/.apex-sentinel")
    args = ap.parse_args()
    brain = Path(args.brain).expanduser()
    brain.mkdir(parents=True, exist_ok=True)

    created = []
    for name in ("LEARNINGS.md", "false-positives.md", "heuristics.md", "targets.json"):
        src = DEFAULTS / name
        if src.exists() and copy_if_missing(src, brain / name):
            created.append(name)

    if (DEFAULTS / "taxonomy.json").exists():
        merge_taxonomy(DEFAULTS / "taxonomy.json", brain / "taxonomy.json")
        if "taxonomy.json" not in created and not (brain / "taxonomy.json").exists():
            created.append("taxonomy.json")
    if (DEFAULTS / "upstreams.json").exists():
        merge_upstreams(DEFAULTS / "upstreams.json", brain / "upstreams.json")

    # always ensure last_checked key exists
    up = brain / "upstreams.json"
    if up.exists():
        data = json.loads(up.read_text())
        data.setdefault("last_checked", None)
        up.write_text(json.dumps(data, indent=2) + "\n")

    if created:
        print(f"[apex-sentinel] brain bootstrapped at {brain}: {', '.join(created)}")
    else:
        print(f"[apex-sentinel] brain ok at {brain}")


if __name__ == "__main__":
    main()
