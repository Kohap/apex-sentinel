#!/usr/bin/env python3
"""Apex component handshake check.

Verifies that owning-component artifacts exist on disk. Chat claims do not count.

Usage:
  component_check.py [research-dir]
  component_check.py [research-dir] --strict   # FAIL on any missing owner
  component_check.py [research-dir] --phase P7

Exit 0 if the current bar is met, 1 if a required owner is missing.
Default (no --strict): FAIL only when a CONFIRMED/report finding exists without
P7 gauntlet, or when handshake rows are SKIP with no reason. WARN otherwise so
pre-1.3 hunts are not restarted.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"<fill|<title>|H-000|TEMPLATE|\bTBD\b|_e\.g\.", re.I)


def substance(p: Path, min_bytes: int = 60) -> bool:
    if not p.is_file():
        return False
    t = p.read_text(errors="replace")
    if len(t.strip()) < min_bytes:
        return False
    if PLACEHOLDER.search(t) and len(t) < 500:
        return False
    return True


def layer_of(scope: Path) -> str:
    if not scope.is_file():
        return "EVM"
    m = re.search(r"Research layer:\s*([A-Za-z]+)", scope.read_text(errors="replace"), re.I)
    return (m.group(1).upper() if m else "EVM")


def handshake_skips_without_reason(text: str) -> list[str]:
    bad = []
    for line in text.splitlines():
        if "|" not in line or line.strip().startswith("|---") or "Phase |" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6:
            continue
        status = cells[-1].upper()
        evidence = cells[-2]
        if status == "SKIP" and len(evidence) < 8:
            bad.append(f"handshake SKIP without reason: {cells[0]} {cells[1]}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("research", nargs="?", default="research")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--phase")
    args = ap.parse_args()
    r = Path(args.research).expanduser()
    layer = layer_of(r / "scope.md")
    warns: list[str] = []
    fails: list[str] = []

    def need(label: str, ok: bool, fatal: bool = False) -> None:
        if ok:
            return
        (fails if (args.strict or fatal) else warns).append(label)

    need("P0 kensho/ragnarok: scope.md", substance(r / "scope.md") or substance(r / "intake.md"))
    if layer != "APPLICATION":
        need(
            "P1 iykes: recon.md or auth-triage.md",
            substance(r / "recon.md") or substance(r / "auth-triage.md") or substance(r / "coverage.md"),
        )
        need("P1 ragnarok: architecture.md", substance(r / "architecture.md", 80))
    else:
        need(
            "P1 APPLICATION: coverage.md or architecture.md",
            substance(r / "coverage.md") or substance(r / "architecture.md") or substance(r / "scope.md"),
        )

    hypo = r / "hypotheses.md"
    hypo_txt = hypo.read_text(errors="replace") if hypo.is_file() else ""
    has_confirmed = bool(re.search(r"^H-\d+.*\bCONFIRMED\b", hypo_txt, re.M))
    if has_confirmed:
        need("P7 jailbreaker+iykes+kensho: fp-kill.md", substance(r / "fp-kill.md", 120), fatal=True)

    report = r / "report.md"
    report_txt = report.read_text(errors="replace") if report.is_file() else ""
    finding = bool(re.search(r"^##+\s*(Title|Summary|Root Cause)", report_txt, re.M | re.I))
    honest = bool(re.search(r"No confirmed finding meets the Ragnarok evidence standard", report_txt, re.I))
    if finding and not honest:
        need("P7 fp-kill.md required before a non-empty report", substance(r / "fp-kill.md", 120), fatal=True)
        need(
            "P5 experiments/ required before a non-empty report",
            (r / "experiments").is_dir() and any((r / "experiments").rglob("*")),
            fatal=True,
        )

    hs = r / "handshake.md"
    if not hs.is_file():
        warns.append(
            "handshake.md missing (pre-1.3 hunt?). Do not restart P0–P5; fill it on the next residual."
        )
    else:
        fails.extend(handshake_skips_without_reason(hs.read_text(errors="replace")))
        if args.strict and not substance(hs, 80):
            fails.append("handshake.md is still the blank template")

    phase = (args.phase or "").upper()
    if phase == "P7" and not substance(r / "fp-kill.md", 120):
        fails.append("P7 requested but fp-kill.md is empty — load jailbreaker + iykes + kensho and fill it")
    if phase == "P1" and layer != "APPLICATION" and not (
        substance(r / "auth-triage.md") or substance(r / "recon.md")
    ):
        fails.append("P1 requested but iykes recon/auth-triage artifacts missing")

    print("COMPONENT HANDSHAKE CHECK")
    print(f"research: {r}  layer: {layer}")
    if not warns and not fails:
        print("OK — owners have artifacts on disk.")
        return 0
    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")
    if fails:
        print("Action: run scripts/load_card.sh <phase>, load that file, produce the artifact.")
        print("A named component with no artifact is a hallucination.")
        return 1
    print("Action: warnings only. Continue residual; do not restart. Fill handshake.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
