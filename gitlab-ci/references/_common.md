# GitLab CI — Shared Patterns Reference

Common patterns shared across all stack-specific references. Agents generating pipeline YAML **must** consult this page before writing.

## 1. Workflow Rules

Canonical MR + branch dedup. Prevents duplicate pipelines when a branch has an open MR.

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
```

Source: <https://docs.gitlab.com/ci/yaml/workflow/>

## 2. Cache Strategy

Per-branch + per-lockfile keys. Producer jobs use `pull-push`; downstream consumers use `pull`.

```yaml
install:
  cache:
    key:
      files: [pnpm-lock.yaml]
      prefix: ${CI_COMMIT_REF_SLUG}
    paths: [node_modules, .pnpm-store]
    policy: pull-push
```

Source: <https://docs.gitlab.com/ci/caching/>

## 3. Components First, Templates Second

Favor GitLab CI/CD components for reusable, versioned pipeline units, especially when a job pattern will be reused across projects. Use `include: component` with explicit inputs and pinned versions.

```yaml
include:
  - component: $CI_SERVER_FQDN/my-org/ci-components/node-test@1.4.2
    inputs:
      stage: test
      node-version: "26"
```

Component rules:

- Prefer catalog-published semantic versions or commit SHAs; avoid `~latest` in production pipelines.
- Use typed `spec:inputs` for user-configurable component behavior; read `inputs.md` when adding or consuming component inputs.
- Use `$CI_SERVER_FQDN` instead of hardcoding `gitlab.com` so self-managed instances work.
- Audit third-party components before use; they run code with CI access.
- Avoid job-name collisions because component config merges into the final pipeline.

Source: <https://docs.gitlab.com/ci/components/>

## 4. `extends:` Usage

Use `extends:` for repository-local reuse or when no suitable component exists. Prefer components over local templates for cross-project reuse. Max 3 levels of inheritance.

```yaml
.my-base:
  image: node:26-bookworm-slim
  cache:
    key: { files: [pnpm-lock.yaml] }
    paths: [node_modules]

lint:
  extends: .my-base
  script: [pnpm lint]
```

Source: <https://docs.gitlab.com/ci/yaml/yaml_optimization/>

## 5. `default:` Keyword

Sets shared configuration for all jobs. Replaces the deprecated global-level pattern.

```yaml
default:
  image: node:26-bookworm-slim
  cache:
    key: { files: [pnpm-lock.yaml], prefix: ${CI_COMMIT_REF_SLUG} }
    paths: [node_modules, .pnpm-store]
    policy: pull-push
```

Source: <https://docs.gitlab.com/ci/yaml/#default>

## 6. Artifact Best Practices

Always set `expire_in`. Use `when: always` for test reports. Restrict propagation with `dependencies:`.

```yaml
test:
  artifacts:
    paths: [coverage/]
    expire_in: 1 week
    when: always
    reports:
      junit: junit.xml
```

Source: <https://docs.gitlab.com/ci/yaml/#artifacts>

## 7. Security Template Includes

GitLab-managed security templates are opt-in. Override their stage via variables.

```yaml
include:
  - template: Jobs/SAST.gitlab-ci.yml
  - template: Jobs/Secret-Detection.gitlab-ci.yml

variables:
  SAST_STAGE: security
  SECRET_DETECTION_STAGE: security
```

Source: <https://docs.gitlab.com/ci/yaml/includes/>

## 8. Deprecated Keywords

Do **not** generate these in any pipeline YAML:

| Keyword | Replacement |
| --------- | ------------- |
| `only:` / `except:` | `rules:` with `if:` conditions |
| Global `image:` | `default: image:` |
| Global `cache:` | `default: cache:` |
| Global `before_script:` | `default: before_script:` |
| Global `after_script:` | `default: after_script:` |

Source: <https://docs.gitlab.com/ci/yaml/deprecated_keywords/>

## 9. Matrix Execution

Use `parallel:matrix` when the same job should run across versions, platforms, services, or feature flags. Keep matrix dimensions small and name variables clearly.

```yaml
test:
  stage: test
  parallel:
    matrix:
      - NODE_VERSION: [24, 26]
        DATABASE_URL: [postgres, mysql]
  image: node:${NODE_VERSION}-bookworm-slim
  script: npm test
```

Use matrix jobs for compatibility checks; do not use them when a single latest-stable version is enough.

Source: <https://docs.gitlab.com/ci/jobs/job_control/#parallelize-large-jobs>

## 10. Reuse Mechanism Decision Tree

| Scenario | Mechanism | Why |
| ---------- | ----------- | ----- |
| Cross-project reusable pipeline unit | `include: component` | Versioned, documented, and catalog-friendly |
| Repository-local job reuse | `extends:` | File-agnostic, explicit override order |
| Single field/block reference | `!reference` tag | Targeted snippet reuse in arrays/maps |
| In-file reuse (legacy compat) | YAML anchors (`&` / `<<:`) | Works but merge-order is brittle |
| Override specific keys | `extends:` with partial definition | Only keys present are overridden |
| Merge array fields | `!reference` | Anchors cannot merge arrays sanely |

Source: <https://docs.gitlab.com/ci/yaml/yaml_optimization/>

## 11. Variables Review

After drafting YAML, review hardcoded values and promote reusable or environment-specific values into `variables:` or component `inputs:`. Read `inputs.md` before adding `spec:inputs`,
`include:inputs`, or `trigger:inputs`.

Good candidates:

- language/tool versions (`NODE_VERSION`, `GO_VERSION`, `RUST_VERSION`, `PYTHON_VERSION`)
- cache/tool directories (`UV_CACHE_DIR`, `GOMODCACHE`, `CARGO_HOME`)
- deploy regions, registry names, image tags, chart names, and environment URLs
- repeated flags shared by multiple jobs

Do not move secrets into YAML variables. Secrets belong in GitLab CI/CD settings as masked/protected variables.

## 12. Render and Lint Full Configuration

When the pipeline uses components or includes, render the merged configuration before reviewing job interactions:

```bash
glab ci config compile --path .gitlab-ci.yml
```

Then lint the same file:

```bash
glab ci lint --path .gitlab-ci.yml
```

Use `--path .gitlab-ci.new.yml` when proposing a replacement file.
