# From skill to agent

The v1 skill described a workflow for a host model to interpret. The v2 CLI owns
the run lifecycle, repository snapshot, time limits, evidence capture, validation,
report generation, and resumption. Codex provides the model and local shell/file
tools. The agent decides which code paths and experiments to investigate.

## Review findings addressed

| Baseline issue | Agent behavior |
|---|---|
| Completed six-gate checklist rejected | Every structured gate is checked explicitly; all six PASS results with evidence can proceed |
| Fresh scaffold gets a completion-like PASS | Initial state is NOT_STARTED; completion requires actual command events, coverage, and a follow-up round |
| Prose and note files satisfy runtime evidence | Confirmation requires test source under artifacts/, the actual command event, exit zero, and distinct failure/control observations from its output |
| Saved status disagrees with combined result | One controller owns state.json and report.md |
| Financial bounty filter hides useful project defects | All confirmed severities appear; impact is specific to the defect, including data exposure and unauthorized actions |
| No guaranteed repair handoff | Confirmation requires reproduction steps, a precise repair, and a regression check |
| Inconsistent finding status labels | One JSON contract is shared by prompting, validation, state, and reporting |

The new evidence binding is stronger than a Markdown gate but not a semantic proof
system. A model can still design a poor test or misunderstand a trust boundary.
The follow-up round challenges those errors; review the test and its impact
interpretation before applying a repair.

## Legacy compatibility patches

Existing scripts receive narrow fixes: the six-gate inversion and blank-answer
handling; missing-input rejection; coverage/final-summary requirements for empty
closure; per-finding runtime/economic marker lookup; aggregate report-state writing;
CONFIRMED-REPORTABLE label recognition; and creation of the coverage template.

Legacy Markdown gates remain format checks. The v2 CLI replaces them for new audits;
it does not claim to retrofit captured execution into historical hunt folders.

## Existing users

- Existing hunt folders and ~/.apex-sentinel are not migrated or modified automatically.
- Start a new v2 audit using a local project path. Retain old artifacts as history.
- The original entrypoint is archived in references/legacy-v1-skill.md. SKILL.md now
  explains how to invoke the agent and interpret its results.
- Separate component skills remain available independently. The CLI uses its bundled
  methodology and does not claim those components were executed.
- Resume reuses the recorded snapshot. After changing project code, start a new audit
  so the source hashes and evidence describe the new revision.
