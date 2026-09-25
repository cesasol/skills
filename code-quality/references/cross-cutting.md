# Cross-Cutting Checks — Shell, Markdown, YAML, Containers, and Secrets

These checks apply to every repository regardless of its main language. They are cheap, they never need a project environment, and they catch the defects that language linters never see.

Every snippet below is `prek.toml` syntax. For hook mechanics, stages, and migration from `.pre-commit-config.yaml`, use the **prek** skill; for Markdown rules, the **rumdl** skill.

## Secrets

Secret scanning is the one check that must exist even in a repository with no code, because a leaked credential cannot be un-leaked.

```toml
[[repos]]
repo = "https://github.com/gitleaks/gitleaks"
rev = "v8.30.1"
hooks = [{ id = "gitleaks" }]
```

Pair the hook with the platform's own scanner — GitLab's `Secret-Detection.gitlab-ci.yml` template, or GitHub's secret scanning and push protection — because the hook only sees what the developer
commits locally. When a secret does land, rotate it first and scrub history second; a deleted commit is still in every clone.

## Shell

```toml
[[repos]]
repo = "https://github.com/koalaman/shellcheck-precommit"
rev = "v0.11.0"
hooks = [{ id = "shellcheck" }]

[[repos]]
repo = "https://github.com/scop/pre-commit-shfmt"
rev = "v3.14.1-1"
hooks = [{ id = "shfmt", args = ["-w", "-s"] }]
```

Conventions that make shell reviewable:

- Start every script with `#!/usr/bin/env bash` and `set -euo pipefail`.
- Quote every expansion. ShellCheck's SC2086 is right essentially always.
- Keep scripts in `scripts/`, make them executable, and call them from a `just` recipe rather than inlining logic in CI YAML. `shfmt -w -s` belongs in `just fix`, `shfmt -d` in `just fmt-check`.
- `set -o pipefail` plus `grep -q` on a large stream produces a false negative, because the writer dies of SIGPIPE. Read from a file or use a here-string instead of a pipe.

## Markdown

rumdl is the fast Markdown linter and formatter. One `rumdl.toml` at the root governs the repository, including documentation, prompts, and agent files. The **rumdl** skill covers the rules, the
presets, and migration from markdownlint.

```toml
#:schema https://raw.githubusercontent.com/rvben/rumdl/refs/heads/main/rumdl.schema.json

[global]
disable = ["MD041"]
respect-gitignore = true
exclude = [".claude", ".pi", ".opencode", "fixtures"]
extend-enable = ["MD060"]

[MD013]
line-length = 200
code-blocks = false
tables = false
reflow = true

[MD029]
style = "ordered"

[MD033]
allowed_elements = ["br", "details", "summary"]
```

```toml
[[repos]]
repo = "https://github.com/rvben/rumdl-pre-commit"
rev = "v0.2.73"
hooks = [
  { id = "rumdl" },
  { id = "rumdl-fmt" },
]
```

Exclude agent working directories and vendored content: they contain transient text that should not define the repository's documentation style.

In the justfile, `rumdl check` is the gate and `rumdl check --fix` is the repair. Never gate on `rumdl fmt`: it applies changes and exits zero, so it can only pass.

```make
lint:
    uvx rumdl check .

fix:
    uvx rumdl check --fix .
```

## YAML and Pipeline Config

```toml
[[repos]]
repo = "https://github.com/adrienverge/yamllint"
rev = "v1.38.0"
hooks = [{ id = "yamllint", args = ["--strict"] }]

[[repos]]
repo = "https://github.com/rhysd/actionlint"
rev = "v1.7.12"
hooks = [{ id = "actionlint" }]
```

- `actionlint` validates GitHub Actions workflows, including shell inside `run:` steps, which is where most workflow bugs hide.
- GitLab CI has no offline equivalent. Validate with the project's CI Lint endpoint (`glab ci lint`) before pushing a pipeline change.
- Prefer the prek builtin `check-yaml` hook for syntax and reserve yamllint for style, so failures are unambiguous.

## Containers

```toml
[[repos]]
repo = "https://github.com/hadolint/hadolint"
rev = "v2.15.1"
hooks = [{ id = "hadolint-docker" }]
```

Use the `hadolint-docker` hook when the runner has Docker or Podman, and `hadolint` when the binary is installed. Podman-based repositories name their files `Containerfile`; add
`files = "(Containerfile|Dockerfile)[^/]*$"` so the hook still matches.

Image scanning (Trivy, Grype) belongs in the pipeline after the build, not in a commit hook.

## Spelling and Hygiene

```toml
[[repos]]
repo = "https://github.com/crate-ci/typos"
rev = "v1.50.1"
hooks = [{ id = "typos" }]
```

`typos` is low noise and catches misspellings in identifiers and documentation alike. Add a `_typos.toml` for domain words rather than disabling the hook.

The prek builtin hooks cover the rest of the hygiene layer at effectively zero cost: `trailing-whitespace`, `end-of-file-fixer`, `mixed-line-ending`, `check-yaml`, `check-json`, `check-toml`,
`check-merge-conflict`, `check-case-conflict`, `check-added-large-files`, `check-shebang-scripts-are-executable`, `detect-private-key`, and `no-commit-to-branch`.

## EditorConfig

`.editorconfig` is the one setting editors honor without a plugin. Keep it consistent with the formatters, never in competition with them:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4

[*.{md,markdown}]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

## Failure Modes

- **The secret scanner fires on a test fixture.** Move the fixture value to an obvious dummy, or add a narrowly scoped allowlist entry with a comment. Never disable the hook.
- **rumdl reformats a file the team hand-formatted.** Encode the intent in `rumdl.toml` (line length, table style, allowed HTML) so the formatter and the team agree.
- **yamllint fights the pipeline's own style.** Relax the specific rule (usually `line-length` or `truthy`) in `.yamllint`, not the whole hook.
- **hadolint fails on a multi-stage build the team wants.** Pin the rule exception with `# hadolint ignore=DL3008` on the line above, which keeps the exception visible in review.
- **Hooks pass locally but CI finds violations.** CI runs `--all-files`; the developer's run only saw staged files. That difference is intentional — fix the findings.
