#!/usr/bin/env bash
# Master validation script for the gitlab-ci skill.
# Run from repo root: bash gitlab-ci/tests/validate.sh
set -euo pipefail

SKILL_DIR="gitlab-ci"
TESTS_DIR="gitlab-ci/tests"
REF_DIR="$SKILL_DIR/references"
SKILL_FILE="$SKILL_DIR/SKILL.md"

REF_FILES=(
    "$REF_DIR/_common.md"
    "$REF_DIR/nodejs.md"
    "$REF_DIR/python.md"
    "$REF_DIR/go.md"
    "$REF_DIR/docker.md"
    "$REF_DIR/rust.md"
    "$REF_DIR/advanced.md"
)
ALL_REF_FILES=("$SKILL_FILE" "${REF_FILES[@]}")

FAILED=0

pass() { echo "[PASS] $1"; }
fail() { echo "[FAIL] $1"; FAILED=1; }
warn() { echo "[WARN] $1"; }

# ─── Check 1: SKILL.md frontmatter ───────────────────────────────────────────
check_frontmatter() {
    python3 -c "
import yaml, sys
try:
    with open('$SKILL_FILE') as f:
        content = f.read()
    parts = content.split('---', 2)
    if len(parts) < 3:
        sys.exit(1)
    meta = yaml.safe_load(parts[1])
    if not isinstance(meta, dict) or 'name' not in meta:
        sys.exit(1)
    sys.exit(0)
except Exception:
    sys.exit(1)
" && pass "SKILL.md frontmatter" || fail "SKILL.md frontmatter"
}

# ─── Check 2: SKILL.md line count ≤200 ───────────────────────────────────────
check_line_count() {
    local lines
    lines=$(wc -l < "$SKILL_FILE")
    if [ "$lines" -le 200 ]; then
        pass "SKILL.md line count ($lines ≤ 200)"
    else
        fail "SKILL.md line count ($lines > 200)"
    fi
}

# ─── Check 3: All reference files exist ──────────────────────────────────────
check_ref_files_exist() {
    local all_exist=0
    for f in "${ALL_REF_FILES[@]}"; do
        if [ -f "$f" ]; then
            echo "  [OK] $f"
        else
            echo "  [MISSING] $f"
            all_exist=1
        fi
    done
    if [ "$all_exist" -eq 0 ]; then
        pass "All reference files exist (${#ALL_REF_FILES[@]} files)"
    else
        fail "Some reference files are missing"
    fi
}

# ─── Check 4: No deprecated keywords in reference files ──────────────────────
check_no_deprecated_keywords() {
    local found=0
    for f in "${REF_FILES[@]}"; do
        if grep -n -E '^\s*(only|except):' "$f" 2>/dev/null; then
            echo "  [DEPRECATED] Found in: $f"
            found=1
        fi
    done
    if [ "$found" -eq 0 ]; then
        pass "No deprecated keywords (only/except) in reference files"
    else
        fail "Deprecated keywords found in reference files"
    fi
}

# ─── Check 5: Each reference file cites ≥1 GitLab docs URL ───────────────────
check_gitlab_docs_urls() {
    local missing=0
    for f in "${REF_FILES[@]}"; do
        if grep -q 'docs.gitlab.com' "$f" 2>/dev/null; then
            :
        else
            echo "  [NO DOCS URL] $f"
            missing=1
        fi
    done
    if [ "$missing" -eq 0 ]; then
        pass "All reference files cite at least one GitLab docs URL"
    else
        fail "Some reference files are missing GitLab docs URLs"
    fi
}

# ─── Check 6: yamllint on expected.yml files ─────────────────────────────────
check_yamllint() {
    if ! command -v yamllint &>/dev/null; then
        warn "yamllint not installed — skipping yamllint check"
        return
    fi
    local errors=0
    while IFS= read -r -d '' f; do
        if ! yamllint -d relaxed "$f" >/dev/null 2>&1; then
            echo "  [YAML LINT ERROR] $f"
            yamllint -d relaxed "$f" | sed 's/^/    /'
            errors=1
        fi
    done < <(find "$TESTS_DIR/evals" -name 'expected.yml' -print0 2>/dev/null || true)
    if [ "$errors" -eq 0 ]; then
        pass "yamllint passed on all expected.yml files"
    else
        fail "yamllint errors found"
    fi
}

# ─── Check 7: assertions.py on all expected.yml ──────────────────────────────
check_assertions_py() {
    local errors=0
    while IFS= read -r -d '' f; do
        echo "  [CHECK] $f"
        if python3 "$TESTS_DIR/assertions.py" "$f" >/dev/null 2>&1; then
            :
        else
            echo "  [FAIL] assertions.py failed on $f"
            python3 "$TESTS_DIR/assertions.py" "$f" 2>&1 | sed 's/^/    /'
            errors=1
        fi
    done < <(find "$TESTS_DIR/evals" -name 'expected.yml' -print0 2>/dev/null || true)
    if [ "$errors" -eq 0 ]; then
        pass "assertions.py passed on all expected.yml files"
    else
        fail "assertions.py failed on some expected.yml files"
    fi
}

# ─── Main ────────────────────────────────────────────────────────────────────
echo "=== gitlab-ci skill validation ==="
echo ""

check_frontmatter
check_line_count
check_ref_files_exist
check_no_deprecated_keywords
check_gitlab_docs_urls
check_yamllint
check_assertions_py

echo ""
if [ "$FAILED" -eq 0 ]; then
    echo "All checks passed."
    exit 0
else
    echo "Some checks failed."
    exit 1
fi
