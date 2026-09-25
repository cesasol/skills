# just Recipes — The Standard Recipe Set

Recipe names are the repository's public interface. A developer, a prek hook, a pipeline job, and an agent all reach for the same handful of verbs, so those verbs must mean the same thing in every
repository. `just lint` never rewrites a file. `just fix` always does. `just ci` is the whole gate and nothing else.

For the mechanics of writing justfiles (arguments, private recipes, dependencies, `just --fmt`), use the **just** skill. This reference covers only the names and what each one must do.

## The Standard Set

| Recipe | Present when | Writes files | Runs inside `ci` | May block |
| --- | --- | --- | --- | --- |
| `default` | always | no | no | no |
| `ci` | always | no | is the gate | no |
| `lint` | always | no | yes | no |
| `fix` | always | yes | never | no |
| `test` | always | no | yes | no |
| `setup` | always | environment only | no | no |
| `hooks` | always | yes, through autofixing hooks | no | no |
| `fmt` | a formatter exists for any detected stack | yes | no | no |
| `fmt-check` | `fmt` exists | no | yes | no |
| `typecheck` | the language has a checker separate from its compiler | no | yes | no |
| `build` | the repository produces an artifact: wheel, bundle, binary, image | yes, into an ignored path | yes when the artifact ships | no |
| `dev` | the repository runs locally with reload | no | never | yes |
| `start` | the built artifact is runnable the way production runs it | no | never | yes |

`default`, `ci`, `lint`, `fix`, `test`, `setup`, and `hooks` exist in every repository, including a docs-only one. The rest appear when the repository has the thing they act on. Omit a recipe that has
no work rather than defining a stub that prints nothing: a missing recipe fails loudly, and `just --list` stays honest about what the project can do.

## Rules

1. **`lint` is read-only.** A gate that repairs its own input cannot fail. Every linter runs in check mode with warnings as errors, and the fixing variant lives in `fix`.
2. **`fix` is the single autofix door.** It runs every formatter and every linter's `--fix` pass, formatters last so the linter's output gets formatted. It must be idempotent: a second run changes
   nothing.
3. **`fmt` is a subset of `fix`.** Keep `fmt` when formatting alone is useful: a hook, or a large mechanical commit. `fix` may then reuse it through just's subsequent-dependency syntax
   (`fix: && fmt`), which runs the body first and the formatter after, instead of restating the commands.
4. **`ci` composes, it does not implement.** The body of `ci` is a dependency list of check-only recipes. If a command appears in `ci` and nowhere else, it belongs in its own recipe.
5. **`ci` never calls `fix`, `dev`, or `start`.** Those three write files or block forever. A pipeline that autofixes hides the defect it was built to report.
6. **`dev` and `start` are the only long-running recipes.** They may hold the terminal, bind a port, and watch the filesystem. Nothing may depend on them.
7. **`start` runs what production runs.** It executes the built artifact with production settings and no reload. `dev` is the watch loop with debug settings. Keep them separate even when the command
   differs by one flag, because CI and container entrypoints call `start`.
8. **`build` writes only to an ignored path.** `dist/`, `bin/`, `target/`, `.output/`. A build that dirties the working tree breaks the hook suite and the pipeline's clean-tree check.
9. **`setup` is the only recipe allowed to install anything.** Every other recipe assumes `setup` already ran, and fails with the tool's own error when it did not.
10. **The names are fixed; the extras are free.** Add `release`, `migrate`, `docs`, or `bench` as the project needs, but never rename a standard recipe. Use `alias` for shorthand:
    `alias f := fix`.
11. **One process owns `dev` and `start`.** A repository with two runnable processes, such as an API and a web server, gives the bare names to the primary deployable and prefixes the rest:
    `web-dev`, `web-start`, `worker-start`. Never split the meaning instead, as in `dev` for the API and `start` for the web server, because then neither name means what it means everywhere else.
    Once a second process earns its own justfile, its local `dev` and `start` are unambiguous again and the prefixes disappear.
