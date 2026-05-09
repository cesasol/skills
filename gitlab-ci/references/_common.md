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

## 3. `extends:` Usage

Preferred over YAML anchors for cross-file reuse. Max 3 levels of inheritance.

```yaml
.my-base:
  image: node:24-bookworm-slim
  cache:
    key: { files: [pnpm-lock.yaml] }
    paths: [node_modules]

lint:
  extends: .my-base
  script: [pnpm lint]
```

Source: <https://docs.gitlab.com/ci/yaml/yaml_optimization/>

## 4. `default:` Keyword

Sets shared configuration for all jobs. Replaces the deprecated global-level pattern.

```yaml
default:
  image: node:24-bookworm-slim
  cache:
    key: { files: [pnpm-lock.yaml], prefix: ${CI_COMMIT_REF_SLUG} }
    paths: [node_modules, .pnpm-store]
    policy: pull-push
```

Source: <https://docs.gitlab.com/ci/yaml/#default>

## 5. Artifact Best Practices

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

## 6. Security Template Includes

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

## 7. Deprecated Keywords

Do **not** generate these in any pipeline YAML:

| Keyword | Replacement |
|---------|-------------|
| `only:` / `except:` | `rules:` with `if:` conditions |
| Global `image:` | `default: image:` |
| Global `cache:` | `default: cache:` |
| Global `before_script:` | `default: before_script:` |
| Global `after_script:` | `default: after_script:` |

Source: <https://docs.gitlab.com/ci/yaml/deprecated_keywords/>

## 8. Reuse Mechanism Decision Tree

| Scenario | Mechanism | Why |
|----------|-----------|-----|
| Cross-file reuse | `extends:` | File-agnostic, explicit override order |
| Single field/block reference | `!reference` tag | Targeted snippet reuse in arrays/maps |
| In-file reuse (legacy compat) | YAML anchors (`&` / `<<:`) | Works but merge-order is brittle |
| Override specific keys | `extends:` with partial definition | Only keys present are overridden |
| Merge array fields | `!reference` | Anchors cannot merge arrays sanely |

Source: <https://docs.gitlab.com/ci/yaml/yaml_optimization/>
