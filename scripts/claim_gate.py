#!/usr/bin/env python3
"""Apex claim gate — refuse CONFIRMED-for-report without the FP gauntlet on disk.

A finding may be CONFIRMED-REPORTABLE only when research/fp-kill.md has a real
section for that H-id that answers jailbreaker six gates, iykes 5, kensho 5.5,
brain FPs, ragnarok kill, permissionless YES, and a harness path.

Honest empty report.md with no CONFIRMED rows → PASS.
TRUST / SURVIVOR / FALSE POSITIVE in report.md → FAIL.

Usage: claim_gate.py [research-dir]
Exit 0 PASS, 1 FAIL.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TRUST_RE = re.compile(
    r"\b(onlyOwner|onlyowner|admin key|owner rug|1-step ownable|ownable eoa|"
    r"safe 3/|safe 2/|m-of-n|multisig threshold|eip-?7702 delegat|"
    r"platform owner|keeper-trusted|trust finding)\b",
    re.I,
)
H_HEAD = re.compile(r"^##+\s*(H-\d+)\b", re.I | re.M)
H_ROW = re.compile(r"^(H-\d+)\s*\|", re.M)
CONFIRMED = re.compile(r"\bCONFIRMED(?:-REPORTABLE)?\b", re.I)
PLACEHOLDER = re.compile(
    r"<title>|<fill|H-000|TEMPLATE|TBD|_e\.g\.", re.I
)

JAIL_GATES = ("Process", "Reachability", "Real Impact", "PoC Validation", "Math Bounds", "Environment")
IYKES_HINTS = ("Gas-feasible", "Access control", "production config", "Mitigating", "Temporary")
KENSHO_HINTS = ("Unprivileged", "upstream check", "centralization", "Duplicate", "Honest severity")


def read(p: Path) -> str:
    return p.read_text(errors="replace") if p.is_file() else ""


def nonempty(p: Path, min_bytes: int = 40) -> bool:
    if not p.is_file():
        return False
    text = p.read_text(errors="replace").strip()
    if len(text) < min_bytes:
        return False
    if PLACEHOLDER.search(text) and len(text) < 400:
        return False
    return True


def sections(fp: str) -> dict[str, str]:
    out: dict[str, str] = {}
    cur, buf = None, []
    for line in fp.splitlines():
        m = H_HEAD.match(line)
        if m:
            if cur:
                out[cur] = "\n".join(buf)
            cur = m.group(1).upper()
            buf = [line]
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf)
    return out


def has_all(text: str, needles: tuple[str, ...]) -> list[str]:
    missing = []
    low = text.lower()
    for n in needles:
        if n.lower() not in low:
            missing.append(n)
    return missing


def permissionless_yes(sec: str) -> bool | None:
    m = re.search(r"PERMISSIONLESS\s*:\s*([A-Za-z-]+)", sec, re.I)
    if not m:
        return None
    v = m.group(1).upper()
    if v in ("YES", "TRUE"):
        return True
    if v in ("NO", "FALSE", "TRUST"):
        return False
    return None


def verdict(sec: str) -> str:
    m = re.search(r"VERDICT\s*:\s*([A-Z][A-Z- ]+)", sec, re.I)
    return (m.group(1).strip().upper() if m else "")


def jail_all_pass(sec: str) -> bool:
    # Every gate name appears, and no FAIL on those rows if a table exists.
    if has_all(sec, JAIL_GATES):
        # fail if a gate row explicitly says FAIL
        for g in JAIL_GATES:
            if re.search(rf"{re.escape(g)}\s*\|\s*FAIL\b", sec, re.I):
                return False
        # require at least one PASS
        return bool(re.search(r"\|\s*PASS\b", sec, re.I))
    return False


def main() -> int:
    research = Path(sys.argv[1] if len(sys.argv) > 1 else "research").expanduser()
    reasons: list[str] = []
    report = research / "report.md"
    hypo = research / "hypotheses.md"
    fp = research / "fp-kill.md"
    killed = research / "killed.md"
    exps = research / "experiments"

    report_txt = read(report)
    hypo_txt = read(hypo)
    fp_txt = read(fp)
    honest = bool(re.search(
        r"No confirmed finding meets the Ragnarok evidence standard",
        report_txt, re.I,
    ))
    finding_sections = bool(re.search(
        r"^##+\s*(Title|Summary|Root Cause|Proof of Concept)",
        report_txt, re.M | re.I,
    ))
    if re.search(r"Status:\s*(SURVIVOR|INCONCLUSIVE|Potential)\b", report_txt, re.I):
        reasons.append("report.md: SURVIVOR / INCONCLUSIVE / Potential is not reportable")

    confirmed_ids = []
    for line in hypo_txt.splitlines():
        if "|" not in line:
            continue
        if re.match(r"^H-\d+", line) and re.search(r"\bCONFIRMED\b", line, re.I):
            confirmed_ids.append(line.split("|")[0].strip().upper())

    # Honest empty + no CONFIRMED rows: PASS (still warn if fp-kill never started)
    if honest and not finding_sections and not confirmed_ids:
        print("CLAIM GATE PASS — honest empty report, no CONFIRMED rows.")
        print("Nothing to claim. Do not fabricate a finding to fill the report.")
        return 0

    if finding_sections and not confirmed_ids:
        reasons.append("report.md has finding sections but hypotheses.md has no CONFIRMED row")

    if confirmed_ids and not nonempty(fp, 80):
        reasons.append("fp-kill.md missing/placeholder — jailbreaker/iykes/kensho gauntlet did not run")

    secmap = sections(fp_txt)
    for hid in confirmed_ids:
        if hid not in secmap or PLACEHOLDER.search(secmap[hid][:400] or ""):
            reasons.append(f"{hid}: no real fp-kill.md section (component P7 skipped)")
            continue
        sec = secmap[hid]
        miss_j = has_all(sec, JAIL_GATES)
        if miss_j:
            reasons.append(f"{hid}: jailbreaker gates missing: {', '.join(miss_j)}")
        elif not jail_all_pass(sec):
            reasons.append(f"{hid}: jailbreaker six gates are not all PASS")
        if has_all(sec, IYKES_HINTS):
            reasons.append(f"{hid}: iykes second-opinion incomplete")
        if has_all(sec, KENSHO_HINTS):
            reasons.append(f"{hid}: kensho §5.5 incomplete")
        if not re.search(r"FP patterns checked:", sec, re.I):
            reasons.append(f"{hid}: brain FP list not quoted")
        if not re.search(r"Mutation|kill mutations", sec, re.I):
            reasons.append(f"{hid}: no ragnarok kill mutation recorded")
        perm = permissionless_yes(sec)
        v = verdict(sec)
        if perm is None:
            reasons.append(f"{hid}: PERMISSIONLESS: YES/NO not stated")
        elif perm is False:
            reasons.append(f"{hid}: PERMISSIONLESS NO → TRUST, cannot be CONFIRMED-REPORTABLE")
        if TRUST_RE.search(sec) and perm is not True:
            reasons.append(f"{hid}: trust/admin language without PERMISSIONLESS YES")
        if v and "CONFIRMED-REPORTABLE" not in v and "CONFIRMED" in v:
            reasons.append(f"{hid}: verdict {v} is not CONFIRMED-REPORTABLE")
        if not re.search(r"RUNTIME_VERIFIED", hypo_txt):
            reasons.append(f"{hid}: hypotheses.md CONFIRMED row missing RUNTIME_VERIFIED")
        if not re.search(r"ECONOMICALLY_VERIFIED", hypo_txt):
            reasons.append(f"{hid}: hypotheses.md CONFIRMED row missing ECONOMICALLY_VERIFIED")

    if confirmed_ids:
        if not exps.is_dir() or not any(exps.rglob("*")):
            reasons.append("research/experiments/ empty — no RUNTIME evidence")
        if not nonempty(killed, 20) and "kill" not in fp_txt.lower():
            reasons.append("killed.md empty and fp-kill has no kill mutations")

    if honest and finding_sections:
        reasons.append("report.md mixes honest-empty sentence with finding sections")

    print("CLAIM GATE CHECK")
    print(f"research: {research}")
    print(f"CONFIRMED rows: {', '.join(confirmed_ids) or '(none)'}")
    if reasons:
        print("FAIL")
        for r in reasons:
            print(f"  - {r}")
        print("Action: demote the claim or finish fp-kill.md / harness. Do not disclose.")
        return 1
    print("PASS — gauntlet on disk, permissionless, harness present.")
    print("Action: proceed to report_gate.sh, then P10 only for Crit/High quantified loss.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
