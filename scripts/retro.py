#!/usr/bin/env python3
"""Apex Sentinel retro — capture lessons from an engagement into the Brain.

Usage:
  retro.py --finding --target P --class AS-001 [--name new-class] --text "..."
           [--evidence RUNTIME] [--severity High] [--product-type vault]
           [--chain base] [--tags a,b]
  retro.py --fp --pattern "<shape>" --why "<how it died>" [--source T]
  retro.py --register-target --target P --commit SHA --summary "one line"
           [--findings "AS-001:High,AS-013:killed"]
  retro.py --type heuristic|timing|method|intel --text "..." [--target P]

Every flag run appends one ledger entry and updates the relevant Brain file.
"""
import argparse, json, re, sys
from datetime import date
from pathlib import Path

BRAIN = Path.home() / ".apex-sentinel"
TYPES = ("finding", "fp", "heuristic", "timing", "method", "intel")
LEVELS = ("SOURCE", "DEPLOYMENT", "RUNTIME", "ECONOMIC")


def fail(msg):
    sys.exit(f"retro.py: {msg}")


def next_id(path, pattern):
    ids = [int(m.group(1)) for m in pattern.finditer(path.read_text())] if path.exists() else []
    return max(ids, default=0) + 1


def append_learning(ledger, lines):
    n = next_id(ledger, re.compile(r"^### L-(\d+) ", re.M))
    kind = lines.get("_kind", "")
    block = f"\n### L-{n} | {date.today().isoformat()} | {kind}\n"
    for k, v in lines.items():
        if not k.startswith("_"):
            block += f"{k}: {v}\n"
    with ledger.open("a") as f:
        f.write(block)
    # refresh index table (append after last existing row)
    text = ledger.read_text()
    one = lines.get("BODY", "").splitlines()[0][:80]
    idx_new = f"| L-{n} | {date.today().isoformat()} | {kind} | {lines.get('TARGET','-')} | {one} |\n"
    header_row = "| ID | Date | Type | Target | One-line |\n|----|------|------|--------|----------|\n"
    if "(no entries yet" in text:
        text = re.sub(r"\n\(no entries yet[^\n]*\n", "\n", text)
        text = text.replace(header_row, header_row + idx_new)
    elif header_row not in text:
        fail("LEARNINGS.md index header missing")
    else:
        ends = [m.end() for m in re.finditer(r"^\| L-\d+ [^\n]*\n", text, re.M)]
        pos = ends[-1] if ends else text.index(header_row) + len(header_row)
        text = text[:pos] + idx_new + text[pos:]
    ledger.write_text(text)
    print(f"[apex-sentinel] recorded L-{n} in {ledger}")


def bump_taxonomy(cls, name=None):
    tf = BRAIN / "taxonomy.json"
    data = json.loads(tf.read_text())
    if cls == "new":
        if not name:
            fail("--class new requires --name")
        nid = f"AS-{max(int(c['id'].split('-')[1]) for c in data['classes'])+1:03d}"
        data["classes"].append({"id": nid, "name": name, "aliases": [], "product_types": [],
                                "refs": ["learned"], "hits": 1})
        cls = nid
        print(f"[apex-sentinel] new class {nid}: {name}")
    else:
        hit = False
        for c in data["classes"]:
            if c["id"] == cls:
                c["hits"] = c.get("hits", 0) + 1
                hit = True
                break
        if not hit:
            fail(f"class {cls} not in taxonomy (use --class new --name X)")
    data["_meta"]["last_updated"] = date.today().isoformat()
    tf.write_text(json.dumps(data, indent=2))
    return cls


def do_fp(args):
    fpf = BRAIN / "false-positives.md"
    n = next_id(fpf.parent / "LEARNINGS.md", re.compile(r"^### L-(\d+) ", re.M))
    row = f"| {args.pattern} | {args.why} | {date.today().isoformat()} | {args.source or '-'} |\n"
    text = fpf.read_text()
    if "(none yet)" in text:
        text = text.replace("| (none yet) | | | |\n", "")
    fpf.write_text(text.rstrip("\n") + "\n" + row)
    append_learning(fpf.parent / "LEARNINGS.md",
                    {"_kind": "fp", "TARGET": args.source or "-",
                     "CLASS": "-", "PRODUCT": "-",
                     "EVIDENCE": "-", "BODY": f"FP pattern: {args.pattern}\nDied because: {args.why}",
                     "TAGS": "false-positive"})


def do_target(args):
    tj = BRAIN / "targets.json"
    data = json.loads(tj.read_text())
    key = args.target.lower().replace(" ", "-")
    prev = data["targets"].get(key, {"engagements": []})
    prev["engagements"] = prev.get("engagements", []) + [
        {"date": date.today().isoformat(), "commit": args.commit,
         "summary": args.summary, "findings": args.findings or ""}]
    prev["last"] = date.today().isoformat()
    data["targets"][key] = prev
    tj.write_text(json.dumps(data, indent=2))
    append_learning(BRAIN / "LEARNINGS.md",
                    {"_kind": "engagement", "TARGET": args.target,
                     "CLASS": "-", "PRODUCT": "-", "EVIDENCE": "-",
                     "BODY": f"Engagement closed @ {args.commit}. {args.summary}"
                             + (f" Findings: {args.findings}" if args.findings else ""),
                     "TAGS": "engagement"})
    print(f"[apex-sentinel] registered target {key} ({len(prev['engagements'])} engagements)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--finding", action="store_true")
    p.add_argument("--fp", action="store_true")
    p.add_argument("--register-target", action="store_true")
    p.add_argument("--type", choices=TYPES)
    p.add_argument("--target"); p.add_argument("--class", dest="cls"); p.add_argument("--name")
    p.add_argument("--text"); p.add_argument("--evidence", choices=LEVELS)
    p.add_argument("--severity"); p.add_argument("--product-type"); p.add_argument("--chain")
    p.add_argument("--tags"); p.add_argument("--pattern"); p.add_argument("--why")
    p.add_argument("--source"); p.add_argument("--commit"); p.add_argument("--summary")
    p.add_argument("--findings")
    a = p.parse_args()

    BRAIN.mkdir(exist_ok=True)
    init = Path(__file__).resolve().parent / "init_brain.py"
    if init.exists():
        import subprocess
        subprocess.run([sys.executable, str(init), "--brain", str(BRAIN)], check=False)
    if a.fp:
        if not (a.pattern and a.why):
            fail("--fp needs --pattern and --why")
        return do_fp(a)
    if a.register_target:
        if not (a.target and a.commit):
            fail("--register-target needs --target and --commit")
        return do_target(a)
    if not a.text:
        fail("provide --text (or --fp/--register-target)")
    kind = a.type or ("finding" if a.finding else None)
    if not kind:
        fail("specify --finding or --type")
    cls = "-"
    if kind == "finding":
        if not a.cls:
            fail("findings need --class AS-XXX or 'new'")
        cls = bump_taxonomy(a.cls, a.name)
    body = a.text if "\n" in a.text else a.text
    append_learning(BRAIN / "LEARNINGS.md",
                    {"_kind": kind, "TARGET": a.target or "general",
                     "CLASS": cls, "PRODUCT": a.product_type or "-",
                     "EVIDENCE": a.evidence or "SOURCE",
                     "BODY": body + (f" [severity {a.severity}]" if a.severity else ""),
                     "TAGS": ",".join(filter(None, [a.tags, a.chain])) or "-"})


if __name__ == "__main__":
    main()
