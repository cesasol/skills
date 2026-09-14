---
name: code-quality
description: >
  Use this skill to audit, install, or repair the deterministic quality baseline of any repository, in any
  language: prek git hooks, a justfile entrypoint, a blocking pipeline on GitLab CI or GitHub Actions, and the
  formatter, linter, and type checker each detected stack needs (ruff and ty for Python; oxlint, eslint, and tsc
  for TypeScript or JavaScript; golangci-lint for Go; clippy and rustfmt for Rust; shellcheck, rumdl, hadolint,
  and gitleaks across the tree). Use when the request is to set up linting, add pre-commit hooks, wire a quality
  stage into CI, standardize tooling across a polyglot or monorepo codebase, or verify that static analysis
  really blocks a merge.
compatibility: Requires Git and a POSIX shell. Assumes uv (uvx), just, and the toolchain of each detected language. Every hook and job must run non-interactively.
metadata:
  writing-style: Chicago Manual of Style
  baseline: prek, just, pipeline, formatter, linter, type checker, secret scanning
---

# code-quality — The Deterministic Quality Baseline

Deterministic analysis is the cheapest defect removal available. A formatter, a linter, a type checker, and a secret scanner reach the same verdict on every machine and on every commit, and together
they intercept a large share of what a codebase would otherwise ship — the working estimate behind this skill is at least half of the defects a team would meet in review, in staging, or in production.
Tests and human review are for the remainder, and they work better when the mechanical defects are already gone.

This skill is language agnostic but deliberately opinionated. A repository either meets the baseline below or records, in the repository itself, why it does not.

## The Baseline

| Layer | Requirement | Canonical command |
| --- | --- | --- |
| Hook runner | `prek.toml` at the repository root | `uvx prek run --all-files` |
| Task runner | `justfile` with a `ci` recipe | `just ci` |
| Pipeline | `.gitlab-ci.yml` or `.github/workflows/ci.yml` with a quality stage that blocks the merge | pipeline calls `just ci` |
| Config | Dedicated tool files; no block over forty lines inside a shared manifest | `bash scripts/audit.sh .` |
| Format | One formatter per language, autofix locally and check-only in CI | `just fmt`, `just fmt-check` |
| Lint | One linter per language, warnings treated as errors | `just lint` |
| Types | A type checker for every typed language, blanket suppressions disabled | `just typecheck` |
| Tests | One test command that reports coverage | `just test` |
| Secrets | A `gitleaks` hook, plus the platform's own secret detection | `uvx prek run gitleaks --all-files` |

Defaults by stack: **Python** uses uv, ruff, ty, and pytest; **TypeScript or JavaScript** uses pnpm, oxlint, tsc, and vitest; **Go** uses golangci-lint; **Rust** uses rustfmt, clippy, and nextest;
**shell** uses shellcheck and shfmt; **Markdown** uses rumdl; **containers** use hadolint.

## Workflow

1. Audit before touching anything. Run `scripts/audit.sh` (see below) and treat its gap list as the work order.
2. Read the reference for every stack the audit detected, plus [references/ci-pipelines.md](references/ci-pipelines.md).
3. Ask only what the audit cannot settle: which package manager is authoritative, whether an existing linter may be replaced, and which branch protects production. Keep it to two to four questions.
4. Apply the changes in bootstrap order (below), copying from `assets/` and adapting to the repository's real commands.
5. Verify by running each new command, then `uvx prek run --all-files`, then `just ci`. A baseline that was never executed is not a baseline.
6. Report the gaps closed, the gaps deliberately left open, and the exact commands that now gate a merge.

## Run the Audit

Resolve `scripts/audit.sh` against this skill's directory, not the audited repository:

```bash
# Human-readable gap report for the current repository.
bash scripts/audit.sh .

# Machine-readable findings, for planning the work order.
bash scripts/audit.sh --json /path/to/repo

# Fail on warnings too, which is the right setting for a repository that already met the baseline once.
bash scripts/audit.sh --strict .
```

The script never writes to the target repository. It reads the tracked file list, detects each stack (including nested packages in a monorepo), and reports three statuses: `ok`, `gap` for a missing
part of the baseline, and `warn` for a weaker-than-preferred choice. It exits `0` when no gap remains, `1` when a gap remains or `--strict` finds a warning, and `2` on a usage error.

### Worked Example

A Python service with a Nuxt client, audited before any change:

