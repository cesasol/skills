# Python — GitLab CI Reference

Patterns for Python projects using uv, poetry, or pip.
Read `_common.md` for shared patterns, including components, workflow rules, cache strategy, matrix execution, artifacts, and validation commands.

Source: <https://docs.gitlab.com/ci/yaml/>

## Detection Signals

| File | Stack |
| ------ | ------- |
| `uv.lock` | Python + uv |
| `poetry.lock` | Python + poetry |
| `pyproject.toml` (no lockfile) | Python + pip/build |
| `requirements.txt` | Python + pip |
| `pytest.ini` / `conftest.py` | pytest available |

## Docker Image

For uv projects, use Astral's uv image with uv preinstalled instead of installing uv with pip in every job:

```yaml
variables:
  PYTHON_VERSION: '3.14'
  UV_VERSION: '0.11.15'
  BASE_LAYER: trixie-slim
  UV_CACHE_DIR: '$CI_PROJECT_DIR/.uv-cache'
  # GitLab CI creates a separate mountpoint for the build directory, so uv must copy instead of hard-linking.
  UV_LINK_MODE: copy

.uv-image: &uv-image
  image: ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_VERSION}-${BASE_LAYER}

.setup-uv: &setup-uv
  - uv sync --frozen
```

If using a distroless uv image, set `entrypoint: [""]` on the image. For non-uv projects, use `python:${PYTHON_VERSION}-slim`.

Source: <https://docs.astral.sh/uv/guides/integration/gitlab/#using-the-uv-image>

**poetry variant**: use `python:${PYTHON_VERSION}-slim` with `pip install poetry && poetry install --no-root`
**pip variant**: use `python:${PYTHON_VERSION}-slim` with `pip install -r requirements.txt`

## Cache Strategy

Source: <https://docs.gitlab.com/ci/caching/>

```yaml
.uv-cache: &uv-cache
  key:
    files: [uv.lock]
    prefix: ${CI_COMMIT_REF_SLUG}
  paths: [.uv-cache]
  policy: pull
```

Add `after_script: [uv cache prune --ci]` to uv jobs that write the cache to keep GitLab cache archives small.

## Install Job

```yaml
install:
  stage: install
  <<: *uv-image
  cache:
    <<: *uv-cache
    policy: pull-push
  script:
    - *setup-uv
  after_script:
    - uv cache prune --ci
  artifacts:
    paths: [.venv]
    expire_in: 1 hour
```

## Quality Jobs (parallel)

```yaml
lint:
  stage: quality
  <<: *uv-image
  needs: [install]
  cache:
    <<: *uv-cache
  script:
    - *setup-uv
    - uv run ruff check .
    - uv run ruff format --check .

typecheck:
  stage: quality
  <<: *uv-image
  needs: [install]
  cache:
    <<: *uv-cache
  script:
    - *setup-uv
    - uv run mypy .
```

## Matrix variant

Use a matrix when the package intentionally supports multiple Python versions:

```yaml
test:compat:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION: [3.13, 3.14]
  <<: *uv-image
  script:
    - *setup-uv
    - uv run pytest
```

For ordinary service CI, test only the deployed latest stable Python version.

## Test Job

Source: <https://docs.gitlab.com/ci/testing/unit_test_reports/>
Source: <https://docs.gitlab.com/ci/testing/code_coverage/>

```yaml
test:
  stage: test
  <<: *uv-image
  needs: [install]
  cache:
    <<: *uv-cache
  script:
    - *setup-uv
    - uv run pytest --junitxml=junit.xml --cov=. --cov-report=xml:coverage.xml
  coverage: '/TOTAL.*\s+([\d.]+)%/'
  artifacts:
    when: always
    expire_in: 1 week
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths: [coverage.xml]
```

## Build Job

```yaml
build:
  stage: build
  <<: *uv-image
  needs: [install, lint, typecheck, test]
  cache:
    <<: *uv-cache
  script:
    - *setup-uv
    - uv run python -m build
  artifacts:
    expire_in: 1 day
    paths: [dist/]
```

## Recommended Stage Order

```yaml
stages:
  - install
  - quality
  - test
  - build
  - deploy
```
