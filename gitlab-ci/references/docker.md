# Docker — GitLab CI Reference

Patterns for building and pushing Docker images to GitLab Container Registry.
Read `_common.md` for shared patterns.

Source: <https://docs.gitlab.com/ci/yaml/>
Source: <https://docs.gitlab.com/ci/docker/using_docker_images/>

## Detection Signals

| File | Stack |
|------|-------|
| `Dockerfile` | Docker build |
| `.dockerignore` | Docker build (optimized) |
| `docker-compose.yml` | multi-service setup |

## Docker-in-Docker (DinD) Setup

Source: <https://docs.gitlab.com/ci/docker/using_docker_build/>

```yaml
variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: '/certs'

.docker-base: &docker-base
  image: docker:27
  services:
    - docker:27-dind
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
```

## Image Tagging Strategy

Use predefined CI variables — never hardcode hostnames:
- `$CI_REGISTRY_IMAGE` — full image path (e.g. `registry.gitlab.com/group/project`)
- `$CI_COMMIT_SHORT_SHA` — 8-char commit SHA
- `$CI_COMMIT_REF_SLUG` — branch/tag name, URL-safe

```yaml
# Tag with both SHA and branch slug
IMAGE_TAG: "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
IMAGE_LATEST: "$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG"
```

## Build Job

```yaml
build:docker:
  stage: build
  <<: *docker-base
  script:
    - |
      docker build \
        --cache-from "$CI_REGISTRY_IMAGE:latest" \
        --tag "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" \
        --tag "$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG" \
        .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG"
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
```

## Kaniko Alternative (rootless runners)

```yaml
build:kaniko:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:v1.23.0-debug
    entrypoint: ['']
  script:
    - /kaniko/executor
        --context "$CI_PROJECT_DIR"
        --dockerfile "$CI_PROJECT_DIR/Dockerfile"
        --destination "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
        --destination "$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG"
        --cache=true
        --cache-repo "$CI_REGISTRY_IMAGE/cache"
```

## Multi-Stage Build Pattern

Keep build tools out of the final image:

```dockerfile
# Build stage
FROM golang:1.23 AS builder
WORKDIR /app
COPY . .
RUN go build -o /app/bin/server ./cmd/server

# Runtime stage
FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/bin/server /server
ENTRYPOINT ["/server"]
```

## Recommended Stage Order

```yaml
stages:
  - test
  - build    # docker build + push
  - deploy   # see advanced.md
```