12. **`just --list` is the documentation.** Every standard recipe carries a one-line comment, and helpers are private (`_name`) so the list shows only what a caller should invoke. Only the last
    comment line above a recipe reaches the list, so keep the description to one line and put longer notes in a section header.

## Composition

The usual shape, for a repository with a formatter, a type checker, and tests:

```make
# Everything a merge must satisfy. CI calls exactly this.
ci: fmt-check lint typecheck test

# Every safe automatic repair. `&& fmt` runs the formatter after the body,
# so the linter's rewrites get formatted rather than the reverse.
fix: && fmt
    uv run ruff check --fix .
```

Variants worth knowing:

- The artifact is the deliverable (a library, a container image, a binary): `ci: fmt-check lint typecheck test build`. A package that no longer builds is broken, whatever the tests say.
- The compiler is the type checker (Go, Rust): drop `typecheck` or point it at `go build ./...` or `cargo check`, and say which in a comment.
- Markdown-only repository: `ci: lint test`, where `lint` is rumdl and `test` is whatever validates the content.
- Slow suites: keep `ci` complete and split the pipeline into parallel jobs that call the individual recipes. Never trim `ci` to make it fast; trim the pipeline's critical path.

## Python Library or CLI

```make
ci: fmt-check lint typecheck test

# Lint, read-only. Warnings are errors.
lint:
    uv run ruff check .

# Every automatic repair: lint autofix in the body, formatter after it.
fix: && fmt
    uv run ruff check --fix .

fmt:
    uv run ruff format .

fmt-check:
    uv run ruff format --check .

typecheck:
    uv run ty check

test:
    uv run --no-sync pytest --cov --cov-report=term

# Wheel and sdist into dist/.
build:
    uv build

# The installed console script, as a user would call it.
start *ARGS:
    uv run --no-sync mytool {{ ARGS }}

setup:
    uv sync --frozen --all-groups
    uvx prek install
```

A library has no server to run, so `dev` is optional. Define it only as the watch loop the team actually uses, and name the dependency in a comment, because `pytest-watcher` is not in the default
dependency set:

```make
# Re-run the suite on save. Requires the pytest-watcher dev dependency.
dev:
    uv run --no-sync ptw . -- -x -q
```

## Python Service

```make
ci: fmt-check lint typecheck test

# Reload on save, debug settings, localhost only.
dev:
    uv run --no-sync fastapi dev src/app/main.py

# Production entrypoint. The container image runs this command.
start:
    uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

# The deployable artifact is the image, so build it here.
build:
    podman build --tag ${IMAGE:-app}:dev .
```

`lint`, `fix`, `fmt`, `fmt-check`, `typecheck`, `test`, and `setup` are identical to the library case. Keep `start` free of reload flags and free of `--host 127.0.0.1`: the image entrypoint is the
same line, so a debug flag here becomes a debug flag in production.

## TypeScript or JavaScript Web App

```make
ci: fmt-check lint typecheck test build

lint:
    pnpm exec oxlint --max-warnings 0

fix: && fmt
    pnpm exec oxlint --fix

fmt:
    pnpm exec prettier --write .

fmt-check:
    pnpm exec prettier --check .

# vue-tsc for Vue, svelte-check for Svelte, tsc elsewhere.
typecheck:
    pnpm exec tsc --noEmit

test:
    pnpm exec vitest run --coverage

build:
    pnpm run build

# Dev server with HMR.
dev:
    pnpm run dev

# Serve the build output the way the deployment does.
start:
    node .output/server/index.mjs

setup:
    pnpm install --frozen-lockfile
    uvx prek install
```

Notes:

- `build` belongs in `ci` for an app, because a type-clean project can still fail to bundle.
- A static SPA has no server entrypoint. Use `pnpm exec vite preview` for `start` and say so in the comment, or drop `start` entirely.
- Nuxt projects need `nuxt prepare` before `typecheck` finds the generated types. Put it in `setup`, not in `typecheck`.

