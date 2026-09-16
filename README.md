# Apex Sentinel

**A local repository audit agent that turns suspected defects into reproducible findings and repair instructions.**

Apex v2 controls an audit run: it copies a repository, investigates its code with
Grok or Codex, creates and runs local tests, challenges its findings in a follow-up round,
and writes a structured report. It preserves progress so a bounded or interrupted
run can continue later.

The original Web3 skill is preserved as methodology and legacy tooling. The v2
agent supports application and contract source reviews without requiring a bounty,
permissionless financial loss, or separately installed component skills.

## Quick start

Requirements: macOS or Linux, Python 3.10+, Git, and either a Grok CLI login
(`@xai-official/grok`, `XAI_API_KEY` or `grok login`) or a Codex CLI login.
Model runs consume the usage available to that account.

```sh
git clone https://github.com/Kohap/apex-sentinel.git
cd apex-sentinel
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
# Grok (preferred when authenticated) or Codex
apex doctor
apex audit /path/to/your-project --output /path/to/new-audit
# force a backend:
apex audit /path/to/your-project --runtime grok --output /path/to/new-audit
apex audit /path/to/your-project --runtime codex --output /path/to/new-audit
```

The output must be a **new directory outside the project**. If omitted, Apex
creates a timestamped sibling directory. Without installation, run the same
commands as `python3 -m apex_agent` from this checkout.

```sh
apex audit /path/to/project --focus "Tenant isolation and private file downloads"
apex audit /path/to/project --max-rounds 4 --timeout 300 --budget 1200
apex resume /path/to/audit --max-rounds 2 --budget 600
apex status /path/to/audit
apex report /path/to/audit
```

`--runtime auto` (default) uses Grok CLI when it is installed and authenticated,
otherwise Codex. `--runtime grok` / `--runtime codex` force one backend.
`--model MODEL` selects a model on a new audit; otherwise Apex uses that CLI's
default. `--grok` / `--codex` select the executable. Resume retains the original
model, snapshot, and scope. Time budgets and round counts apply to each invocation;
they are not token or spending caps.

## How the agent works

1. **Snapshot:** copy eligible source files, including current uncommitted and
   untracked files, and record their hashes. The original project is not the agent's
   working directory.
2. **Explore:** inspect entry points and trust boundaries, choose local experiments,
   execute actual project code, and record candidates and coverage.
3. **Verify:** revisit candidates, attempt falsification, and rerun reproductions
   with a legitimate-use control. First-round claims cannot self-confirm.
4. **Validate:** require matching source citations, six answered gates, repair and
   regression instructions, a test artifact, and observations found in successful
   command events from the current round.
5. **Report or continue:** preserve all findings and limitations. Stop on scoped
   completion, a blocker, interruption, or the configured budget.

These are sequential rounds of one agent workflow, not a parallel agent swarm.
The controller stores logs and state outside the agent's writable workspace.
It invokes Grok (`grok --prompt-file`, structured JSON, session command capture)
or the supported [Codex non-interactive interface](https://learn.chatgpt.com/docs/non-interactive-mode)
with structured output and command-event capture.

## Deliverables

```text
audit/
  report.md              Findings, repairs, coverage, and blockers
  findings.json          Structured findings and evidence bindings
  state.json             Snapshot manifest, status, progress, and exclusions
  rounds/001/
    prompt.txt           Exact round instructions
    events.jsonl         Raw runtime event stream
    stderr.log           Runtime diagnostics
    response.json        Model's proposed structured result
    commands.json        Captured completed command executions
  workspace/
    source/              Project snapshot
    artifacts/           Reproduction tests and scratch files
```

A confirmed finding includes the affected source line, preconditions, expected and
observed behavior, impact bounds, runnable reproduction, control case, falsification
attempt, specific repair, and regression check. Every confirmed severity appears in
the report. Proposed fixes are instructions; v2 does not automatically modify the
original repository, create pull requests, disclose findings, or deploy changes.

## Status and exit codes

| Status | Meaning |
|---|---|
| NOT_STARTED | Snapshot exists; no audit work has completed |
| RUNNING | Investigation is active |
| COMPLETE_SCOPED | Scoped review and follow-up verification finished without recorded blockers or unresolved leads |
| PARTIAL | More verification or coverage remains when the round/time budget ends |
| BLOCKED | Runtime, evidence validation, dependency, or snapshot problem stopped the run |
| INTERRUPTED | The user stopped the run; saved evidence can be resumed |

`audit` and `resume` return 0 for COMPLETE_SCOPED, 2 for incomplete/blocked results,
and 1 for setup errors. Exit 0 does **not** mean no vulnerabilities were found;
inspect findings.json. `status`, `report`, and `doctor` return 0 when their command
succeeds. A completed review with zero findings still needs recorded coverage and
a follow-up round.

## Boundaries and current limitations

- Codex runs use a workspace-write sandbox and disable shell network access.
  Grok defaults to `--sandbox off` (no bubblewrap). Pass `--sandbox workspace`
  or `strict` when `bwrap` is installed. Global skill descriptions may still be
  supplied by the selected CLI; the audit prompt does not invoke those skills.
- Reproductions use installed local tools and synthetic data. Missing dependencies,
  unavailable contract forks, or services produce blockers. There is no automatic
  dependency installation, live exploitation, or production access.
- Git-ignored files, common dependency/build directories, symlinks, common credential
  filenames, and files over 2 MB are excluded. Snapshot limits are 20,000 files and
  100 MB. Inclusion hashes and explicit exclusions are recorded; ignored directory
  contents are not exhaustively enumerated. Excluded code is not covered.
- Sandboxing is supplied by the selected CLI, not a VM created by Apex. Some
  already-sandboxed hosts cannot initialize a second sandbox; Apex records this
  as BLOCKED.
- Evidence validation checks recorded execution and required fields. It cannot
  mathematically prove exploit semantics, prevent every model error, or certify
  whole-project security. Findings still merit human review. Hashes support
  traceability; they are not tamper-proof attestations.
- This first version audits source snapshots. It does not include browser-based
  frontend testing, automatic environment provisioning, or automatic patching.

## Local evaluation

```sh
python3 -m unittest discover -s tests -v
apex audit examples/invoice-demo --output /tmp/apex-invoice-evaluation
```

The invoice example contains fictional data and an intentionally imperfect access
check. Automated tests exercise the controller with deterministic runtime fixtures;
they do not claim to benchmark model detection quality. See [validation](docs/VALIDATION.md)
for the actual live-run outcome and test coverage.

## Review and migration

- [Original v1.3.1 review](docs/reviews/2026-09-16-v1-review.md)
- [Original reproduction results](docs/reviews/apex-review-checks.json)
- [What changed in v2](docs/MIGRATION.md)
- [Archived v1 skill](references/legacy-v1-skill.md)

Legacy scripts remain available for existing hunt folders. The new runtime does
not use their Markdown gates or write to the global v1 Brain.

Copyright (c) 2026 Gift. All rights reserved. Existing [license](LICENSE) retained.
