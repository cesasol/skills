# Skills

A collection of skills for AI coding agents like [OpenCode](https://github.com/opencode-ai/opencode) and Claude Code.

## Available Skills

| Skill                                                                           | Description                                                                                                                                                                                           |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [dispatch-gitlab-feature-workitems](dispatch-gitlab-feature-workitems/SKILL.md) | Parallel GitLab feature development workflow: expands requirements into workitem docs, dispatches one agent per item, each with its own worktree, branch, and GitLab draft MR.                        |
| [docs-layout](docs-layout/SKILL.md)                                             | Normalized `docs/` folder layout with a shared spine (decisions, roadmap, reports, runbooks, reference) plus backend/frontend extras, with naming conventions for phased, dated, and flat files.      |
| [fastapi-api](fastapi-api/SKILL.md)                                             | Production-grade FastAPI API conventions for project structure, routers, schemas, dependency injection, async database access, error handling, testing, migrations, and tooling.                      |
| [gitlab-ci](gitlab-ci/SKILL.md)                                                 | GitLab CI pipeline generation and refactoring for Node.js, Python, Go, Docker, and Rust projects, including components, inputs, matrix jobs, validation, caching, artifacts, and deployment patterns. |
| [gitlab-workflow](gitlab-workflow/SKILL.md)                                     | Single-branch GitLab Flow guidance for issues, feature branches, merge requests, reviews, pipeline checks, and GitLab Flavored Markdown using `glab`.                                                 |
| [glab](glab/SKILL.md)                                                           | GitLab CLI (`glab`) usage for merge requests, issues, CI/CD pipelines, releases, API access, project management, infrastructure resources, and safe non-interactive automation.                       |
| [image-prompt-crafter](image-prompt-crafter/SKILL.md)                           | Craft, upsample, and refine text prompts for AI image generation models: FLUX.1/2 Dev, FLUX.2 Klein, Z-Image Turbo, and Ernie Image. Outputs 2–3 prompt variations in clean code blocks.              |
| [just](just/SKILL.md)                                                           | Command runner best practices for justfiles, shared recipes, reproducible developer workflows, and CI entrypoints.                                                                                    |
| [prek](prek/SKILL.md)                                                           | Fast pre-commit-compatible hook runner setup, configuration, first-party hook selection, and CI usage.                                                                                                |
| [resume-pdf](resume-pdf/SKILL.md)                                               | Tailored, ATS-optimized PDF resume generation using a Pandoc + XeLaTeX pipeline.                                                                                                                      |
| [rumdl](rumdl/SKILL.md)                                                         | Fast Markdown linting and formatting with strict-but-agent-friendly rumdl configuration, first-party prek hooks, CI guidance, and documented exceptions.                                              |

## Deprecated Skills

| Skill                                       | Replacement                                                                                                                    | Notes                                                                      |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| [comfyui](comfyui/SKILL.md)                 | [image-prompt-crafter](image-prompt-crafter/SKILL.md) for prompt crafting; use project-specific ComfyUI tooling for execution. | Deprecated and retained for compatibility only.                            |
| [flux-prompt-gen](flux-prompt-gen/SKILL.md) | [image-prompt-crafter](image-prompt-crafter/SKILL.md)                                                                          | Deprecated; image-prompt-crafter covers FLUX plus additional image models. |

## Agent Definitions

Reusable agent and subagent prompts live in [`agents/`](agents/). They are not Agent Skills packages;
they use a portable Markdown behavior contract plus optional harness-specific frontmatter for tools,
model selection, and subagent mode.

## Installation

### Requirements

- [OpenCode](https://github.com/opencode-ai/opencode) or any agent that supports the skills format (Claude Code, etc.)

### Install via Skills CLI

```bash
# Replace SKILL_NAME with one of the available skill directory names, for example:
npx skills add cesasol/skills@image-prompt-crafter
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
