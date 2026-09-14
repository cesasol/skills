# Go and Rust — golangci-lint, clippy, and Pinned Toolchains

Both ecosystems ship an official formatter and a dominant linter, so the baseline is short: format in the hook, lint with warnings as errors, and pin the toolchain so CI and the developer compile the
same code.

## Go

### Go Layout

| Concern | File | Notes |
| --- | --- | --- |
| Module | `go.mod` | The `go` directive pins the language version. |
| Lint | `.golangci.yml` | golangci-lint v2 schema. |
| Toolchain | `toolchain` directive in `go.mod` | Keeps CI on the same compiler. |

### golangci-lint

```yaml
# .golangci.yml — golangci-lint v2
version: "2"

linters:
  default: standard
  enable:
    - errcheck
    - govet
    - staticcheck
    - revive
    - bodyclose
    - errorlint
    - gosec
  exclusions:
    rules:
      - path: _test\.go$
        linters: [gosec, errcheck]

formatters:
  enable:
    - gofmt
    - goimports
```

```bash
golangci-lint run                 # lint the module
golangci-lint run --fix           # lint and autofix
golangci-lint fmt                 # format via the configured formatters
go vet ./...                      # cheap sanity pass, already covered by govet
go test ./... -race -cover        # the race detector is not optional in CI
```

### Go Hooks and Recipes

```toml
[[repos]]
repo = "https://github.com/golangci/golangci-lint"
rev = "v2.13.2"
hooks = [
  { id = "golangci-lint-fmt" },
  { id = "golangci-lint" },
]
```

The `golangci-lint` hook lints only what changed (`--new-from-rev HEAD`); the `golangci-lint-full` hook lints everything and belongs in CI.

```make
lint:
    golangci-lint run

fmt:
    golangci-lint fmt

fmt-check:
    test -z "$(gofmt -l .)"

test:
    go test ./... -race -coverprofile=coverage.out
```

### Go Failure Modes

- **The hook passes and CI fails.** The hook used `--new-from-rev`; CI ran the full pass. Keep both, and treat the full pass as authoritative.
- **A linter version bump adds findings.** Pin `rev` and the CI image tag, then take the bump as its own merge request.
- **`gosec` floods the test files.** Exclude by path in `exclusions.rules`, never by disabling the linter globally.
- **Generated code fails.** Mark it with the standard `// Code generated ... DO NOT EDIT.` header; golangci-lint skips it by default.

## Rust

### Rust Layout

| Concern | File | Notes |
| --- | --- | --- |
| Manifest | `Cargo.toml` | Workspace lints live in `[workspace.lints]`. |
| Lock | `Cargo.lock` | Committed, including for libraries, so CI is reproducible. |
| Toolchain | `rust-toolchain.toml` | Pins the channel and the components. |
| Format | `rustfmt.toml` | Optional; defaults are good. |

```toml
# rust-toolchain.toml
[toolchain]
channel = "1.93.0"
components = ["rustfmt", "clippy"]
```

### clippy and rustfmt

```bash
cargo fmt --all -- --check          # formatting gate
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features           # or: cargo nextest run
```

`-D warnings` is the whole point: clippy without it is advisory, and advisory linting decays. The equivalent in the manifest, which also covers editors:

```toml
# Cargo.toml
[workspace.lints.rust]
unsafe_code = "forbid"
unused_must_use = "deny"

[workspace.lints.clippy]
all = { level = "deny", priority = -1 }
unwrap_used = "deny"
expect_used = "warn"
```

Each member then opts in with `[lints] workspace = true`.

### Rust Hooks and Recipes

Rust hooks must run against the project's own toolchain, so define them locally:

```toml
[[repos]]
repo = "local"
hooks = [
  { id = "cargo-fmt", name = "cargo fmt", entry = "cargo fmt --all --", language = "system", types = ["rust"] },
  { id = "cargo-clippy", name = "cargo clippy", entry = "cargo clippy --all-targets --all-features -- -D warnings", language = "system", types = ["rust"], pass_filenames = false },
]
```

```make
lint:
    cargo clippy --all-targets --all-features -- -D warnings

fmt:
    cargo fmt --all

fmt-check:
    cargo fmt --all -- --check

test:
    cargo nextest run --all-features
```

### Rust Failure Modes

- **clippy is slow in the hook.** Move it to `pre-push` or to CI, and keep only `cargo fmt` on commit.
- **CI uses a different compiler than the developer.** `rust-toolchain.toml` is missing, or the CI image overrides it. The file must win.
- **`unwrap_used` breaks the test suite.** Allow it inside `#[cfg(test)]` modules explicitly; do not drop the lint for the crate.
- **A dependency triggers a clippy lint.** Fix the call site; `#[allow(...)]` needs a comment naming the upstream issue.
