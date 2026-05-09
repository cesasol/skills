#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"
echo "=== python-uv-pytest assertions ==="
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED"
grep -q "uv sync" "$EXPECTED" && echo "[PASS] uv sync present" || { echo "[FAIL] missing uv sync"; exit 1; }
grep -q "ruff" "$EXPECTED" && echo "[PASS] ruff present" || { echo "[FAIL] missing ruff"; exit 1; }
grep -q "pytest" "$EXPECTED" && echo "[PASS] pytest present" || { echo "[FAIL] missing pytest"; exit 1; }
echo "=== All assertions passed ==="
