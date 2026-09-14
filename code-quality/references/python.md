# Python — uv, ruff, ty, and pytest

The Python baseline is Astral's toolchain end to end: uv resolves and locks, ruff lints and formats, ty checks types, and pytest runs the suite. One resolver, one linter, one formatter, one type
checker, all pinned.

## Layout

| Concern | File | Notes |
| --- | --- | --- |
| Project metadata | `pyproject.toml` | May also hold `[tool.ruff]` and `[tool.pytest.ini_options]` while each block stays under forty lines. |
| Lock | `uv.lock` | Committed. CI installs with `--frozen`. |
| Interpreter pin | `.python-version` | uv reads it; CI images should match it. |
| Types | `ty.toml` | Keep type-checker settings out of `pyproject.toml` so overrides stay readable. |

Once a tool's block in `pyproject.toml` reaches forty lines — headers and comments included — extraction is mandatory: `[tool.ruff*]` to `ruff.toml`, `[tool.pytest.ini_options]` to `pytest.ini`,
`[tool.coverage.*]` to `.coveragerc`. Rule tables with per-rule justifications reach that size quickly, and they read far better in the tool's own file. `[project]`, `[tool.uv]`, and dependency groups
stay in the manifest regardless of length.

## uv

```bash
uv sync --frozen                                # single project, exact lockfile
uv sync --frozen --all-packages --all-groups    # workspace: every member plus every dev group
uv run --no-sync pytest                         # run against the already-synced environment
uv run --package sigrun pytest                  # run one workspace member from the root
uvx ruff check .                                # one-off tool run, no project install
```

A plain `uv sync` in a workspace root installs only the root project, so the dev group — pytest, ty — is missing. That mismatch is the most common cause of "works locally, fails in CI" for uv
workspaces. Use `--all-packages --all-groups` in CI, then `uv run --no-sync` in each job.

## ruff

One baseline at the root; members extend it and add only their own rules. The example below fits in the manifest; the moment it grows past forty lines it moves to `ruff.toml`, where members point at
it with `extend = "../ruff.toml"`.

```toml
# pyproject.toml (root)
[tool.ruff]
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
ignore = ["E501", "B008"]

[tool.ruff.lint.pyupgrade]
keep-runtime-typing = true
```

```toml
# svc-example/pyproject.toml (member)
[tool.ruff]
extend = "../pyproject.toml"

[tool.ruff.lint]
extend-select = ["C4", "SIM", "TCH"]
```

Rules of thumb:

- `E501` is usually ignored because `ruff format` owns line length; do not also configure a second formatter.
- `B008` is ignored in FastAPI projects, where `Depends()` in a default argument is the intended idiom.
- Promote a member's rule to the root only when every member already passes it.

Commands:

```bash
ruff check .            # lint
ruff check --fix .      # lint and autofix
ruff format .           # format
ruff format --check .   # verify formatting, for CI
```

## ty

ty is Astral's type checker. It is in beta, moves fast, and must be pinned like any other dependency.

```toml
# ty.toml
[environment]
python-version = "3.14"

[terminal]
error-on-warning = true

[analysis]
# A blanket `# type: ignore` must not silence a real error. Fix the type instead.
respect-type-ignore-comments = false

# Tests construct Settings() with no arguments because monkeypatch supplies the
# environment at runtime; production startup still validates every field.
[[overrides]]
include = ["**/tests/**"]

[overrides.rules]
missing-argument = "ignore"
unresolved-attribute = "ignore"
```

```bash
uv run ty check                 # check the project
uv run ty check src             # check one directory
uvx ty check --python .venv     # one-off run against an existing environment
```

Notes:

- ty needs the installed dependencies to resolve imports. Run it after `uv sync`, not before.
- Disable competing checkers in editor configuration when the repository standardizes on ty; two checkers reporting different errors on the same line teaches contributors to ignore both.
- mypy or pyright stays acceptable in a repository already committed to it. Do not run two checkers in CI.

## pytest

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--strict-markers --strict-config"
```

CI should publish coverage in the platform's native format, so the merge request shows it:

```bash
uv run --no-sync pytest --cov=package_name --cov-report=term --cov-report=xml:coverage.xml --junitxml=report.xml
```

## Hooks

```toml
[[repos]]
repo = "https://github.com/astral-sh/ruff-pre-commit"
rev = "v0.16.7"
hooks = [
  { id = "ruff-check", args = ["--fix"] },
  { id = "ruff-format" },
]
```

Type checking belongs in a local hook or in CI, not in an isolated hook environment, because ty needs the project's real dependency set:

```toml
[[repos]]
repo = "local"
hooks = [
  { id = "ty", name = "ty check", entry = "uv run ty check", language = "system", types = ["python"], pass_filenames = false },
]
```

Keep that hook only when the project's check finishes in a second or two; otherwise leave type checking to `just typecheck` and the pipeline.

## just Recipes

```make
# Install the whole workspace, including dev tools.
setup:
    uv sync --frozen --all-packages --all-groups

lint:
    uv run ruff check .

fmt:
    uv run ruff format .

fmt-check:
    uv run ruff format --check .

typecheck:
    uv run ty check

test:
    uv run --no-sync pytest
```

## Failure Modes

- **`ty` cannot resolve an import that exists.** The environment is not synced, or ty is pointed at the wrong interpreter. Run `uv sync`, then pass `--python .venv` when invoking ty outside `uv run`.
- **ruff and another formatter disagree.** Remove the other formatter. Black, autopep8, and isort are all subsumed by `ruff format` and the `I` rule set.
- **CI installs a different dependency set than the developer.** Use `--frozen` everywhere, and never regenerate the lockfile inside a CI job.
- **A new ty release adds errors.** That is the checker improving, not a reason to disable it. Pin the version, fix the findings in a dedicated merge request, then bump.
- **Per-member ruff configs drift.** Members must use `extend`; a standalone `[tool.ruff.lint] select` in a member silently overrides the shared baseline.
