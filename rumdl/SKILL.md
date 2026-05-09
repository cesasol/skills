---
name: rumdl
description: >
  Use this skill when setting up, running, configuring, or troubleshooting rumdl,
  the fast Markdown linter and formatter. Apply it when users ask to lint Markdown,
  migrate from markdownlint, configure .rumdl.toml, add Markdown checks to CI, or
  fix documentation style failures.
compatibility: Requires the rumdl CLI; this repository prefers uvx or uv tool for installation/execution.
---

# rumdl — Markdown Linting and Formatting

rumdl is a fast Markdown linter and formatter with markdownlint-compatible rules, auto-fixes, CI output formats, and project-local configuration.

## Critical Rules for Agents

1. **Use `rumdl check` for verification.** It reports violations and exits non-zero when problems remain.
2. **Use `rumdl check --fix` for safe auto-fixes.** It fixes what it can and still fails if unfixable issues remain.
3. **Do not use `rumdl fmt` as the only CI gate.** Formatter mode applies fixes and exits successfully; pair it with `check` for enforcement.
4. **Keep configuration local and explicit.** Prefer `.rumdl.toml` in the repository root so agents and CI share the same rules.
5. **Use CI-native output when available.** Prefer `--output-format github` on GitHub Actions and `--output-format gitlab` on GitLab when running rumdl directly.

## Install

In this repository, prefer `uvx` for one-off execution or `uv tool install` for a persistent user tool:

```bash
# uv / uvx
uv tool install rumdl
uvx rumdl check .
```

Other ecosystems can install rumdl with cargo, Homebrew, npm, or the official GitHub Action when appropriate:

```bash

# cargo
cargo install rumdl

# Homebrew
brew install rvben/tap/rumdl

# npm
npm install -g rumdl
```

For GitHub Actions, either call the repository `just` recipes after setting up uv, or use the official action when the project does not standardize on uv:

```yaml
- uses: rvben/rumdl@v0
  with:
    config: .rumdl.toml
    report-type: annotations
```

## Core Commands

```bash
rumdl check .                         # lint all Markdown files under the repo
rumdl check README.md docs/           # lint specific files or directories
rumdl check --fix .                   # auto-fix, then fail if violations remain
rumdl fmt .                           # format only; not sufficient as a CI gate
rumdl init                            # create a default .rumdl.toml
rumdl init --preset google            # initialize from a preset
rumdl config                          # show merged effective configuration
rumdl import .markdownlint.json       # migrate from markdownlint config
rumdl --version                       # verify installation
```

## Configuration

Use `.rumdl.toml` at the repository root unless the project already standardizes on `pyproject.toml` or another supported location.

```toml
exclude = [".git", "node_modules", "vendor", "dist"]
line-length = 120

[MD003]
style = "atx"

[MD013]
line_length = 120

[MD033]
allowed_elements = ["br", "details", "summary"]
```

## CI Examples

### GitHub Actions

```yaml
- uses: rvben/rumdl@v0
  with:
    config: .rumdl.toml
    report-type: annotations
```

### Direct CLI

```bash
rumdl check --output-format github .
rumdl check --output-format gitlab .
```

## Common Mistakes and Failure Handling

- **Mistake: running only `rumdl fmt` in CI.** Use `rumdl check` because CI should fail when violations remain.
- **Mistake: leaving markdownlint config drift.** Use `rumdl import` once, then keep `.rumdl.toml` as the source of truth.
- **Failure: generated or vendored files cause noise.** Add them to `exclude` instead of weakening rules globally.
- **Failure: long prose lines are intentional.** Configure MD013 explicitly rather than relying on defaults.

## Output Format for Agent Responses

When completing rumdl work, report:

- Config files changed.
- Commands run and whether they passed.
- Files auto-fixed, if any.
- Remaining manual Markdown issues, if any.
