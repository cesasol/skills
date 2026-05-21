---
name: dispatch-gitlab-feature-workitems
description: >
  Use when working in a GitLab-hosted repository and the user provides one or more feature
  requests that should be developed in parallel, each needing an isolated branch, worktree,
  tracking document in docs/workitems/, and a GitLab draft merge request created with glab.
  Do not use for GitHub repos or generic task planning.
---

# Dispatch GitLab Feature Workitems

## Overview

Turn a list of independent feature requests in a GitLab repository into parallel development streams, each with a workitem document, isolated git worktree, feature branch, and draft GitLab MR.

**Core principle:** the orchestrator owns shell operations and git state; implementation agents own only file reads/edits inside their assigned worktree. This prevents agents from clobbering each
other or pushing incomplete work.

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

All shell steps are handled by the bundled `dispatch-gitlab-feature-workitems/scripts/setup-worktree.sh`. Run the bundled script in place; do not copy it into the target repository, because copied
scripts grow stale and pollute project files.

```bash
bash <skill-dir>/scripts/setup-worktree.sh <slug> "<title>" [label] [assignee]
```

The script handles in order:

1. Validates the current repository is accessible as a GitLab project with `glab repo view -F json`
2. Ensures `.worktrees/` is ignored locally via `.git/info/exclude`
3. `git worktree add` — creates the isolated branch and worktree
4. Copies the workitem doc and makes the first commit
5. `git push -u origin feature/<slug>`
6. `glab mr create --draft` — extracts the summary paragraph automatically and assigns the MR when an assignee is provided or can be inferred from `glab auth status`
7. Dependency install — auto-detects the package manager (pnpm, yarn, npm, uv/pip, bundler, Cargo) or skips if none found

Run this for each workitem **before** dispatching agents.

### Phase 3 — Dispatch Parallel Agents (Orchestrator)

Launch all implementation agents in the same turn so they run concurrently. Each agent prompt must be self-contained because agents may not inherit context.

Use the worker/general implementation agent type available in the current harness (`agent_type: "worker"` in Codex, or the equivalent general-purpose implementation agent elsewhere). Tell agents to
avoid Bash/shell commands even if their harness exposes them; the orchestrator will handle validation, commits, pushes, and MR updates.

Agents must be told explicitly:

- The absolute path of their worktree
- That they must not run Bash, shell, git, package-manager, or MR commands
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
Set the implementation worker agent type on each Agent tool call (`agent_type: "worker"` in Codex).

```text
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
| ------ | ------- | -------- |
| Write workitem docs | Orchestrator | `docs/workitems/<slug>.md`, do NOT commit to main |
| Create worktree | Orchestrator | `git worktree add .worktrees/<slug> -b feature/<slug>` |
| Commit doc | Orchestrator | First commit inside worktree |
| Push branch | Orchestrator | `git push -u origin feature/<slug>` |
| Create MR | Orchestrator | `glab mr create --draft ...` |
| Setup worktree | Orchestrator | `bash <skill-dir>/scripts/setup-worktree.sh <slug> "<title>" [label] [assignee]` |
| Dispatch agents | Orchestrator | One agent per item, all in one message (parallel) |
| Implement feature | Agent | File edits only — no Bash |
| Commit + push impl | Orchestrator | After agents return |

---

## Gotchas

- This skill is only for GitLab repositories. If `glab repo view -F json` fails or the project is hosted on GitHub, do not use this workflow.
- This skill is only for feature requests that can be built independently. If the requests share files heavily or require a design decision first, clarify and sequence the work instead of dispatching
  immediately.
- Keep `docs/workitems/<slug>.md` uncommitted on the main worktree; the setup script copies and commits it inside each feature worktree.
- The setup script creates and pushes branches and draft MRs. Review generated slugs/titles before running it because those names become public branch/MR metadata.
- Pass an assignee as the fourth script argument when the authenticated `glab` user should not own the MR. You can also set `GITLAB_WORKITEM_ASSIGNEE`.
- The script ignores `.worktrees/` through `.git/info/exclude` so it does not modify project `.gitignore`.

## Common Mistakes

**Delegating shell work to agents** — Keep all git, glab, dependency install, and validation commands in the orchestrator. Use `setup-worktree.sh` before agent dispatch, then commit/push
implementations after agents return.

**Sequential dispatch** — All agents must be sent in a single message for true parallelism.

**Vague agent prompts** — Include the full workitem doc content inline and the absolute worktree
path. Agents have zero inherited context.

**Skipping the worktree** — Always isolate each workitem in its own worktree to prevent conflicts.

**Committing workitem docs to main** — Write the files but do NOT commit them on main. Copy them
into the worktree as the first commit on the feature branch.

**Interactive glab** — Always pass flags non-interactively. See the **glab** skill for details.

---

## Bundled resources

- `scripts/setup-worktree.sh`. Run it from the skill directory rather than copying it into the target repo. It validates GitLab access, locally ignores `.worktrees/`, creates the worktree and branch,
  commits the workitem doc, pushes the branch, opens a draft MR with `glab`, assigns the MR when possible, and installs dependencies when a recognized manifest is present.

## Related skills

- Use the `glab` skill for GitLab MR creation and management details.
- Use a brainstorming/planning workflow first if requirements need clarification before dispatch.
