#!/usr/bin/env bash
# Print the one-phase load card. Artifact-or-it-didn't-happen.
# Usage: load_card.sh [P0|P1|...|P10|PR|P7]
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOLVE="$HERE/resolve_skill.sh"
PHASE="$(echo "${1:-}" | tr '[:lower:]' '[:upper:]')"
PHASE="${PHASE#PHASE}"
[ -n "$PHASE" ] || { echo "usage: load_card.sh P0|P1|P2|P3|P4|P5|P6|P7|P8|P9|P10|PR" >&2; exit 2; }

skill() {
  local n="$1"
  if [ -x "$RESOLVE" ]; then
    bash "$RESOLVE" "$n" 2>/dev/null || echo "<$n not installed>"
  else
    echo "<resolve_skill.sh missing>"
  fi
}

KENSHO="$(skill kensho)"
RAG="$(skill ragnarok)"
IYKES="$(skill iykes-web3-bughunt-skill)"
JAIL="$(skill jailbreaker)"
[ "$JAIL" = "<jailbreaker not installed>" ] && JAIL="$(skill viktor-blackhat)"
APEX="$(cd "$HERE/.." && pwd)"
BRAIN="${APEX_BRAIN:-$HOME/.apex-sentinel}"

header() {
  echo "APEX LOAD CARD — $1"
  echo "Load ONLY these files. Produce the artifact. Tick research/handshake.md."
  echo "Do not improvise the methodology from memory."
  echo
}

case "$PHASE" in
  P0)
    header "P0 Authorize · Scope · Brief"
    echo "Load:"
    echo "  $KENSHO/SKILL.md          # Part 3 intake + audit-status only"
    echo "  $RAG/references/phases/00-scope.md"
    echo "  $RAG/references/bounty.md  # if this is a bounty"
    echo "Run:"
    echo "  python3 $APEX/scripts/init_brain.py"
    echo "  python3 $APEX/scripts/brief.py --product-type <T> --target <N> --layer EVM|APPLICATION"
    echo "Produce: research/intake.md  research/scope.md (incl. Research layer)"
    echo "Do not: invent chain-id, inbox, or authorization."
    ;;
  P1)
    header "P1 Ground truth · thin map"
    echo "Load:"
    echo "  $RAG/references/phases/01-map.md"
    echo "Run (do not rewrite):"
    echo "  $IYKES/tools/step1_ground_truth.sh"
    echo "  $IYKES/tools/step2_creator_trace.sh  $IYKES/tools/step2_bundle_grep.sh"
    echo "  $IYKES/tools/step3_surface_map.sh"
    echo "  $IYKES/tools/step4_auth_triage.sh     # from 0xdead"
    echo "Produce: research/recon.md  research/auth-triage.md  research/coverage.md"
    echo "         research/architecture.md (graph + ONE trace)"
    echo "Do not: dive a lead. APPLICATION: skip step1-4; still start coverage.md."
    ;;
  P2)
    header "P2 Deployment"
    echo "Load: $RAG/references/phases/02-deployment.md"
    echo "      $RAG/references/adapters/evm.md   # if EVM"
    echo "Produce: research/deployment.md"
    echo "Do not: treat address match as a behavior check."
    ;;
  P3)
    header "P3 Invariants · assumptions"
    echo "Load: $RAG/references/phases/03-invariants.md"
    echo "      $RAG/references/phases/04-assumptions.md"
    echo "Produce: research/invariants.md  research/assumptions.md (provenance)"
    echo "Do not: empty files without an explicit N/A rationale."
    ;;
  P4)
    header "P4 Invent states · rank"
    echo "Load: $RAG/references/phases/05-synthesis.md"
    echo "      $RAG/references/seams.md"
    echo "      $RAG/references/phases/05-hypotheses.md"
    echo "Produce: research/contradictions.md  research/representations.md  research/hypotheses.md"
    echo "Do not: start from a SWC / bug-class checklist."
    ;;
  P5)
    header "P5 Experiment-first"
    echo "Load: $RAG/references/phases/06-experiments.md"
    echo "      $RAG/references/kill.md"
    echo "Run:  $APEX/scripts/probe_evm.sh   $APEX/scripts/harness_init.sh"
    echo "      $IYKES/tools/step7_poc_scaffold.sh"
    echo "Produce: research/experiments/<file>  killed.md rows"
    echo "Do not: mark RUNTIME_VERIFIED without a run."
    ;;
  P6)
    header "P6 Economic"
    echo "Load: $RAG/references/phases/10-economic.md"
    echo "Produce: attacker/protocol delta, capital, gas, repeatability on the H-row"
    echo "Do not: assign severity before this."
    ;;
  P7)
    header "P7 Falsification — ALL THREE OWNERS"
    echo "Load:"
    echo "  $JAIL/references/verification-and-reporting.md   # §1 six gates"
    echo "  $IYKES/SKILL.md                                  # Second-opinion gate (5 questions)"
    echo "  $KENSHO/SKILL.md                                 # §5.5 quality gate"
    echo "  $RAG/references/kill.md"
    echo "  $BRAIN/false-positives.md"
    echo "  $APEX/references/anti-hallucination.md"
    echo "Produce: research/fp-kill.md  (one section per live H-###; copy scripts/defaults/fp-kill.md)"
    echo "Do not: CONFIRMED, report.md, or 'I used jailbreaker internally'."
    ;;
  P8)
    header "P8 Expansion · novelty · residual"
    echo "Load: $RAG/references/phases/13-novelty.md"
    echo "      $RAG/references/phases/14-residual.md"
    echo "Produce: research/survivors.md  coverage.md update"
    echo "Do not: restart P0. Short user orders ('investigate X') land here when OPEN."
    ;;
  P9)
    header "P9 Rate · Report"
    echo "Load: $KENSHO/SKILL.md   # Parts 7–8 only"
    echo "      $IYKES/SKILL.md    # Steps 8–9"
    echo "Run:"
    echo "  python3 $APEX/scripts/component_check.py research/"
    echo "  python3 $APEX/scripts/claim_gate.py research/"
    echo "  bash $APEX/scripts/report_gate.sh research/"
    echo "Produce: research/report.md  (honest empty OR CONFIRMED-REPORTABLE)"
    echo "Do not: SURVIVOR in report.md. Do not JACKPOT a TRUST finding."
    ;;
  P10)
    header "P10 Disclose"
    echo "Load: $KENSHO/SKILL.md   # Part 9"
    echo "Run:  $IYKES/tools/step10_contact_hunt.sh"
    echo "      $IYKES/tools/step10_dm_skeleton.py"
    echo "Produce: reports/contacts.md with URL + exact quote"
    echo "Do not: guess security@."
    ;;
  PR|R)
    header "PR Retro"
    echo "Run:"
    echo "  python3 $APEX/scripts/retro.py --finding/--fp/--register-target ..."
    echo "Produce: ~/.apex-sentinel/ LEARNINGS + targets.json"
    echo "Do not: close without this."
    ;;
  *)
    echo "unknown phase: $PHASE" >&2
    exit 2
    ;;
esac
