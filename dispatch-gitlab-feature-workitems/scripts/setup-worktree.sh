#!/usr/bin/env bash
# Scaffolds one feature worktree: branch, workitem commit, push, MR, and dep install.
# Usage: setup-worktree.sh <slug> <title> [label] [assignee]
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: setup-worktree.sh <slug> <title> [label] [assignee]" >&2
  exit 2
fi

SLUG="$1"
TITLE="$2"
LABEL="${3:-vibes}"
ASSIGNEE="${4:-${GITLAB_WORKITEM_ASSIGNEE:-}}"
WORKITEM_DOC="docs/workitems/${SLUG}.md"
WORKTREE_DIR=".worktrees/${SLUG}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: run this script from inside the target git repository." >&2
  exit 1
fi

if [ ! -f "$WORKITEM_DOC" ]; then
  echo "Error: workitem document not found: $WORKITEM_DOC" >&2
  exit 1
fi

if ! command -v glab >/dev/null 2>&1; then
  echo "Error: glab is required for GitLab repository validation and MR creation." >&2
  exit 1
fi

if ! glab repo view -F json >/dev/null; then
  echo "Error: this repository is not accessible as a GitLab project via 'glab repo view -F json'." >&2
  echo "Use this workflow only for GitLab-hosted repositories." >&2
  exit 1
fi

GIT_DIR=$(git rev-parse --git-common-dir)
INFO_EXCLUDE="${GIT_DIR}/info/exclude"
mkdir -p "$(dirname "$INFO_EXCLUDE")"
touch "$INFO_EXCLUDE"
if ! grep -qxF '.worktrees/' "$INFO_EXCLUDE"; then
  printf '\n.worktrees/\n' >> "$INFO_EXCLUDE"
  echo "Added .worktrees/ to ${INFO_EXCLUDE}"
fi

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
MR_ARGS=(
  --draft
  --label "$LABEL"
  --source-branch "feature/${SLUG}"
  -t "Draft: ${TITLE}"
  -d "${SUMMARY}"
)

if [ -z "$ASSIGNEE" ]; then
  ASSIGNEE="$(glab auth status 2>&1 | awk '/Logged in to .* as /{print $NF; exit}' || true)"
fi

if [ -n "$ASSIGNEE" ]; then
  MR_ARGS+=(-a "$ASSIGNEE")
fi

glab mr create "${MR_ARGS[@]}"

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
