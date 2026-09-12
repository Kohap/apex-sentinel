#!/usr/bin/env bash
# Apex report gate — ragnarok report_gate + claim_gate + component handshake.
# Honest empty report still PASSes. A finding without fp-kill.md FAILS.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR="$HERE/vendor/ragnarok/report_gate.sh"
RESEARCH="research"
WRITE=0
for arg in "$@"; do
  if [ "$arg" = "--write" ]; then
    WRITE=1
  else
    RESEARCH="$arg"
  fi
done

echo "== apex component_check =="
python3 "$HERE/component_check.py" "$RESEARCH"
CC_RC=$?
echo
echo "== apex claim_gate =="
python3 "$HERE/claim_gate.py" "$RESEARCH"
CG_RC=$?
echo
echo "== ragnarok report_gate =="
if [ -x "$VENDOR" ]; then
  if [ "$WRITE" -eq 1 ]; then
    bash "$VENDOR" "$RESEARCH" --write
  else
    bash "$VENDOR" "$RESEARCH"
  fi
  RG_RC=$?
else
  echo "apex report_gate: vendor missing at $VENDOR" >&2
  RG_RC=1
fi

echo
if [ "$CC_RC" -ne 0 ] || [ "$CG_RC" -ne 0 ] || [ "$RG_RC" -ne 0 ]; then
  echo "APEX REPORT GATE FAIL (component=$CC_RC claim=$CG_RC ragnarok=$RG_RC)"
  echo "Do not disclose. Finish fp-kill.md / handshake / harness, or keep the honest empty report."
  exit 1
fi
echo "APEX REPORT GATE PASS"
exit 0
