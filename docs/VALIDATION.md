# Validation record

## Automated checks

Run `python3 -m unittest discover -s tests -v`.

Local result on 16 September 2026: **32 tests passed**. A clean virtual-environment
package installation, console entrypoint, bundled methodology, and skill metadata
were also checked. GitHub Actions runs the suite on macOS and Linux with Python
3.10 and 3.12; consult the workflow result for remote status.

The tests cover complete/incomplete six-gate results, missing evidence, wrong source
locations, unrelated command output, proof-note rejection, missing repair/control
details, path traversal and symlinks, current/untracked snapshots, original-source
preservation, source mutation rejection, two-round confirmation, partial/resumed
runs, interruption, timeouts, missing coverage, blockers, finding retention,
command-event parsing, and the legacy validator regressions.

Controller tests use a deterministic fake runtime. They verify orchestration,
not real model detection performance. Process-adapter tests exercise a fixture
executable without making model calls.

## Live Codex smoke test: 16 September 2026

Target: the bundled synthetic invoice example. Intended run: exploration followed
by verification, two rounds maximum, local Python only.

The installed Codex CLI was detected and authentication was available. The first
attempt was blocked by the host's read-only Codex session database. After the host
granted the required database access, Codex started and returned structured output.
Its shell tools failed to initialize under the enclosing macOS sandbox:

```text
sandbox-exec: sandbox_apply: Operation not permitted
```

The response explicitly reported the blocker and zero findings. Apex rejected
completion because there were no executed command events. No unsafe fallback or
sandbox bypass was added. This verifies blocked-run handling; it does not establish
a successful end-to-end model-driven audit. Run the documented invoice evaluation
from a normal terminal to complete that environment-dependent check.

Raw live transcripts are not committed because they contain machine-specific
runtime context. Historical v1 gate reproductions are included under docs/reviews/
and were captured before the compatibility fixes.