## TypeScript Library

Same `lint`, `fix`, `fmt`, `typecheck`, and `test` as the app. The difference is the tail:

```make
ci: fmt-check lint typecheck test build

# Emit the published artifact, types included.
build:
    pnpm run build

# Watch build for consumers linked into another project.
dev:
    pnpm run build --watch
```

A library has no `start`. Publishing is a separate, explicitly named recipe (`release`), never a side effect of `build`.

## Go Service or CLI

```make
# The compiler is the type checker, so `build` carries that duty.
ci: fmt-check lint test build

lint:
    golangci-lint run

fix: && fmt
    golangci-lint run --fix

fmt:
    golangci-lint fmt

fmt-check:
    test -z "$(gofmt -l .)"

test:
    go test ./... -race -coverprofile=coverage.out

build:
    go build -trimpath -o bin/app ./cmd/app

# Rebuild and restart on save. Requires watchexec.
dev:
    watchexec --restart --exts go -- go run ./cmd/app

start: build
    ./bin/app

setup:
    go mod download
    uvx prek install
```

The race detector is not optional in `test`: it is the only cheap way to find the defect class Go is most prone to.

## Rust Binary or Crate

```make
ci: fmt-check lint test build

lint:
    cargo clippy --all-targets --all-features -- -D warnings

fix: && fmt
    cargo clippy --fix --allow-dirty --all-targets --all-features

fmt:
    cargo fmt --all

fmt-check:
    cargo fmt --all -- --check

# Cheaper than a full build when only the types matter.
typecheck:
    cargo check --all-targets --all-features

test:
    cargo nextest run --all-features

build:
    cargo build --release --locked

# Rebuild and rerun on save. Requires cargo-watch.
dev:
    cargo watch -x run

start: build
    ./target/release/app

setup:
    cargo fetch --locked
    uvx prek install
```

A library crate drops `start` and keeps `build` as the packaging gate (`cargo package --locked` when the crate is published).

## Container Image Repository

A repository whose deliverable is the image itself, with little or no application source:

```make
ci: lint build test

lint:
    uvx prek run hadolint-docker --all-files
    uvx rumdl check .

fix:
    uvx rumdl check --fix .

build:
    podman build --tag ${IMAGE:-app}:dev .

# Verify the built image, not the source.
test: build
    podman run --rm ${IMAGE:-app}:dev --version
    trivy image --exit-code 1 --severity HIGH,CRITICAL ${IMAGE:-app}:dev

start:
    podman run --rm --interactive --tty ${IMAGE:-app}:dev
```

`dev` rarely earns its place here. When it does, it is the mounted-source variant of `start`, and the comment must say what it mounts.

## Infrastructure Repository

Ansible playbooks, quadlet units, Kubernetes manifests, Terraform:

```make
# No formatter owns YAML playbooks, so there is no fmt pair here.
ci: lint test

lint:
    uvx ansible-lint
    uvx yamllint --strict .
    uvx rumdl check .

fix:
    uvx ansible-lint --fix
    uvx rumdl check --fix .

# The dry run is the test suite. molecule replaces it when the repo has scenarios.
test:
    uv run ansible-playbook --check --diff site.yml
```

Never name a deploy `start`. `start` implies a local process that a developer can kill; applying infrastructure changes a live system and needs its own guarded recipe:

```make
# Apply to the real environment. Requires an explicit environment argument.
deploy ENV:
    uv run ansible-playbook --inventory "inventories/{{ ENV }}" site.yml
```

## Documentation or Prompt Repository

Markdown, skills, prompts, agent files. Use the **rumdl** skill for the rule configuration this depends on.

```make
ci: lint test

lint:
    uvx rumdl check .

fix:
    uvx rumdl check --fix .

# Whatever validates the content: schema checks, link checks, packaging.
test:
    python3 -m unittest discover -s tests -v

setup:
    uvx prek install
```

