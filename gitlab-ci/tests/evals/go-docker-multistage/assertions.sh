#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"
echo "=== go-docker-multistage assertions ==="
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED"
grep -q "CI_REGISTRY_IMAGE" "$EXPECTED" && echo "[PASS] CI_REGISTRY_IMAGE used" || { echo "[FAIL] missing CI_REGISTRY_IMAGE"; exit 1; }
grep -q "docker build" "$EXPECTED" && echo "[PASS] docker build present" || { echo "[FAIL] missing docker build"; exit 1; }
echo "=== All assertions passed ==="
