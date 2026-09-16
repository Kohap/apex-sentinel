import argparse
from datetime import datetime
from pathlib import Path
import sys

from . import __version__
from .engine import create_run, run_agent, lock
from .report import save_report
from .runtime import CodexRuntime, GrokRuntime, doctor, doctor_auto, doctor_grok
from .storage import load_json


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def parser():
    ap = argparse.ArgumentParser(prog="apex", description="Apex Sentinel: local repository audit agent")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="command", required=True)
    check = sub.add_parser("doctor", help="Check Grok/Codex CLI compatibility and login")
    check.add_argument("--codex", default="codex", help="Path to Codex executable")
    check.add_argument("--grok", default="grok", help="Path to Grok executable")
    check.add_argument("--runtime", choices=("auto", "grok", "codex"), default="auto",
                       help="Which CLI to verify (default: auto, prefer Grok)")
    audit = sub.add_parser("audit", help="Audit a copy of a local repository")
    audit.add_argument("repository", type=Path)
    audit.add_argument("--output", type=Path, help="New directory outside the audited repository")
    audit.add_argument("--focus", default="Review reachable security defects in this repository; state coverage limits.")
    audit.add_argument("--model", help="Optional model id; otherwise use the CLI default")
    resume = sub.add_parser("resume", help="Continue a partial or interrupted audit from saved evidence")
    resume.add_argument("run", type=Path)
    for command in (audit, resume):
        command.add_argument("--max-rounds", type=positive, default=3, help="Additional rounds for this invocation (default: 3)")
        command.add_argument("--timeout", type=positive, default=300, help="Maximum seconds per round")
        command.add_argument("--budget", type=positive, default=900, help="Maximum total seconds for this invocation")
        command.add_argument("--codex", default="codex", help="Path to Codex executable")
        command.add_argument("--grok", default="grok", help="Path to Grok executable")
        command.add_argument("--runtime", choices=("auto", "grok", "codex"), default="auto",
                             help="Audit backend (default: auto, prefer Grok when authenticated)")
        command.add_argument("--sandbox", default="off",
                             help="Grok sandbox profile: off (default; use when bubblewrap is missing), workspace, read-only, strict (ignored for Codex)")
    for name in ("status", "report"):
        command = sub.add_parser(name, help="Read saved audit status" if name == "status" else "Regenerate report from saved controller state")
        command.add_argument("run", type=Path)
    return ap


def make_runtime(args):
    runtime = getattr(args, "runtime", "auto")
    if runtime == "grok":
        binary = doctor_grok(args.grok)
        return GrokRuntime(binary, sandbox=getattr(args, "sandbox", "off"))
    if runtime == "codex":
        return CodexRuntime(doctor(args.codex))
    name, binary = doctor_auto(args.grok, args.codex)
    if name == "grok":
        return GrokRuntime(binary, sandbox=getattr(args, "sandbox", "off"))
    return CodexRuntime(binary)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "doctor":
            if args.runtime == "codex":
                binary = doctor(args.codex)
                print(f"Ready: {binary}\nRuntime: codex\nAuthentication is available.")
                return 0
            if args.runtime == "grok":
                binary = doctor_grok(args.grok)
                print(f"Ready: {binary}\nRuntime: grok\nAuthentication is available (XAI_API_KEY or grok login).")
                return 0
            name, binary = doctor_auto(args.grok, args.codex)
            print(f"Ready: {binary}\nRuntime: {name}\nAuthentication is available. Audit runs use this CLI by default.")
            return 0
        if args.command in {"status", "report"}:
            if args.command == "report":
                with lock(args.run):
                    state = load_json(args.run / "state.json")
                    save_report(args.run, state)
            else:
                state = load_json(args.run / "state.json")
            print(f"{state['status']}: {state.get('summary') or 'No completed audit round'}")
            print(f"Report: {(args.run / 'report.md').resolve()}")
            return 0
        runtime = make_runtime(args)
        if args.command == "audit":
            target = args.repository.resolve()
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            run_dir = args.output or target.parent / f"{target.name}-apex-{stamp}"
            create_run(target, run_dir, args.focus, args.model)
        else:
            run_dir = args.run
        result = run_agent(run_dir, runtime, args.max_rounds, args.timeout, args.budget)
        print(f"\n{result['status']} — {sum(f['status'] == 'confirmed' for f in result['findings'])} confirmed finding(s)")
        print(f"Runtime: {runtime.name}")
        print(f"Report: {(Path(run_dir) / 'report.md').resolve()}")
        if result.get("error"):
            print(result["error"])
        return 0 if result["status"] == "COMPLETE_SCOPED" else 2
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"apex: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
