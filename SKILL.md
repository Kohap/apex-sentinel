---
name: apex-sentinel
description: Run the Apex Sentinel local repository audit agent, inspect its evidence-backed findings, or resume an incomplete audit. Use for authorized repository security reviews and actionable repair reports.
metadata:
  version: 2.0.0
  author: Gift (https://github.com/Kohap)
---

# Apex Sentinel agent

Apex is now a local command-line agent. Its maintained runtime is `apex_agent/`.
It performs a bounded investigation, runs local reproductions, revisits findings,
and produces a controller-validated report with repair instructions.

## Run

From this repository, check `python3 -m apex_agent doctor`, then:

```sh
python3 -m apex_agent audit /absolute/path/to/project --output /absolute/path/to/new-audit
```

The output directory must be outside the project. With the package installed,
use `apex audit`, `apex resume`, `apex status`, and `apex report`.
See README.md for installation, limits, and examples.

Use the user's requested scope through `--focus`. Use their requested model through
`--model`; otherwise keep the runtime default. Respect the run's configured time
and round limits. Audit output is not permission to disclose or deploy changes.

## Interpret results

Read `report.md` and `state.json`. `COMPLETE_SCOPED` means the recorded scope was
reviewed and verification completed; it does not certify the whole project.
`PARTIAL`, `BLOCKED`, and `INTERRUPTED` require the stated next action or a resume.
An empty report is never sufficient evidence of a completed audit.

Confirmed findings include a source location, actual captured command output,
a failure case, a legitimate-use control, a repair, and a regression check.
Unverified leads remain separate. Do not strengthen claims beyond those artifacts.

## Legacy methodology

The v1 orchestration document is archived at references/legacy-v1-skill.md.
The component playbooks informed the new methodology; they are not automatically
executed or falsely claimed as completed by the CLI. Legacy scripts are retained
for old hunt folders, but their Markdown checks are not the v2 evidence validator.
