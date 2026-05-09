# Skills

A collection of skills for AI coding agents like [OpenCode](https://github.com/opencode-ai/opencode) and Claude Code.

## Available Skills

| Skill | Description |
|-------|-------------|
| [comfyui](comfyui/SKILL.md) | Run FLUX.2 image generation/editing workflows on a local ComfyUI instance (`localhost:8188`). |
| [dispatch-feature-workitems](dispatch-feature-workitems/SKILL.md) | Parallel feature development workflow: expands requirements into workitem docs, dispatches one agent per item, each with its own worktree, branch, and GitLab draft MR. |
| [docs-layout](docs-layout/SKILL.md) | Normalized `docs/` folder layout with a shared spine (decisions, roadmap, reports, runbooks, reference) plus backend/frontend extras, with naming conventions for phased, dated, and flat files. |
| [flux-prompt-gen](flux-prompt-gen/SKILL.md) | Generate optimized text-to-image prompts for Black Forest Labs FLUX models (FLUX.1, FLUX.2 [pro], FLUX.2 [max], FLUX.2 [klein]). |
| [glab](glab/SKILL.md) | GitLab CLI (`glab`) — merge requests, issues, CI/CD pipelines, releases, API access, and full project management from the terminal. |
| [just](just/SKILL.md) | Command runner best practices for justfiles, shared recipes, and CI entrypoints. |
| [prek](prek/SKILL.md) | Fast pre-commit-compatible hook runner setup, configuration, and CI usage. |
| [rumdl](rumdl/SKILL.md) | Fast Markdown linting and formatting with rumdl configuration and CI guidance. |

## Agent Definitions

Reusable agent and subagent prompts live in [`agents/`](agents/). They are not Agent Skills packages;
they use a portable Markdown behavior contract plus optional harness-specific frontmatter for tools,
model selection, and subagent mode.

## Installation

### Requirements

- [OpenCode](https://github.com/opencode-ai/opencode) or any agent that supports the skills format (Claude Code, etc.)

### Install via Skills CLI

```bash
# Replace SKILL_NAME with: comfyui, docs-layout, flux-prompt-gen, glab, or resume-pdf
npx skills add cesasol/skills@SKILL_NAME
```

### Download `.skill` package

Each skill is published to the GitLab Package Registry on every push to `main`:

```bash
# Latest version
curl -LO "https://gitlab.com/api/v4/projects/cesasol%2Fskills/packages/generic/SKILL_NAME/latest/SKILL_NAME.skill"

# Specific version (commit SHA)
curl -LO "https://gitlab.com/api/v4/projects/cesasol%2Fskills/packages/generic/SKILL_NAME/VERSION/SKILL_NAME.skill"
```

### Manual Installation

Clone the repo and copy the skill directory into your agent's skills folder:

```bash
git clone https://gitlab.com/cesasol/skills.git

# Global (all projects)
cp -r skills/SKILL_NAME ~/.agents/skills/SKILL_NAME

# Project-level
cp -r skills/SKILL_NAME .opencode/skills/SKILL_NAME
```

### Verify

Once installed, the agent should list the skill in its available skills. You can test by asking:

> "Check the pipeline status for the current branch using glab."

## Development

### Agent Skills specification coverage

This repository validates every top-level skill directory against the public
[Agent Skills specification](https://agentskills.io/specification.md) before packaging.

```bash
just ci
```

The shared CI recipe runs rumdl Markdown linting, prek hooks, Agent Skills validation,
unit tests, and skill package verification. The validator enforces hard requirements
for `SKILL.md` frontmatter, skill naming, optional field shapes, directory/name
consistency, and local Markdown references.

## Developer

Built by [@cesasol](https://cesasol.dev/).

## License

MIT
