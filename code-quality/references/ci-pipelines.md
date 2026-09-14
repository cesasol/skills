# Pipelines — Making the Baseline Blocking

A check that runs only on a developer's machine is a suggestion. The pipeline is what turns the baseline into a rule, so every repository needs one quality stage that runs the same commands the hooks
run, across the whole tree, with no way to merge past a failure.

## The Contract

| Property | Requirement |
| --- | --- |
| Trigger | Merge or pull requests, the default branch, and tags. |
| Entry point | `uvx prek run --all-files`, then `just ci`. |
| Scope | Lint and secret scanning cover the whole repository; tests may be scoped by path. |
| Failure | Blocking. No `allow_failure: true`, no `continue-on-error: true`, no manual quality jobs. |
| Determinism | Pinned images, pinned tool versions, frozen lockfiles, cached but never regenerated dependencies. |
| Duration | Fast enough that nobody asks to skip it. Split slow suites into parallel jobs instead of relaxing them. |

## GitLab CI

```yaml
stages: [quality, test]

workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_TAG
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH

include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml

# prek runs every hook — formatters, linters, gitleaks, hygiene — over the full tree.
# SKIP=no-commit-to-branch: that hook fails by design on the protected branch.
quality:hooks:
  stage: quality
  image: ghcr.io/astral-sh/uv:python3.14-bookworm-slim
  variables:
    SKIP: no-commit-to-branch
  script:
    - uvx prek run --all-files

quality:types:
  stage: quality
  image: ghcr.io/astral-sh/uv:python3.14-bookworm-slim
  script:
    - uv sync --frozen --all-packages --all-groups
    - uv run --no-sync ty check

test:
  stage: test
  image: ghcr.io/astral-sh/uv:python3.14-bookworm-slim
  coverage: '/^TOTAL\s+.*\s+(\d+(?:\.\d+)?)%$/'
  script:
    - uv sync --frozen --all-packages --all-groups
    - uv run --no-sync pytest --cov --cov-report=term --cov-report=xml:coverage.xml --junitxml=report.xml
  artifacts:
    when: always
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

sast:
  stage: quality

secret_detection:
  stage: quality
```

GitLab specifics worth knowing:

- Security templates default to a `test` stage. Repin them, as above, when the pipeline names its stages differently.
- `rules:changes` evaluates to true on tag pipelines and on the first pipeline of a new branch. Gate tag work on an explicit `$CI_COMMIT_TAG` pattern, never on `changes` alone.
- In a monorepo, trigger one child pipeline per service with `strategy: depend`, so the parent's status — and therefore the merge request — reflects every child.
- Cache with a key derived from the lockfile, and let exactly one job seed the cache with `policy: pull-push` while the rest use `pull`.

## GitHub Actions

```yaml
name: ci

on:
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0 # gitleaks needs history
      - uses: astral-sh/setup-uv@v10
        with:
          enable-cache: true
      - uses: j178/prek-action@v3
        with:
          extra_args: --all-files
      - name: just ci
        run: uvx rust-just ci
```

GitHub specifics worth knowing:

- Pin actions by major tag at minimum; pin by commit SHA for anything that touches credentials.
- Set `permissions` explicitly. The default token is broader than a quality job needs.
- `fetch-depth: 0` matters for history-scanning tools such as gitleaks; everything else is happy with a shallow clone.
- Make the quality job a required status check in branch protection. Without that, the pipeline reports but does not block.

## Keeping Local and CI in Step

The recurring failure is a pipeline that checks something the developer never runs, or the reverse. Prevent it structurally:

1. Put every command in a `just` recipe.
2. Let hooks and CI call those recipes rather than restating the commands.
3. Pin the same tool versions in both places: `prek.toml` revisions, lockfiles, and the CI image tag.
4. When CI needs an extra step — full-tree scans, image builds, coverage upload — add it as a separate recipe, not as inline YAML.

## Failure Modes

- **The pipeline passes but the merge still breaks the default branch.** The job was not a required check, or it ran only on pushes. Cover merge or pull requests explicitly.
- **`prek run --all-files` fails only in CI.** The developer's hooks are not installed. Run `uvx prek install`; the CI failure is correct.
- **The protected-branch hook fails the pipeline on `main`.** Set `SKIP=no-commit-to-branch` for that job.
- **Cache poisoning makes a green pipeline lie.** Key caches on the lockfile, never restore across branches without a prefix, and never let a job write a lockfile.
- **Quality jobs are skipped by path filters.** Scope tests by path if needed, but lint, formatting, and secret scanning always run over the whole tree.
- **A flaky test drives the team to `allow_failure: true`.** Quarantine the test explicitly, with an issue link and a deadline, instead of weakening the job that protects the branch.