`rumdl check` is the gate and `rumdl check --fix` is the repair. Never make `rumdl fmt` the gate: it applies changes and exits zero, so it can only ever pass.

## Polyglot Monorepo

The root justfile owns the contract; each package owns its own commands.

```make
# Packages that carry their own justfile, in dependency order.
PACKAGES := "api web"

ci: fmt-check lint typecheck test

# Fan out one recipe to every package that defines it. A package without that
# recipe is skipped, never stubbed.
_each RECIPE:
    #!/usr/bin/env bash
    set -euo pipefail
    for pkg in {{ PACKAGES }}; do
      just --justfile "${pkg}/justfile" --show '{{ RECIPE }}' >/dev/null 2>&1 || continue
      echo "==> ${pkg}: {{ RECIPE }}"
      just --justfile "${pkg}/justfile" --working-directory "${pkg}" '{{ RECIPE }}'
    done

fmt-check: (_each "fmt-check")
lint: (_each "lint")
typecheck: (_each "typecheck")
test: (_each "test")
build: (_each "build")

# Packages repair their own sources first, then the hook suite covers the
# whole tree: Markdown, YAML, whitespace, and everything no package owns.
fix: (_each "fix")
    uvx prek run --all-files
```

Rules that matter more in a monorepo than anywhere else:

- The pipeline calls the root `ci` and nothing deeper. Path filters decide which jobs run; they never decide which recipe names exist.
- Every package defines the same recipe names, even when a name maps to a different tool. That is the point of the contract.
- Secret scanning, Markdown, and YAML checks run once at the root over the whole tree, never per package.
- A package with no work for a recipe omits it. The root's fan-out probes with `just --show` and skips what is missing, so nobody has to write an empty recipe to keep the loop happy.

## Beyond the Standard

Common additions, and the names to use for them:

| Purpose | Recipe | Notes |
| --- | --- | --- |
| Run every hook over the tree | `hooks` | `uvx prek run --all-files`. See the **prek** skill. |
| Refresh hook revisions | `hooks-update` | `uvx prek auto-update`, then rerun the suite. |
| Report baseline gaps | `audit` | `bash scripts/audit.sh .` |
| Remove build output | `clean` | Only ignored paths. Never `git clean -x` without an argument. |
| Publish | `release` | Separate from `build`, and never a dependency of `ci`. |
| Apply infrastructure | `deploy ENV` | Requires an explicit environment. |
| Database migrations | `migrate`, `migrate-new NAME` | `migrate` is idempotent; the generator is a different recipe. |
| Benchmarks | `bench` | Outside `ci`: too slow and too noisy to gate a merge. |

## Failure Modes

- **CI passes after rewriting the checkout.** A fixing command leaked into `lint` or `ci`. Move it to `fix` and let the job fail.
- **`just ci` blocks forever in the pipeline.** `dev` or `start` became a dependency of a gate recipe, or a recipe reads from stdin. Gate recipes are non-interactive by definition.
- **`start` works locally and the image crashes.** The recipe carried a developer-only flag (reload, `127.0.0.1`, a debug log level). `start` must be the production command, unmodified.
- **`fix` produces a different result on the second run.** The formatter runs before the linter's autofix, so the linter's output is unformatted. Put the formatter last.
- **`build` dirties the working tree.** The output path is not ignored, or a generator writes next to the source. Redirect to an ignored directory and commit the `.gitignore` entry.
- **A recipe exists only in the pipeline's YAML.** The developer cannot reproduce the failure. Every command CI runs is a recipe first.
- **Recipe names drift between packages.** `test:unit` here, `tests` there, `check` somewhere else. Rename to the standard set in one mechanical commit; the pipeline and the hooks then stop
  special-casing.
- **`setup` is required but undocumented, so every recipe fails on a fresh clone.** Name `setup` in the README's first code block, and keep it the only recipe that installs.
