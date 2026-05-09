---
name: prek
description: >
  Use this skill when setting up, running, configuring, or troubleshooting prek,
  the fast pre-commit-compatible Git hook runner. Apply it when users ask for
  pre-commit hooks, prek.toml, .pre-commit-config.yaml compatibility, CI hook
  checks, hook migration, or local quality gates.
compatibility: Requires the prek CLI; this repository prefers uvx or uv tool for installation/execution.
---

# prek — Fast Pre-commit Hook Runner

prek is a fast Git hook manager and pre-commit-compatible runner. It can use native `prek.toml` configuration or existing `.pre-commit-config.yaml` files.

## Critical Rules for Agents

1. **Run hooks on all files in CI.** Use `prek run --all-files` so CI checks the full repository, not only staged changes.
2. **Use `prek run` locally for staged changes.** That mirrors normal pre-commit behavior.
3. **Validate config after editing.** Run `prek validate-config prek.toml` or validate the selected config file.
4. **Prefer local hooks for project recipes.** Use `repo = "local"` when invoking `just`, `rumdl`, tests, or other repo-owned commands.
5. **Keep hooks non-interactive.** Git hooks and CI must not prompt for input, open editors, or require TTY workflows.

## Install

```bash
# uv / uvx
uv tool install prek
uvx prek run --all-files
```

Other ecosystems can install prek with Homebrew, npm, cargo, or the official installer/action when appropriate:

```bash

# Homebrew
brew install prek

# npm
npm install -g @j178/prek

# cargo
cargo install --locked prek
```

## Core Commands

```bash
prek install                         # install Git hook shims
prek install -f                      # replace existing pre-commit shims
prek install --prepare-hooks         # install shims and prepare hook environments
prek prepare-hooks                   # prepare hook environments only
prek run                             # run hooks on staged files
prek run --all-files                 # run hooks on every matching file
prek run <hook-id>                   # run one hook
prek run --dry-run                   # preview execution
prek run --hook-stage pre-push       # run hooks for another hook stage
prek list                            # list configured hooks
prek auto-update                     # update hook revisions
prek validate-config prek.toml       # validate native config
prek cache gc                        # clean old hook environments
```

## Configuration

Use `prek.toml` for new projects unless the repository already has `.pre-commit-config.yaml`.

```toml
[[repos]]
repo = "local"
hooks = [
  { id = "lint-markdown", name = "Lint Markdown", language = "system", entry = "just lint-md", files = "\\.md$" },
  { id = "validate-skills", name = "Validate skills", language = "system", entry = "just validate-skills", files = "(^|/)SKILL\\.md$|^scripts/validate_skills\\.py$|^tests/" },
]
```

Use `.pre-commit-config.yaml` only when compatibility with existing pre-commit tooling is more important than native TOML.

## CI Examples

### GitHub Actions

```yaml
- uses: j178/prek-action@v2
- run: prek run --all-files
```

### Generic CI

```bash
prek run --all-files
```

## Common Mistakes and Failure Handling

- **Mistake: relying on staged-file hooks in CI.** Always use `--all-files` in CI.
- **Mistake: duplicate hook definitions.** prek discovers one config per directory; keep one source of truth.
- **Failure: hooks cannot find tools.** Install tools before `prek run` or make hooks call a `just` recipe that installs/checks prerequisites.
- **Failure: hook changes files.** Re-run the hook, inspect the diff, and commit the formatted result.

## Output Format for Agent Responses

When completing prek work, report:

- Config files changed.
- Hook IDs added or changed.
- Whether `prek run --all-files` passed.
- Any hook that modified files or still fails.
