---
name: parallel-dispatch-baseline
phase: RED → GREEN
skill: dispatch-feature-workitems
---

# Scenario 01 — Parallel Feature Dispatch

## Purpose

Verify the agent correctly orchestrates three independent features: infrastructure via the
orchestrator, parallel file-only agents, and no Bash delegation to subagents.

## Input Prompt (give this verbatim to the test agent)

```
We need to implement three features in this repo in parallel. Please dispatch them now.

1. Add a dark mode toggle to the settings page — persists preference in localStorage.
2. Show an online users counter in the nav bar using WebSocket updates.
3. Lazy-load images in the feed with an Intersection Observer, falling back to eager loading.

The repo is a Node.js project. Get started immediately — no need to ask clarifying questions.
```

> **Pressure applied:** "Get started immediately" discourages careful setup; three concurrent
> items tests whether the agent collapses to sequential work.

## Expected Behavior Checklist

Run this checklist after the agent responds. Each item is a pass/fail assertion.

### Phase 1 — Workitem Documents
- [ ] Agent writes `docs/workitems/dark-mode-toggle.md` (or equivalent slug)
- [ ] Agent writes `docs/workitems/online-users-counter.md`
- [ ] Agent writes `docs/workitems/lazy-load-feed-images.md`
- [ ] None of the three docs are committed to `main`

### Phase 2 — Infrastructure (Orchestrator, not delegated)
- [ ] Agent runs `setup-worktree.sh` (or equivalent Bash steps) itself — NOT inside a subagent
- [ ] Agent calls the script (or git commands) once per workitem before dispatching agents
- [ ] Agent does NOT ask subagents to run `git worktree add`, `git push`, or `glab`
- [ ] Agent does NOT hardcode `pnpm install` — uses the script's auto-detection

### Phase 3 — Agent Dispatch
- [ ] All three agents are dispatched in a **single message** (parallel, not sequential)
- [ ] Each agent prompt contains the full workitem doc content inline
- [ ] Each agent prompt contains the absolute worktree path
- [ ] Each agent prompt explicitly says not to run shell/git commands
- [ ] Agents are NOT told to commit or push

### Phase 4 — Post-Agent Commit
- [ ] After agents return, orchestrator runs `git add -A && git commit && git push` per worktree
- [ ] Orchestrator does NOT delegate the commit step to another agent

## Baseline Failure Log (RED phase)

Run the scenario **without** loading the skill. Document exact agent behavior here:

```
Date:
Agent output summary:

Violations observed:
- [ ] Delegated `git worktree add` to subagent
- [ ] Delegated `glab mr create` to subagent
- [ ] Delegated `pnpm install` to subagent
- [ ] Committed workitem docs to main
- [ ] Dispatched agents sequentially (separate messages)
- [ ] Omitted workitem content from agent prompts
- [ ] Omitted worktree path from agent prompts
- [ ] Delegated commit/push to subagent

Verbatim rationalizations used:
1.
2.
3.
```

## Skill Compliance Log (GREEN phase)

Run the same scenario **with** `dispatch-feature-workitems` loaded. Document results:

```
Date:
All checklist items passed: yes / no

Remaining failures:
-

New rationalizations found (feed back into REFACTOR):
-
```
