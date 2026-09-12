#!/usr/bin/env python3
"""Apex Sentinel brief — inject the Brain into a new engagement (Phase P0).

Usage:
  brief.py --product-type vault [--chain base] [--keywords "oracle,4626"]
           [--target somedao] [--layer EVM|APPLICATION] [--brain ~/.apex-sentinel]

Prints: freshness status, intent routing, ranked taxonomy classes for the
product type, matching false-positive patterns, target history, and recent
lessons. Bootstraps the brain if missing.
"""
import argparse, json, re, subprocess, sys
from datetime import date, datetime
from pathlib import Path

STALE_DAYS = 14
HERE = Path(__file__).resolve().parent


def load(p, default):
    p = Path(p).expanduser()
    if not p.exists():
        return default
    if p.suffix == ".json":
        return json.loads(p.read_text())
    return p.read_text()


def days_since(iso):
    if not iso:
        return None
    try:
        d = datetime.fromisoformat(iso[:10]).date()
        return (date.today() - d).days
    except ValueError:
        return None


def bootstrap(brain: Path) -> None:
    init = HERE / "init_brain.py"
    if init.exists():
        subprocess.run([sys.executable, str(init), "--brain", str(brain)], check=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product-type", dest="ptype")
    ap.add_argument("--chain")
    ap.add_argument("--keywords", help="comma separated")
    ap.add_argument("--target")
    ap.add_argument("--layer", choices=("EVM", "APPLICATION", "SOLANA"), default="EVM")
    ap.add_argument("--brain", default="~/.apex-sentinel")
    a = ap.parse_args()
    brain = Path(a.brain).expanduser()
    bootstrap(brain)

    print(f"# APEX SENTINEL BRIEF — {date.today().isoformat()} (v1.2.0)")
    print(f"\nLayer: {a.layer}. Ragnarok: v4 (SYNTHESIS OPEN after thin map).")
    print("Intent: 'investigate X' / 'keep hunting' after OPEN = residual P8, not a new P0.")
    print("'audit skill' = Apex Sentinel, not the bug-ai-auditor stub.")
    if a.layer == "APPLICATION":
        print("APPLICATION: skip EVM reconstruction gate. Hunt compose → policy → simulate → execute.")
        print("Check AS-022..AS-028, AS-030 first (kill switch, cooldown, 0x0 receiver, wrong dry-run).")

    # 1. freshness
    up = load(brain / "upstreams.json", {})
    age = days_since(up.get("last_checked"))
    if age is None:
        print("\n## ⚠ FRESHNESS: upstreams never checked — run scripts/update_check.sh before hunting")
    elif age > STALE_DAYS:
        print(f"\n## ⚠ FRESHNESS: last checked {age}d ago (> {STALE_DAYS}) — run scripts/update_check.sh")
    else:
        print(f"\n## Freshness: OK ({age}d since last check)")

    # 2. taxonomy ranking
    tax = load(brain / "taxonomy.json", {"classes": []})
    kws = [k.strip().lower() for k in (a.keywords or "").split(",") if k.strip()]
    scored = []
    for c in tax.get("classes", []):
        if c.get("retired"):
            continue
        s = 0
        pts = c.get("product_types", [])
        if a.ptype and (a.ptype in pts or "any" in pts):
            s += 10
        if a.layer == "APPLICATION" and any(x in pts for x in ("policy", "mcp", "agent")):
            s += 12
        hay = " ".join([c["name"], *c.get("aliases", [])]).lower()
        s += 3 * sum(1 for k in kws if k in hay)
        s += min(c.get("hits", 0), 5)
        scored.append((s, c))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    top = [c for s, c in scored if s > 0][:10] or [c for _, c in scored[:8]]
    print(f"\n## Priority classes{' for ' + a.ptype if a.ptype else ''} (check these first)")
    for c in top:
        hits = f" · {c['hits']} field hit(s)" if c.get("hits") else ""
        kill = " · MUST KILL temporary-vs-persistent first" if c.get("kills_required") else ""
        trust = " · usually trust-finding not permissionless" if c.get("trust_finding_default") else ""
        print(f"- **{c['id']} {c['name']}**{hits}{kill}{trust} — refs: {', '.join(c.get('refs', []))}")

    # 3. false positives
    fps = load(brain / "false-positives.md", "")
    rows = [r for r in fps.splitlines()
            if r.startswith("| ") and not r.startswith("| (none")
            and "Pattern" not in r and "---" not in r]
    print(f"\n## Known false-positive patterns ({len(rows)}) — verify your lead isn't one of these")
    for r in rows[:12]:
        cells = [c.strip() for c in r.strip("|").split("|")]
        if len(cells) >= 3:
            print(f"- {cells[0]} → died because: {cells[1]} ({cells[2]})")

    # 4. target history
    tj = load(brain / "targets.json", {"targets": {}})
    key = (a.target or "").lower().replace(" ", "-")
    if key and key in tj.get("targets", {}):
        t = tj["targets"][key]
        print(f"\n## Prior engagements on '{a.target}' ({len(t['engagements'])})")
        for e in t["engagements"][-3:]:
            print(f"- {e['date']} @ {e.get('commit','?')}: {e.get('summary','')}"
                  + (f" findings={e['findings']}" if e.get("findings") else ""))
        print("→ Re-check what changed since last commit; do not re-run killed hypotheses blindly.")
        print("→ If NOW.md already says OPEN/residual, do NOT restart P0–P5.")

    # 5. recent lessons
    led = load(brain / "LEARNINGS.md", "")
    blocks, cur = [], None
    for line in led.splitlines():
        if line.startswith("### L-"):
            if cur:
                blocks.append(cur)
            cur = [line]
        elif cur is not None and ": " in line and re.match(r"^[A-Z_]+: ", line):
            cur.append(line)
    if cur:
        blocks.append(cur)
    blocks = [b for b in blocks if "<NNN>" not in b[0]]
    if blocks:
        print(f"\n## Recent lessons ({min(len(blocks), 8)} of {len(blocks)})")
        for b in blocks[-8:]:
            lid = b[0].split(" ", 1)[1].split(" |")[0]
            body = next((l for l in b if l.startswith("BODY:")), "")
            print(f"- {lid}: {body[6:120]}")

    if not a.ptype:
        print("\n(tip: pass --product-type for sharper class ranking)")


if __name__ == "__main__":
    main()
