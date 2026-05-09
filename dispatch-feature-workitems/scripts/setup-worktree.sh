#!/usr/bin/env bash
# Scaffolds one feature worktree: branch, workitem commit, push, MR, and dep install.
# Usage: setup-worktree.sh <slug> <title> [label]
set -euo pipefail

SLUG="$1"
TITLE="$2"
LABEL="${3:-vibes}"
WORKITEM_DOC="docs/workitems/${SLUG}.md"
WORKTREE_DIR=".worktrees/${SLUG}"

# 1. Create worktree and branch
git worktree add "$WORKTREE_DIR" -b "feature/${SLUG}"

# 2. Copy workitem doc and commit
mkdir -p "${WORKTREE_DIR}/docs/workitems"
cp "$WORKITEM_DOC" "${WORKTREE_DIR}/${WORKITEM_DOC}"
git -C "$WORKTREE_DIR" add "${WORKITEM_DOC}"
git -C "$WORKTREE_DIR" commit -m "docs: add workitem for ${TITLE}"

# 3. Push branch
git -C "$WORKTREE_DIR" push -u origin "feature/${SLUG}"

# 4. Extract summary paragraph from workitem doc
SUMMARY=$(awk '/^## Summary/{found=1; next} found && /^## /{exit} found{print}' "$WORKITEM_DOC" | sed '/^[[:space:]]*$/d' | head -5)

# 5. Create draft MR
glab mr create --draft \
  --label "$LABEL" \
  -a cesasol \
  --source-branch "feature/${SLUG}" \
  -t "Draft: ${TITLE}" \
  -d "${SUMMARY}"

# 6. Auto-detect package manager and install dependencies
install_deps() {
  local dir="$1"
  if [ -f "${dir}/pnpm-lock.yaml" ]; then
    echo "pnpm detected — installing"
    pnpm --dir "$dir" install
  elif [ -f "${dir}/yarn.lock" ]; then
    echo "yarn detected — installing"
    (cd "$dir" && yarn install)
  elif [ -f "${dir}/package-lock.json" ]; then
    echo "npm detected — installing"
    (cd "$dir" && npm install)
  elif [ -f "${dir}/pyproject.toml" ]; then
    if command -v uv &>/dev/null; then
      echo "pyproject.toml + uv detected — syncing"
      (cd "$dir" && uv sync)
    else
      echo "pyproject.toml detected — pip installing"
      (cd "$dir" && pip install -e .)
    fi
  elif [ -f "${dir}/requirements.txt" ]; then
    echo "requirements.txt detected — pip installing"
    (cd "$dir" && pip install -r requirements.txt)
  elif [ -f "${dir}/Gemfile" ]; then
    echo "Gemfile detected — bundle installing"
    (cd "$dir" && bundle install)
  elif [ -f "${dir}/Cargo.toml" ]; then
    echo "Cargo.toml detected — skipping (cargo resolves at build time)"
  else
    echo "No recognized manifest — skipping dependency install"
  fi
}

install_deps "$WORKTREE_DIR"

echo ""
echo "Worktree ready:  ${WORKTREE_DIR}"
echo "Branch:          feature/${SLUG}"