```text
Quality baseline audit — /srv/example
Stacks detected: python, typescript, shell

universal
  [ok]   hook runner        prek.toml
  [gap]  ci recipe          justfile has no `ci` recipe
  [gap]  pipeline gate      the pipeline never runs `prek run --all-files` or `just ci`
python
  [ok]   lint + format      ruff configured
  [gap]  type checker       no ty.toml, no [tool.ty], and no other type-checker config
typescript (web)
  [gap]  linter             no oxlint and no eslint configuration
  [warn] strict mode        web/tsconfig.json inherits its base config; confirm strict is on

6 ok, 4 gaps, 1 warnings
```

The resulting work order is the gap list, in bootstrap order: add the `ci` recipe, add `ty.toml` and `.oxlintrc.json`, confirm `strict` in the inherited tsconfig, then make the pipeline call
`uvx prek run --all-files` and `just ci`. Re-run the audit; it must end with `0 gaps` before the work is reported as done.

## Stack Detection

| Signal | Stack | Reference |
| --- | --- | --- |
| `pyproject.toml`, `*.py` | Python | [references/python.md](references/python.md) |
| `package.json`, `*.ts`, `*.tsx`, `*.vue`, `*.svelte` | TypeScript or JavaScript | [references/typescript.md](references/typescript.md) |
| `go.mod` | Go | [references/go-rust.md](references/go-rust.md) |
| `Cargo.toml` | Rust | [references/go-rust.md](references/go-rust.md) |
| `*.sh`, `Dockerfile`, `Containerfile`, `*.md`, `*.yml` | Shell, containers, docs, CI config | [references/cross-cutting.md](references/cross-cutting.md) |
| `.gitlab-ci.yml`, `.github/workflows/` | Pipeline platform | [references/ci-pipelines.md](references/ci-pipelines.md) |

A repository with several signals is polyglot, not ambiguous. Configure every detected stack; do not make the user choose one.

## Critical Rules for Agents

1. **Audit first, edit second.** Never add a tool before the audit shows the gap it fills. Adopting the repository's existing equivalent tool beats installing a second one.
2. **One command, three callers.** The developer, the hook, and the pipeline must invoke the same `just` recipe. Divergence between local checks and CI is the failure this baseline exists to prevent.
3. **Pin every version.** Pin hook revisions in `prek.toml`, dependencies in a lockfile, and toolchains in `.python-version`, `packageManager`, or `rust-toolchain.toml`. Refresh with
   `prek auto-update`.
4. **A check that cannot fail is not a check.** Never add `|| true`, `continue-on-error: true`, or `allow_failure: true` to a quality job, and never let the pipeline's lint stage be manual.
5. **Warnings are errors.** Configure each linter so a warning exits nonzero: `--max-warnings 0` for oxlint and eslint, `-D warnings` for clippy, `error-on-warning` for ty.
6. **One config per concern, at the root.** A monorepo has exactly one hook config and one shared lint baseline that members extend. Per-package hook configs drift and silently stop running.
7. **Forty lines is the eviction threshold.** A tool's configuration may live in the shared manifest — `pyproject.toml`, `package.json`, `Cargo.toml` — only while it stays small. Once a tool's block
   reaches forty lines, moving it to the tool's own file is a requirement, not a preference.
8. **Fix the code, never the rule.** Do not delete a rule or widen an ignore to make a check pass. When an exception is genuinely right, scope it to the narrowest path and comment the reason.
9. **Keep hooks fast, and push slow work to CI.** Hooks run on staged files and should finish in seconds. Full-tree type checks, test suites, and image scans belong in the pipeline.
10. **Disable blanket type suppressions.** Set `respect-type-ignore-comments = false` for ty, and forbid `@ts-ignore` in favor of the narrower `@ts-expect-error` with a written reason.
11. **Formatting is machine business.** Autofix formatting in the hook, check formatting in CI, and keep it out of review comments entirely.

### When a Config Outgrows Its Host

A manifest describes the project; it is not a settings dump. Past forty lines a tool's block buries the project metadata, produces merge conflicts on every unrelated change, and loses the schema
support and comment style the tool's own format provides. Count the block including its subsection headers and comments, then extract:

| Inline block | Extract to |
| --- | --- |
| `[tool.ruff]` and `[tool.ruff.*]` | `ruff.toml` |
| `[tool.ty]` | `ty.toml` |
| `[tool.pytest.ini_options]` | `pytest.ini` |
| `[tool.coverage.*]` | `.coveragerc` |
| `"eslintConfig"` | `eslint.config.js` |
| `"prettier"` | `.prettierrc.json` |
| `"jest"` | `jest.config.ts` |
| `"scripts"` | `just` recipes, with thin `package.json` wrappers only where a tool demands them |

