#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"
echo "=== docker-registry-push assertions ==="
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED"
grep -q "CI_REGISTRY_IMAGE" "$EXPECTED" && echo "[PASS] CI_REGISTRY_IMAGE used" || { echo "[FAIL] missing CI_REGISTRY_IMAGE"; exit 1; }
grep -q "CI_COMMIT_SHORT_SHA" "$EXPECTED" && echo "[PASS] SHA tag present" || { echo "[FAIL] missing SHA tag"; exit 1; }
grep -q "CI_COMMIT_REF_SLUG" "$EXPECTED" && echo "[PASS] ref slug tag present" || { echo "[FAIL] missing ref slug tag"; exit 1; }
echo "=== All assertions passed ==="
