#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"

echo "=== Template eval assertions ==="

# 1. File exists
test -f "$EXPECTED" && echo "[PASS] expected.yml exists" || { echo "[FAIL] expected.yml missing"; exit 1; }

# 2. assertions.py passes
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED" || exit 1

echo "=== All assertions passed ==="
