# Agents

This folder contains reusable agent and subagent definitions. There is no mature cross-harness standard for agents comparable to the Agent Skills specification, so definitions here use a portable Markdown contract plus thin frontmatter adapters for the current target harness.

## Recommended shape

Each agent file should keep two layers separate:

1. **Portable contract** — role, trigger, responsibilities, boundaries, workflow, verification, and reporting. This should remain useful even if copied into another harness.
2. **Harness adapter** — frontmatter keys such as `description`, `mode`, `model`, and `tools`. These are harness-specific and usually need translation when copied elsewhere.

```markdown
---
name: agent-name
description: "Short trigger-oriented description. Say when to use the agent."
mode: subagent
model: provider/model-name
tools:
  read: true
  grep: true
  edit: true
  bash: false
---

# Agent Name — Role

Portable behavior contract goes here.
```

## Authoring checklist

- **Trigger:** Describe user intent, not implementation details. Use phrases like "Use when...".
- **Role:** State the agent's narrow specialty in one sentence.
- **Name:** Include a stable kebab-case `name` even if the target harness derives identity from the filename.
- **Inputs:** Name what context the orchestrator should provide.
- **Allowed work:** List file types, actions, and tools the agent may use.
- **Boundaries:** Explicitly say what the agent must not modify or decide.
- **Workflow:** Give a short ordered process that works without hidden context.
- **Verification:** Define what evidence must be checked before completion.
- **Reporting:** Specify the concise handoff format expected by the orchestrator.
- **Portability:** Avoid project names, private paths, personal accounts, and harness-only tool names in the body unless they are clearly marked as adapter details.

## Harness notes

- **Claude Code:** Custom subagents commonly use Markdown files with YAML frontmatter for description, model, and tool access. Keep prompts self-contained because subagents may not inherit the full orchestrator context.
- **OpenCode:** Agents can be Markdown files or host configuration entries. The filename is commonly the identifier, while frontmatter/config carries description, mode, model, tools, and permissions.
- **Codex:** There is no direct Markdown-frontmatter subagent equivalent to Claude Code/OpenCode. Preserve the Markdown behavior contract and translate it into the local Codex configuration, `AGENTS.md` guidance, profiles, sandbox settings, or developer instructions where supported.
- **Pi:** Pi-style subagents use Markdown plus YAML frontmatter with fields for name/description, model, tools, thinking/context options, and isolation. Translate the adapter keys rather than assuming exact spelling compatibility.
- **Other harnesses:** Treat support as implementation-defined unless the harness documents a formal agent schema. Use the Markdown body as the source of truth and write a small adapter when needed.

## Repository policy

- Agents should be reusable across projects unless their filename or README section clearly marks them as project-specific.
- Prefer read/search/edit permissions over shell access. Grant shell only when the role truly owns command execution.
- Keep agent prompts deterministic: no hidden dependencies, no unbounded authority, and no vague "be helpful" scope.
- Pair every capability with a boundary and every completion claim with verification evidence.
