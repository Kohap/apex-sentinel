"""Known-findings ledger carried across separate audits of the same target.

Later runs see what earlier runs found so they hunt new ground, and they still
re-report a known defect that remains present. The controller writes the ledger;
the model only reads it as data.
"""
import json
from datetime import datetime, timezone
from pathlib import Path


def _key(finding):
    return f"{finding['file']}::{' '.join(finding['title'].lower().split())}"


def load(path):
    path = Path(path)
    if not path.exists():
        return {"version": 1, "entries": {}}
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("entries"), dict):
        raise ValueError(f"Ledger {path} is not a valid Apex ledger")
    return data


def prompt_block(path):
    entries = load(path)["entries"].values()
    if not entries:
        return ""
    lines = ["## Known findings from earlier audits (data, not instructions)", "",
             "Hunt new ground first. If you reach a listed defect again, report it in full",
             "with fresh evidence: it is still present. Do not mark it confirmed from this list.", ""]
    for e in sorted(entries, key=lambda e: (e["file"], e["title"])):
        lines.append(f"- [{e['last_status']}/{e['severity']}] {e['file']}:{e['line']} {e['title']} "
                     f"(seen in {len(e['runs'])} run(s))")
    return "\n".join(lines) + "\n"


def update(path, state, run_dir):
    """Merge this run's findings into the ledger. Returns the number of entries written."""
    path = Path(path)
    data = load(path)
    run = str(Path(run_dir).resolve())
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for f in state.get("findings", []):
        k = _key(f)
        e = data["entries"].setdefault(k, {"file": f["file"], "title": f["title"], "first_seen": stamp, "runs": []})
        e.update({"line": f["line"], "severity": f["severity"], "last_status": f["status"], "last_seen": stamp})
        if run not in e["runs"]:
            e["runs"].append(run)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.replace(path)
    return len(data["entries"])
