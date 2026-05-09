# Node.js — GitLab CI Reference

Patterns for Node.js projects using pnpm, npm, or yarn.
Read `_common.md` for shared patterns (workflow rules, cache strategy, extends, artifacts, deprecated keywords).

Source: <https://docs.gitlab.com/ci/yaml/>

## Detection Signals

| File | Stack |
|------|-------|
| `pnpm-lock.yaml` | Node.js + pnpm |
| `yarn.lock` | Node.js + yarn |
| `package-lock.json` | Node.js + npm |
| `nuxt.config.ts` / `next.config.js` / `vite.config.ts` | note framework |
| `playwright.config.ts` | e2e tests available |

## Docker Image

`node:${NODE_VERSION}-bookworm-slim` — Debian-based, smaller than full, has glibc for native modules.

## pnpm Setup (primary)

Use corepack to activate the exact pnpm version from `package.json`:

```yaml
variables:
  NODE_VERSION: '24'
  PNPM_VERSION: '10.32.1'
  PNPM_STORE_DIR: '$CI_PROJECT_DIR/.pnpm-store'

.setup-pnpm: &setup-pnpm
  - corepack enable
  - corepack prepare pnpm@${PNPM_VERSION} --activate
  - pnpm config set store-dir "$PNPM_STORE_DIR"
```

**npm variant**: replace script with `npm ci`
**yarn variant**: replace script with `yarn install --frozen-lockfile`

## Cache Strategy

Source: <https://docs.gitlab.com/ci/caching/>

```yaml
.pnpm-cache: &pnpm-cache
  key:
    files: [pnpm-lock.yaml]
    prefix: ${CI_COMMIT_REF_SLUG}
  paths: [.pnpm-store, node_modules]
  policy: pull  # install job overrides to pull-push
```

For npm: `files: [package-lock.json]`, paths: `[node_modules]`
For yarn: `files: [yarn.lock]`, paths: `[node_modules, .yarn/cache]`

## Install Job

```yaml
install:
  stage: install
  image: node:${NODE_VERSION}-bookworm-slim
  cache:
    <<: *pnpm-cache
    policy: pull-push
  script:
    - *setup-pnpm
    - pnpm install --frozen-lockfile
  artifacts:
    paths: [node_modules, .nuxt]  # .nuxt only for Nuxt projects
    expire_in: 1 hour
```

## Quality Jobs (parallel)

Both use `needs: [install]` to start as soon as install finishes.

```yaml
lint:
  stage: quality
  image: node:${NODE_VERSION}-bookworm-slim
  needs: [install]
  cache:
    <<: *pnpm-cache
  script:
    - *setup-pnpm
    - pnpm lint

typecheck:
  stage: quality
  image: node:${NODE_VERSION}-bookworm-slim
  needs: [install]
  cache:
    <<: *pnpm-cache
  script:
    - *setup-pnpm
    - pnpm typecheck
```

## Unit Test Job

Source: <https://docs.gitlab.com/ci/testing/unit_test_reports/>
Source: <https://docs.gitlab.com/ci/testing/code_coverage/>

```yaml
test:unit:
  stage: test
  image: node:${NODE_VERSION}-bookworm-slim
  needs: [install]
  cache:
    <<: *pnpm-cache
  script:
    - *setup-pnpm
    - pnpm test:coverage --reporter=default --reporter=junit --outputFile=junit.xml
  coverage: '/All files[^|]*\|[^|]*\s+([\d.]+)/'
  artifacts:
    when: always
    expire_in: 1 week
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    paths: [coverage/]
```

## E2E Test Job (Playwright)

Use the official Playwright image — browsers and system deps are pre-installed.
Pin the image version to match `@playwright/test` in your lockfile.

```yaml
test:e2e:
  stage: test
  image: mcr.microsoft.com/playwright:v1.50.0-jammy  # pin to version in lockfile
  needs: [install]
  cache:
    <<: *pnpm-cache
  script:
    - *setup-pnpm
    # Reinstall: cached node_modules came from a different image; binary deps may differ
    - pnpm install --frozen-lockfile --prefer-offline
    - pnpm test:e2e
  artifacts:
    when: always
    expire_in: 1 week
    paths: [playwright-report/, test-results/]
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Build Job

```yaml
build:
  stage: build
  image: node:${NODE_VERSION}-bookworm-slim
  needs: [install, lint, typecheck, test:unit]
  cache:
    <<: *pnpm-cache
  script:
    - *setup-pnpm
    - pnpm build
  artifacts:
    expire_in: 1 day
    paths:
      - .output/    # Nuxt
      - dist/       # Vite / generic
      - .next/      # Next.js
```

## Recommended Stage Order

```yaml
stages:
  - install
  - quality    # lint + typecheck in parallel
  - test       # unit + e2e in parallel
  - build
  - deploy     # see advanced.md
```
