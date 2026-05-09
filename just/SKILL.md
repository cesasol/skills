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

just is a command runner for project recipes. It is not a build system; recipes run when invoked and do not track file timestamps like Make.

## Critical Rules for Agents

1. **Make `just --list` useful.** Add comments for public recipes so humans and agents can discover commands.
2. **Use one CI recipe.** Prefer `just ci` as the single entrypoint for GitHub, GitLab, and local full verification.
3. **Keep recipes non-interactive by default.** Interactive prompts are poor CI and agent workflows; require explicit confirmation recipes for destructive actions.
4. **Use private helper recipes.** Prefix helpers with `_` or mark them private so `--list` stays focused.
5. **Format the justfile.** Run `just --fmt` after editing when the installed just version supports it.

## Install

```bash
# cargo
cargo install just

# Homebrew
brew install just

# official installer
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/bin

# uv / npm
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

## CI Examples

### GitHub Actions

```yaml
- uses: extractions/setup-just@v3
- run: just ci
```

### GitLab CI

```yaml
before_script:
  - curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
script:
  - just ci
```

## Common Mistakes and Failure Handling

- **Mistake: treating just like Make.** just recipes do not skip work because outputs are newer than inputs.
- **Mistake: hiding required tools in undocumented shell snippets.** Put shared commands in named recipes.
- **Failure: recipe works locally but not in CI.** Avoid shell aliases, local-only environment, and interactive commands.
- **Failure: commands run from an unexpected directory.** just searches upward for a justfile; use explicit paths when recipes depend on location.

## Output Format for Agent Responses

When completing just work, report:

- Recipes added or changed.
- Which recipe CI should call.
- Commands run and whether they passed.
- Any recipe that is intentionally local-only or destructive.
