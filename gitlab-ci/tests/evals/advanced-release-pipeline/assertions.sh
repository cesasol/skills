#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"
echo "=== advanced-release-pipeline assertions ==="
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED"
grep -q "resource_group: production" "$EXPECTED" && echo "[PASS] resource_group present" || { echo "[FAIL] missing resource_group"; exit 1; }
grep -q "environment:" "$EXPECTED" && echo "[PASS] environment blocks present" || { echo "[FAIL] missing environment"; exit 1; }
grep -q "release:" "$EXPECTED" && echo "[PASS] release job present" || { echo "[FAIL] missing release job"; exit 1; }
echo "=== All assertions passed ==="