Dependency and packaging tables — `[project]`, `[tool.uv]`, `[tool.poetry]`, `dependencies` — stay in the manifest at any size, because that is the manifest's own job. `scripts/audit.sh` reports an
oversized block as a gap, naming the block, its line count, and its destination.

## Bootstrap Order

Apply in this order, because each step depends on the previous one:

1. **`justfile`** — Define `ci`, `fmt`, `fmt-check`, `lint`, `typecheck`, `test`, `hooks`, and `setup` from [assets/justfile.template](assets/justfile.template). These names are the contract
   everything else calls.
2. **Tool configs** — Add the per-stack configuration: ruff and ty for Python, oxlint and tsconfig for TypeScript, golangci-lint for Go, rustfmt and clippy for Rust, rumdl for Markdown. Start inside
   the manifest only for a handful of settings; anything larger starts in its own file.
3. **Lockfiles and toolchain pins** — Generate `uv.lock` or `pnpm-lock.yaml`, and pin the interpreter or toolchain version.
4. **`prek.toml`** — Start from [assets/prek.toml.template](assets/prek.toml.template), keep only the hooks that match the detected stacks, then run `uvx prek install` and `uvx prek run --all-files`.
5. **Pipeline** — Add a `quality` stage that runs `uvx prek run --all-files` and `just ci`, using [assets/gitlab-ci.yml.template](assets/gitlab-ci.yml.template) or
   [assets/github-ci.yml.template](assets/github-ci.yml.template).
6. **Documentation** — Record the baseline and its exceptions in `README.md` or `AGENTS.md`, so the next contributor sees the contract before the pipeline teaches it to them.

## Monorepos and Polyglot Repositories

- Keep one `prek.toml`, one `rumdl.toml`, and one shared lint baseline at the root. Members extend the shared configuration; they never restate it.
- Keep a root `justfile` for cross-cutting recipes and a per-package `justfile` for package-local work. The root `ci` recipe is what the pipeline calls.
- Scope CI jobs with `rules:changes` (GitLab) or `paths` (GitHub Actions) so an unrelated package does not pay for another package's test suite. Lint and secret scanning still run across the whole
  tree.
- Run the audit from the repository root. It reports each nested package separately and stays quiet about configuration a package correctly inherits from an ancestor.

## Documented Exceptions

An exception is legitimate only when it is narrow, commented, and visible in review. Write it in the tool's own configuration, never as a blanket ignore:

```toml
# ty.toml — tests call Settings() with no arguments because monkeypatch supplies
# the environment at runtime; production startup still validates every field.
[[overrides]]
include = ["**/tests/**"]

[overrides.rules]
missing-argument = "ignore"
```

Disabling a rule for the whole repository requires the same treatment: a comment that states the rule, the reason, and the condition under which it would be re-enabled.

## Edge Cases, Mistakes, and Failure Handling

- **Legacy repository with thousands of violations.** Do not bulk-disable rules. Land the formatter in one mechanical commit, add the linter with a baseline or a per-directory scope, then tighten it
  in follow-up merge requests. Record the plan in the repository.
- **The hook suite reformats files during CI.** That is a failure, not a nuisance: it means the developer's commit skipped the hooks. Keep the CI job failing and fix the local installation with
  `uvx prek install`.
- **A protected-branch hook breaks the pipeline.** `no-commit-to-branch` fails on `main`. Set `SKIP=no-commit-to-branch` for the CI job instead of removing the hook.
- **Generated code fails the linter.** Exclude the generated path in the tool config and in `prek.toml`, and make the generator's output deterministic; never relax the rule globally.
- **A manifest becomes a config dump.** Extracting a forty-line block is mechanical, but do it in its own commit: the diff is large, and mixing it with behavior changes hides both.
- **Two linters for one language.** Pick one owner per concern. oxlint plus eslint is acceptable only when the project truly needs type-aware rules, and the split must be written down.
- **`just ci` passes locally and fails in CI.** The usual causes are an unpinned tool version, a dirty local cache, or a recipe that depends on the developer's shell. Reproduce with a clean checkout.
- **The audit reports a gap the team rejects.** Record the decision in `README.md` or `AGENTS.md` with the reason. An undocumented gap will be reintroduced by the next agent that runs this skill.

## Output Format for Agent Responses

When finishing code-quality work, report:

- The stacks detected and the audit summary before and after the change.
- Files added or changed, grouped by layer: hooks, recipes, tool configs, and pipeline.
- The exact commands that now gate a merge, and their results (`uvx prek run --all-files`, `just ci`).
- Gaps left open, each with a one-line reason and where the decision is recorded.
