---
name: just
description: >
  Use this skill when creating, editing, running, or troubleshooting justfiles for
  the just command runner. Apply it when users ask for project command recipes,
  reproducible developer workflows, CI entrypoints, task aliases, or replacing
  ad-hoc shell snippets with documented just recipes.
compatibility: Requires the just CLI; install with cargo, Homebrew, npm, uv, conda, Nix, Snap, Winget, or the official installer/action.
---

# just — Command Runner

Use `just` to make project commands discoverable, reproducible, and easy for humans, agents, and CI to run. It is not a build system; recipes run when invoked and do not track file timestamps like
Make.

## Workflow

1. Inspect existing project commands first: `justfile`, `package.json`, `pyproject.toml`, `Makefile`, CI config, scripts, and README snippets.
2. Add or update recipes around commands the project already uses; avoid inventing a new toolchain.
3. Keep public recipes documented and stable because CI and agents will depend on them.
4. Run `just --fmt` when supported, then run `just --list` and the changed recipes or `just ci` when safe.
5. Report the recipe names changed and which recipe CI should call.

## Critical Rules for Agents

1. **Make `just --list` useful.** Add comments for public recipes so humans and agents can discover commands.
2. **Use one CI recipe.** Prefer `just ci` as the single entrypoint for GitHub, GitLab, and local full verification.
3. **Keep recipes non-interactive by default.** Interactive prompts are poor CI and agent workflows; require explicit confirmation recipes for destructive actions.
4. **Use private helper recipes.** Prefix helpers with `_` or mark them private so `--list` stays focused.
5. **Format the justfile.** Run `just --fmt` after editing when the installed just version supports it.

## Install

Use the project's existing install path when present. Otherwise prefer the official installer in CI and the user's package manager locally.

```bash
# official installer
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/bin

# cargo / Homebrew / uv / npm
cargo install just
brew install just
uv tool install rust-just
npm install -g rust-just
```

## Core Commands

```bash
just                         # run the default recipe
just --list                  # list recipes with comments
just --summary               # print recipe names only
just --show <recipe>         # show a recipe body
just --evaluate              # print evaluated variables
just --fmt                   # format the justfile
just --dry-run <recipe>      # show commands without executing
just <recipe> <args>         # run a recipe with arguments
```

## justfile Best Practices

Start with a small spine and add project-specific commands as needed:

```make
set shell := ["bash", "-uc"]

# Show available recipes
default:
  just --list

# Run all CI checks
ci: lint test

# Run linters
lint: lint-md

# Lint Markdown
lint-md:
  rumdl check .

# Run tests
test:
  python -m unittest discover -s tests -v

# Private helper, hidden by convention
_ensure-clean:
  git diff --quiet
```

## Gotchas and common mistakes

- **Mistake: treating just like Make.** just recipes do not skip work because outputs are newer than inputs.
- **Mistake: hiding required tools in undocumented shell snippets.** Put shared commands in named recipes.
- **Failure: recipe works locally but not in CI.** Avoid shell aliases, local-only environment, and interactive commands.
- **Failure: commands run from an unexpected directory.** just searches upward for a justfile; use explicit paths when recipes depend on location.
- **Mistake: putting secrets in recipes.** Recipes are committed to the repo; read secrets from environment variables or secret managers.
- **Mistake: making `ci` interactive or destructive.** `just ci` should be safe to run repeatedly in CI and by agents.

## Output Format for Agent Responses

When completing just work, report:

- Recipes added or changed.
- Which recipe CI should call.
- Commands run and whether they passed.
- Any recipe that is intentionally local-only or destructive.
