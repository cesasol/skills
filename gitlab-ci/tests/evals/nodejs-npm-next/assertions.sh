#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"
echo "=== nodejs-npm-next assertions ==="
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED"
grep -q "npm ci" "$EXPECTED" && echo "[PASS] npm ci present" || { echo "[FAIL] missing npm ci"; exit 1; }
grep -q "\.next/" "$EXPECTED" && echo "[PASS] .next/ artifact" || { echo "[FAIL] missing .next/ artifact"; exit 1; }
echo "=== All assertions passed ==="
