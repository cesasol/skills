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

Use `prek` to make local Git hooks and CI quality gates fast, reproducible, and pre-commit-compatible. It can use native `prek.toml` configuration or existing `.pre-commit-config.yaml` files.

## Workflow

1. Inspect the repository for existing hook config: `prek.toml`, `.pre-commit-config.yaml`, CI jobs, `justfile`, and README setup notes.
2. Preserve the existing config format unless the user asks to migrate. Use `prek.toml` for new projects.
3. Prefer hooks that call stable project commands such as `just lint-md` or `just ci` rather than duplicating long shell snippets.
4. Validate the config after editing, then run the changed hook or `prek run --all-files` when safe.
5. Report hook IDs changed, commands run, and whether hooks modified files.

## Critical Rules for Agents

1. **Run hooks on all files in CI.** Use `prek run --all-files` so CI checks the full repository, not only staged changes.
2. **Use `prek run` locally for staged changes.** That mirrors normal pre-commit behavior.
3. **Validate config after editing.** Run `prek validate-config prek.toml` or validate the selected config file.
4. **Use first-party hook repos when available.** Prefer maintained upstream hook repositories for standard tools (for example Ruff and rumdl) instead of wrapping those tools in local hooks.
5. **Prefer local hooks for project recipes.** Use `repo = "local"` when invoking `just`, tests, or other repo-owned commands that do not have a suitable first-party hook.
6. **Keep hooks non-interactive.** Git hooks and CI must not prompt for input, open editors, or require TTY workflows.

## Install

Use the project's existing install method when present. This repository prefers `uvx` for one-off execution and `uv tool install prek` for persistent local installs.

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

Use `prek.toml` for new projects unless the repository already has `.pre-commit-config.yaml`. If both exist, ask which one should be the source of truth before editing.

### Suggested default `prek.toml`

Start with this repo's fast hygiene baseline: builtin hooks for whitespace, syntax, merge safety, executable-bit checks, and basic secret/large-file protection. Add project-specific local hooks after
this baseline.

```toml
# Configuration file for `prek`, a git hook framework written in Rust.
# See https://prek.j178.dev for more information.
#:schema https://www.schemastore.org/prek.json

# Builtin hooks run as fast Rust-native implementations bundled in prek.
[[repos]]
repo = "builtin"
hooks = [
  # Whitespace & EOL hygiene
  { id = "trailing-whitespace", args = ["--markdown-linebreak-ext=md"] },
  { id = "end-of-file-fixer" },
  { id = "mixed-line-ending", args = ["--fix=lf"] },

  # Syntax validation for config-as-code
  { id = "check-yaml" },
  { id = "check-json" },
  { id = "check-json5" },
  { id = "check-toml" },
  { id = "check-xml" },

  # Merge / VCS safety
  { id = "check-merge-conflict" },
  { id = "check-case-conflict" },
  { id = "no-commit-to-branch" },

  # Executable scripts
  { id = "check-shebang-scripts-are-executable" },
  { id = "check-executables-have-shebangs" },

  # Secrets / large files
  { id = "detect-private-key" },
  { id = "check-added-large-files", args = ["--maxkb=512"] },
]

[[repos]]
repo = "https://github.com/gitleaks/gitleaks"
rev = "v8.30.1"
hooks = [{ id = "gitleaks" }]
```

### First-party tool hooks

When a tool provides an official or first-party pre-commit hook repo, use that hook directly instead of a `repo = "local"` wrapper. This keeps hook installation, filenames, and entrypoints aligned
with the tool maintainer's expectations.

For Python projects, use Ruff's hook repo for linting and formatting:

```toml
[[repos]]
repo = "https://github.com/astral-sh/ruff-pre-commit"
rev = "v0.15.12"
hooks = [
  { id = "ruff-check" },
  { id = "ruff-format" },
]
```

For Markdown projects, use rumdl's hook repo and pair it with `.rumdl.toml`:

```toml
[[repos]]
repo = "https://github.com/rvben/rumdl-pre-commit"
rev = "v0.1.91"
hooks = [
  { id = "rumdl" },
  { id = "rumdl-fmt" },
]
```

### Project-specific local hooks

Add local hooks for repo-owned commands when no first-party hook fits:

```toml
[[repos]]
repo = "local"
hooks = [
  { id = "lint-markdown", name = "Lint Markdown", language = "system", entry = "just lint-md", files = "\\.md$" },
  { id = "validate", name = "Validate project", language = "system", entry = "just ci", pass_filenames = false },
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

## Gotchas and common mistakes

- **Mistake: relying on staged-file hooks in CI.** Always use `--all-files` in CI.
- **Mistake: duplicate hook definitions.** prek discovers one config per directory; keep one source of truth.
- **Failure: hooks cannot find tools.** Install tools before `prek run` or make hooks call a `just` recipe that installs/checks prerequisites.
- **Failure: hook changes files.** Re-run the hook, inspect the diff, and commit the formatted result.
- **Mistake: making hooks interactive.** Hooks must not prompt, open editors, or depend on a TTY.
- **Mistake: wrapping standard tools in local hooks when first-party hook repos exist.** Use the tool-maintained hook repo for Ruff, rumdl, and similar tools.
- **Mistake: hiding complex logic in hook entries.** Put reusable project-specific logic in `just` recipes or scripts and call them from a local hook.

## Output Format for Agent Responses

When completing prek work, report:

- Config files changed.
- Hook IDs added or changed.
- Whether `prek run --all-files` passed.
- Any hook that modified files or still fails.
