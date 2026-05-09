---
name: dispatch-feature-workitems
description: >
  Use when user provides one or more feature requests that should be developed in parallel,
  each needing an isolated branch, worktree, tracking document in docs/workitems/, and a
  GitLab draft MR. Triggers on phrases like "implement these features", "work on these items
  in parallel", or any list of requirements that can be built independently.
---

# Dispatch Feature Workitems

## Overview

Turns a list of feature requests into parallel development streams. The orchestrator handles all
Bash-dependent steps (worktrees, commits, pushes, MR creation) because **Bash is blocked for
subagents**. Agents only perform file reading and editing within their assigned worktree.

**Core principle:** Orchestrator owns all shell operations. Agents own only file edits.

## Workflow

### Phase 1 — Expand Workitems (Orchestrator)

For each request, derive a slug and write `docs/workitems/<slug>.md` **without committing**.

Slug rules: lowercase, hyphens only, alphanumeric.  
Example: "Add dark mode toggle" → `add-dark-mode-toggle`

**Workitem document template:**

```markdown
# <Title>

## Summary
<1–2 paragraph expansion of the request, clarifying intent and scope>

## Requirements
- <concrete requirement>
- <concrete requirement>

## Acceptance Criteria
- [ ] <verifiable criterion>
- [ ] <verifiable criterion>

## Technical Notes
<affected files, constraints, implementation hints>
```

### Phase 2 — Infrastructure Setup (Orchestrator, sequential)

All shell steps are handled by `scripts/setup-worktree.sh`. On first use in a project, copy the
bundled script to `.claude/scripts/setup-worktree.sh` and make it executable — the full source is
also embedded at the bottom of this skill. Then call it once per workitem:

```bash
bash .claude/scripts/setup-worktree.sh <slug> "<title>" [label]
```

The script handles in order:
1. `git worktree add` — creates the isolated branch and worktree
2. Copies the workitem doc and makes the first commit
3. `git push -u origin feature/<slug>`
4. `glab mr create --draft` — extracts the summary paragraph automatically
5. Dependency install — auto-detects the package manager (pnpm, yarn, npm, uv/pip, bundler, Cargo) or skips if none found

Run this for each workitem **before** dispatching agents.

### Phase 3 — Dispatch Parallel Agents (Orchestrator)

Use **superpowers:dispatching-parallel-agents**. Send ALL agents in a **single message** so they
run concurrently. Each agent prompt must be **self-contained** — agents inherit no context.

Use `subagent_type: "general-purpose"` for each agent — they need Read, Write, Edit, Glob, and
Grep but no Bash.

Agents must be told explicitly:
- The absolute path of their worktree
- That they CANNOT run Bash or shell commands
- What files to read, edit, or create

### Phase 4 — Commit and Push Agent Work (Orchestrator)

After all agents complete, for each worktree commit and push the implementation:

```bash
cd .worktrees/<slug>
git add -A
git commit -m "feat(<scope>): <short description>"
git push
```

---

## Agent Prompt Template

Use this template when dispatching each agent. Replace all `<placeholders>`.
Set `subagent_type: "general-purpose"` on each Agent tool call.

```
You are implementing a feature inside an isolated git worktree. You cannot run Bash or shell
commands — use only Read, Write, Edit, Glob, and Grep tools.

Worktree absolute path: /path/to/.worktrees/<slug>
Branch: feature/<slug>  (already created and pushed — do NOT run git commands)

## Workitem

<paste the full docs/workitems/<slug>.md content here>

## What to do

Implement the feature described above. All your file operations must target the worktree path
above. The worktree is an independent copy of the repo with its own branch — edits here do not
affect main or other worktrees.

Read the relevant files, then apply your changes. Do not run any shell commands, do not commit,
do not push — the orchestrator will handle git after you return.

Return a brief summary of what you changed and any issues you encountered.
```

---

## Quick Reference

| Step | Actor | Action |
|------|-------|--------|
| Write workitem docs | Orchestrator | `docs/workitems/<slug>.md`, do NOT commit to main |
| Create worktree | Orchestrator | `git worktree add .worktrees/<slug> -b feature/<slug>` |
| Commit doc | Orchestrator | First commit inside worktree |
| Push branch | Orchestrator | `git push -u origin feature/<slug>` |
| Create MR | Orchestrator | `glab mr create --draft ...` |
| Setup worktree | Orchestrator | `bash .claude/scripts/setup-worktree.sh <slug> "<title>"` |
| Dispatch agents | Orchestrator | One agent per item, all in one message (parallel) |
| Implement feature | Agent | File edits only — no Bash |
| Commit + push impl | Orchestrator | After agents return |

---

## Common Mistakes

**Delegating Bash to agents** — Agents cannot run shell commands. All git, glab, and install
operations must happen in the orchestrator (via `setup-worktree.sh`) before agent dispatch, and
via direct git calls after agents return.

**Sequential dispatch** — All agents must be sent in a single message for true parallelism.

**Vague agent prompts** — Include the full workitem doc content inline and the absolute worktree
path. Agents have zero inherited context.

**Skipping the worktree** — Always isolate each workitem in its own worktree to prevent conflicts.

**Committing workitem docs to main** — Write the files but do NOT commit them on main. Copy them
into the worktree as the first commit on the feature branch.

**Interactive glab** — Always pass flags non-interactively. See the **glab** skill for details.

---

## Integration

This skill orchestrates:

- **superpowers:dispatching-parallel-agents** — parallel agent dispatch pattern
- **superpowers:using-git-worktrees** — isolated worktree per branch
- **glab** — GitLab MR creation and management
- **superpowers:brainstorming** — use first if requirements need clarification

---

## setup-worktree.sh (embed in project on first use)

Write this to `.claude/scripts/setup-worktree.sh` and `chmod +x` it before running Phase 2.

```bash
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
```
