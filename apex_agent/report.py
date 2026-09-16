"""Render reports from controller state, never from a model's completion claim."""

from pathlib import Path

from .storage import write_json


def render(state):
    lines = ["# Apex Sentinel audit", "", f"**Status: {state['status']}**", "",
             f"Repository: `{state['repository']}`", f"Snapshot: `{state['snapshot']['content_sha256']}`",
             f"Commit: `{state['snapshot'].get('commit') or 'not a Git checkout'}`", "",
             f"Scope: {state['focus']}", "", state.get("summary") or "No audit round has completed.", "",
             "This is a scoped review of the copied files, not a certification that the project is secure.", ""]
    if state.get("error"):
        lines += ["## Run limitation", "", state["error"], ""]
    confirmed = [f for f in state["findings"] if f["status"] == "confirmed"]
    lines += ["## Confirmed findings", ""]
    if not confirmed:
        lines += ["No finding has passed runtime evidence and follow-up verification.", ""]
    for f in confirmed:
        lines += [f"### {f['id']}: {f['title']} ({f['severity']})", "",
                  f"**Location:** `source/{f['file']}:{f['line']}`", "",
                  f"**Preconditions:** {f['preconditions']}", "",
                  f"**Expected:** {f['expected']}", "", f"**Observed:** {f['actual']}", "",
                  f"**Impact and limits:** {f['impact']}", "", "**Reproduction:**", ""]
        lines += [f"{i}. {s}" for i, s in enumerate(f["reproduction_steps"], 1)]
        proof = f["proof"]
        lines += ["", f"Test: `workspace/{proof['artifact']}`", "", "```sh", proof["command"], "```", "",
                  f"Failure observation: {proof['observation']}", "",
                  f"Legitimate-use control: {proof['control_observation']}", "",
                  f"**Falsification attempt:** {f['falsification']}", "",
                  f"**Repair:** {f['fix']}", "", f"**Regression check:** {f['regression_test']}", "",
                  f"Captured evidence: `rounds/{f['round']:03d}/commands.json`, command `{f['evidence_binding']['command_id']}`.", ""]
    lines += ["## Unverified leads and dismissed claims", ""]
    others = [f for f in state["findings"] if f["status"] != "confirmed"]
    if not others:
        lines += ["None recorded.", ""]
    for f in others:
        lines += [f"- **{f['id']} — {f['status']}: {f['title']}**",
                  f"  {f['falsification'] if f['status'] == 'dismissed' else f['next_action']}"]
    lines += ["", "## Coverage", ""]
    for c in state["coverage"]:
        lines += [f"- **{c['status']} — {c['surface']}** (`{c['file']}`): {c['details']}"]
    if not state["coverage"]:
        lines += ["No coverage has been established."]
    lines += ["", "## Blockers and next steps", ""]
    lines += [f"- {s}" for s in state["blockers"] + state["next_steps"]] or ["None recorded."]
    excluded = state["snapshot"]["excluded"]
    lines += ["", "## Snapshot limits", "",
              f"Copied {len(state['snapshot']['files'])} files; explicitly excluded {len(excluded)} entries.",
              "Git-ignored files, dependency/build directories, symlinks, common credential filenames, and files over 2 MB are not audited.",
              "The complete included-file manifest and explicit exclusions are in state.json.", ""]
    return "\n".join(lines)


def save_report(run_dir, state):
    run_dir = Path(run_dir)
    write_json(run_dir / "state.json", state)
    write_json(run_dir / "findings.json", state["findings"])
    (run_dir / "report.md").write_text(render(state))
