#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"
echo "=== nodejs-pnpm-playwright assertions ==="
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED"
grep -q "pnpm install --frozen-lockfile" "$EXPECTED" && echo "[PASS] pnpm frozen-lockfile" || { echo "[FAIL] missing pnpm frozen-lockfile"; exit 1; }
grep -q "playwright" "$EXPECTED" && echo "[PASS] playwright present" || { echo "[FAIL] missing playwright"; exit 1; }
grep -q "test:e2e" "$EXPECTED" && echo "[PASS] e2e job present" || { echo "[FAIL] missing e2e job"; exit 1; }
echo "=== All assertions passed ==="
