# Rust — GitLab CI Reference

Patterns for Rust projects using Cargo.
Read `_common.md` for shared patterns.

Source: <https://docs.gitlab.com/ci/yaml/>

## Detection Signals

| File | Stack |
|------|-------|
| `Cargo.toml` | Rust project |
| `Cargo.lock` | Rust project (binary/app) |
| `rust-toolchain.toml` | pinned Rust toolchain |

## Docker Image

`rust:1.82-bookworm` — Debian-based with full toolchain.
`rust:1.82-alpine` — smaller, but CGO/musl differences apply.

## Cache Strategy

Source: <https://docs.gitlab.com/ci/caching/>

```yaml
variables:
  CARGO_HOME: '$CI_PROJECT_DIR/.cargo'
  RUST_VERSION: '1.82'

.cargo-cache: &cargo-cache
  key:
    files: [Cargo.lock]
    prefix: ${CI_COMMIT_REF_SLUG}
  paths:
    - .cargo/registry
    - .cargo/git
    - target/
  policy: pull
```

## Quality Jobs (parallel)

```yaml
clippy:
  stage: quality
  image: rust:${RUST_VERSION}-bookworm
  cache:
    <<: *cargo-cache
    policy: pull-push
  script:
    - cargo clippy --all-targets --all-features -- -D warnings

fmt:
  stage: quality
  image: rust:${RUST_VERSION}-bookworm
  cache:
    <<: *cargo-cache
  script:
    - cargo fmt --all -- --check
```

## Test Job

Source: <https://docs.gitlab.com/ci/testing/unit_test_reports/>

```yaml
test:
  stage: test
  image: rust:${RUST_VERSION}-bookworm
  cache:
    <<: *cargo-cache
  script:
    - cargo test --all-features 2>&1 | tee test-output.txt
  artifacts:
    when: always
    expire_in: 1 week
    paths: [test-output.txt]
```

## Build Job (release)

```yaml
build:
  stage: build
  image: rust:${RUST_VERSION}-bookworm
  needs: [clippy, fmt, test]
  cache:
    <<: *cargo-cache
  script:
    - cargo build --release
  artifacts:
    expire_in: 1 day
    paths: [target/release/]
```

## MUSL Static Binary (optional)

For fully static binaries deployable anywhere:

```yaml
build:musl:
  stage: build
  image: rust:${RUST_VERSION}-bookworm
  needs: [clippy, fmt, test]
  cache:
    <<: *cargo-cache
  before_script:
    - rustup target add x86_64-unknown-linux-musl
    - apt-get update -qq && apt-get install -y musl-tools
  script:
    - cargo build --release --target x86_64-unknown-linux-musl
  artifacts:
    expire_in: 1 day
    paths: [target/x86_64-unknown-linux-musl/release/]
```

## Recommended Stage Order

```yaml
stages:
  - quality   # clippy + fmt in parallel
  - test
  - build
  - deploy
```
