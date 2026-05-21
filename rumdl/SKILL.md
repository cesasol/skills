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

Use `rumdl` to keep Markdown consistent with fast linting, safe auto-fixes, markdownlint-compatible rules, CI output formats, and project-local configuration.

## Workflow

1. Inspect existing Markdown config first: `.rumdl.toml`, `rumdl.toml`, `.markdownlint*`, CI config, prek hooks, and just recipes.
2. Preserve the project's style choices. Do not enable stricter prose wrapping or HTML restrictions unless the user asks.
3. Use `rumdl import` when migrating from markdownlint, then make `.rumdl.toml` the source of truth.
4. Run `rumdl check` first for audits and verification. Run `rumdl check --fix` only when the user wants automatic cleanup; run `rumdl check` again for final verification.
5. Report changed config, files auto-fixed, and any remaining manual issues.

## Critical Rules for Agents

1. **Use `rumdl check` for verification.** It reports violations and exits non-zero when problems remain.
2. **Do not auto-fix unless requested.** Use `rumdl check` for audits and verification; use `rumdl check --fix` only when the user asks for cleanup or approves modifying Markdown files.
3. **Do not use `rumdl fmt` as the only CI gate.** Formatter mode applies fixes and exits successfully; pair it with `check` for enforcement.
4. **Keep configuration local and explicit.** Prefer `.rumdl.toml` in the repository root so agents and CI share the same rules.
5. **Use CI-native output when available.** Prefer `--output-format github` on GitHub Actions and `--output-format gitlab` on GitLab when running rumdl directly.

## Install

Use the project's existing install method when present. In this repository, prefer `uvx` for one-off execution or `uv tool install` for a persistent user tool:

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

### Suggested default `.rumdl.toml`

This repo's default is optimized for agent-readable Markdown: prose can remain long enough to avoid token-heavy hard wrapping, but extremely long lines are reflowed. MD060 table formatting is enabled
because skills such as `docs-layout` generate Markdown tables that should be predictable.

```toml
[global]
# Respect .gitignore so generated artifacts, dependency directories, and local
# build outputs stay out of Markdown checks without duplicating ignore patterns.
respect-gitignore = true

# Exclude agent-owned working directories. These paths may contain transient
# prompts, downloaded references, generated scratch files, or third-party content
# that should not define the repository's Markdown style. Add new agent runtime
# directories here when they appear.
exclude = [
  ".claude",
  ".pi",
  ".opencode",
  ".commandcode",
  ".sisyphus",
]

# Enable useful opt-in consistency checks. MD060 keeps tables predictable,
# which matters because skills such as docs-layout generate Markdown tables.
extend-enable = [
  "MD060",
]

# Agent-facing prose should stay mostly unwrapped, but very long prose lines are
# still hard to review. Let rumdl reflow normal paragraphs at a generous width,
# while leaving tables alone because MD060 owns table formatting.
[MD013]
line-length = 200
code-blocks = true
tables = false
headings = true
reflow = true

# Ordered lists should count up explicitly. This makes generated plans,
# procedures, and docs-layout outputs easier to review because skipped or
# duplicated steps are visible in diffs instead of hidden by lazy numbering.
[MD029]
style = "ordered"

# Allow only the small set of inline HTML elements used intentionally in skill
# docs. Broader HTML should be justified locally rather than allowed globally.
[MD033]
allowed_elements = ["br", "details", "summary"]

# Project documentation may use MkDocs-style Markdown features. Skill files stay
# on the standard flavor unless they opt into a local config later.
[per-file-flavor]
"docs/**/*.md" = "mkdocs"
```

Adjust this default only when the project has explicit Markdown style requirements.

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

### prek

When using prek, prefer rumdl's first-party hook repo and pair it with `.rumdl.toml`:

```toml
[[repos]]
repo = "https://github.com/rvben/rumdl-pre-commit"
rev = "v0.1.91"
hooks = [
  { id = "rumdl" },
  { id = "rumdl-fmt" },
]
```

## Gotchas and common mistakes

- **Mistake: running only `rumdl fmt` in CI.** Use `rumdl check` because CI should fail when violations remain.
- **Mistake: leaving markdownlint config drift.** Use `rumdl import` once, then keep `.rumdl.toml` as the source of truth.
- **Failure: generated or vendored files cause noise.** Add them to `exclude` instead of weakening rules globally.
- **Failure: long prose lines are intentional.** Configure MD013 explicitly rather than relying on defaults; this repo uses a generous 200-character line length with paragraph reflow.
- **Mistake: imposing narrow prose wrapping for agent-facing docs without asking.** Hard wrapping can increase token overhead and noisy diffs.
- **Mistake: weakening rules globally for generated/vendor docs.** Exclude generated paths instead.

## Output Format for Agent Responses

When completing rumdl work, report:

- Config files changed.
- Commands run and whether they passed.
- Files auto-fixed, if any.
- Remaining manual Markdown issues, if any.
