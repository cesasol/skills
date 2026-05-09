#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"
echo "=== rust-cargo-clippy assertions ==="
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED"
grep -q "cargo clippy.*-D warnings" "$EXPECTED" && echo "[PASS] clippy -D warnings" || { echo "[FAIL] missing clippy -D warnings"; exit 1; }
grep -q "cargo fmt.*--check" "$EXPECTED" && echo "[PASS] cargo fmt --check" || { echo "[FAIL] missing cargo fmt --check"; exit 1; }
echo "=== All assertions passed ==="
