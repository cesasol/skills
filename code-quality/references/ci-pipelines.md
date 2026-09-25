# Pipelines — Making the Baseline Blocking

A check that runs only on a developer's machine is a suggestion. The pipeline is what turns the baseline into a rule, so every repository needs one quality stage that runs the same commands the hooks
run, across the whole tree, with no way to merge past a failure.

## The Contract

| Property | Requirement |
| --- | --- |
| Trigger | Merge or pull requests, the default branch, and tags. |
| Entry point | `uvx prek run --all-files`, then `just ci`. Never a command the developer cannot run. |
| Scope | Lint and secret scanning cover the whole repository; tests may be scoped by path. |
| Failure | Blocking. No `allow_failure: true`, no `continue-on-error: true`, no manual quality jobs. |
| Determinism | Pinned images, pinned tool versions, frozen lockfiles, cached but never regenerated dependencies. |
| Duration | Fast enough that nobody asks to skip it. Split slow suites into parallel jobs instead of relaxing them. |

## GitLab CI

The pipeline below is the minimum quality gate. For the rest of GitLab pipeline design, which is caching strategy, artifacts, child pipelines, environments, and `rules`, use the **gitlab-ci** skill.

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

# Jobs call recipes. `just` is not in the image, and `uvx rust-just` fails
# because the package's binary is named `just`, so uv needs --from.
.just:
  image: ghcr.io/astral-sh/uv:python3.14-bookworm-slim
  variables:
    JUST: uvx --from rust-just just
  before_script:
    - uv sync --frozen --all-packages --all-groups

quality:checks:
  extends: .just
  stage: quality
  script:
    - $JUST fmt-check
    - $JUST lint
    - $JUST typecheck

# The recipe writes coverage.xml and report.xml; the job only collects them.
test:
  extends: .just
  stage: test
  coverage: '/^TOTAL\s+.*\s+(\d+(?:\.\d+)?)%$/'
  script:
    - $JUST test
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

- A job whose script is anything other than a recipe call has already drifted from the developer's machine. The two exceptions are the hook suite, which prek runs directly, and artifact collection,
  which is platform configuration rather than a command.
- When `just ci` spans two toolchains that no single image carries, either build and pin one image with both, or split the pipeline by package and call each package's own justfile
  (`just --justfile web/justfile lint`). Restating the package's commands in YAML is the wrong fix.
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
        run: uvx --from rust-just just ci
```

GitHub specifics worth knowing:

- Pin actions by major tag at minimum; pin by commit SHA for anything that touches credentials.
- Set `permissions` explicitly. The default token is broader than a quality job needs.
- `fetch-depth: 0` matters for history-scanning tools such as gitleaks; everything else is happy with a shallow clone.
- Make the quality job a required status check in branch protection. Without that, the pipeline reports but does not block.

## Keeping Local and CI in Step

The recurring failure is a pipeline that checks something the developer never runs, or the reverse. Prevent it structurally:

1. Put every command in a `just` recipe, using the standard names from [just-recipes.md](just-recipes.md).
2. Let hooks and CI call those recipes rather than restating the commands. A job body longer than one recipe call is a recipe waiting to be written.
3. Pin the same tool versions in both places: `prek.toml` revisions, lockfiles, and the CI image tag.
4. When CI needs an extra step, such as a full-tree scan, an image build, or a coverage upload, add it as a separate recipe, not as inline YAML.
5. Split the pipeline by recipe, not by fragment: one job per `lint`, `typecheck`, `test`, and `build` when the wall clock demands parallelism. `just ci` stays complete for local use.
6. A smoke test runs `just start` against the built artifact. That is the same command the deployment runs, which is the point.

## Failure Modes

- **The pipeline passes but the merge still breaks the default branch.** The job was not a required check, or it ran only on pushes. Cover merge or pull requests explicitly.
- **`prek run --all-files` fails only in CI.** The developer's hooks are not installed. Run `uvx prek install`; the CI failure is correct.
- **The protected-branch hook fails the pipeline on `main`.** Set `SKIP=no-commit-to-branch` for that job.
- **Cache poisoning makes a green pipeline lie.** Key caches on the lockfile, never restore across branches without a prefix, and never let a job write a lockfile.
- **Quality jobs are skipped by path filters.** Scope tests by path if needed, but lint, formatting, and secret scanning always run over the whole tree.
- **A flaky test drives the team to `allow_failure: true`.** Quarantine the test explicitly, with an issue link and a deadline, instead of weakening the job that protects the branch.
