#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXPECTED="$SCRIPT_DIR/expected.yml"
echo "=== rust-musl-release assertions ==="
python3 "$REPO_ROOT/gitlab-ci/tests/assertions.py" "$EXPECTED"
grep -q "x86_64-unknown-linux-musl" "$EXPECTED" && echo "[PASS] musl target present" || { echo "[FAIL] missing musl target"; exit 1; }
grep -q "cargo build --release --target" "$EXPECTED" && echo "[PASS] release build with target" || { echo "[FAIL] missing release build"; exit 1; }
echo "=== All assertions passed ==="
