# Go — GitLab CI Reference

Patterns for Go projects using Go modules.
Read `_common.md` for shared patterns.

Source: <https://docs.gitlab.com/ci/yaml/>

## Detection Signals

| File | Stack |
|------|-------|
| `go.mod` | Go modules |
| `go.sum` | Go modules (with checksums) |
| `.golangci.yaml` / `.golangci.yml` | golangci-lint configured |

## Docker Image

`golang:1.23-bookworm` — Debian-based with full toolchain.
`golang:1.23-alpine` — smaller, but may lack CGO deps.

## Cache Strategy

Source: <https://docs.gitlab.com/ci/caching/>

```yaml
.go-cache: &go-cache
  key:
    files: [go.sum]
    prefix: ${CI_COMMIT_REF_SLUG}
  paths:
    - $GOPATH/pkg/mod
    - .go-build-cache
  policy: pull
```

Set `GOPATH: '$CI_PROJECT_DIR/.go'` and `GOCACHE: '$CI_PROJECT_DIR/.go-build-cache'` in variables.

## Download Job

```yaml
variables:
  GOPATH: '$CI_PROJECT_DIR/.go'
  GOCACHE: '$CI_PROJECT_DIR/.go-build-cache'
  GO_VERSION: '1.23'

download:
  stage: install
  image: golang:${GO_VERSION}-bookworm
  cache:
    <<: *go-cache
    policy: pull-push
  script:
    - go mod download
    - go mod verify
```

## Lint Job

```yaml
lint:
  stage: quality
  image: golang:${GO_VERSION}-bookworm
  needs: [download]
  cache:
    <<: *go-cache
  script:
    - go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
    - golangci-lint run ./...
```

## Test Job

Source: <https://docs.gitlab.com/ci/testing/unit_test_reports/>

```yaml
test:
  stage: test
  image: golang:${GO_VERSION}-bookworm
  needs: [download]
  cache:
    <<: *go-cache
  script:
    - go test -race -coverprofile=coverage.out ./...
    - go tool cover -func=coverage.out
  coverage: '/total:\s+\(statements\)\s+([\d.]+)%/'
  artifacts:
    when: always
    expire_in: 1 week
    paths: [coverage.out]
```

## Build Job

```yaml
build:
  stage: build
  image: golang:${GO_VERSION}-bookworm
  needs: [download, lint, test]
  cache:
    <<: *go-cache
  script:
    - go build -ldflags="-s -w" -o bin/ ./...
  artifacts:
    expire_in: 1 day
    paths: [bin/]
```

## Recommended Stage Order

```yaml
stages:
  - install   # go mod download
  - quality   # golangci-lint
  - test
  - build
  - deploy
```
