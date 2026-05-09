#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"
echo "=== go-test-golangci assertions ==="
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED"
grep -q "go test.*-race" "$EXPECTED" && echo "[PASS] race flag present" || { echo "[FAIL] missing -race flag"; exit 1; }
grep -q "golangci-lint" "$EXPECTED" && echo "[PASS] golangci-lint present" || { echo "[FAIL] missing golangci-lint"; exit 1; }
echo "=== All assertions passed ==="
