#!/usr/bin/env bash
# Package MotorCraft_BP + MotorCraft_RP into MotorCraft.mcaddon.
# Runs the validator first and aborts on any error.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> validating"
python3 tools/validate.py

OUT="MotorCraft.mcaddon"
echo "==> packaging $OUT"
rm -f "$OUT"
# .mcaddon is a zip with the two pack folders at the top level.
zip -r -q -X "$OUT" MotorCraft_BP MotorCraft_RP \
  -x '*/.DS_Store' -x '*__pycache__*' -x '*.swp'

echo "==> done: $(du -h "$OUT" | cut -f1)  $OUT"
