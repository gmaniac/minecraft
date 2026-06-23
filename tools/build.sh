#!/usr/bin/env bash
# Package Wildforge_BP + Wildforge_RP into Wildforge.mcaddon.
# Runs the validator first and aborts on any error.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> validating"
python3 tools/validate.py

OUT="Wildforge.mcaddon"
echo "==> packaging $OUT"
rm -f "$OUT"
# .mcaddon is a zip with the two pack folders at the top level.
zip -r -q -X "$OUT" Wildforge_BP Wildforge_RP \
  -x '*/.DS_Store' -x '*__pycache__*' -x '*.swp'

echo "==> done: $(du -h "$OUT" | cut -f1)  $OUT"
