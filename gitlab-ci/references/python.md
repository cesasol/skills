# Python — GitLab CI Reference

Patterns for Python projects using uv, poetry, or pip.
Read `_common.md` for shared patterns.

Source: <https://docs.gitlab.com/ci/yaml/>

## Detection Signals

| File | Stack |
|------|-------|
| `uv.lock` | Python + uv |
| `poetry.lock` | Python + poetry |
| `pyproject.toml` (no lockfile) | Python + pip/build |
| `requirements.txt` | Python + pip |
| `pytest.ini` / `conftest.py` | pytest available |

## Docker Image

`python:3.12-slim` or `python:3.13-slim` — Debian-based, smaller than full.

## uv Setup (primary)

```yaml
variables:
  UV_VERSION: '0.5.x'
  UV_CACHE_DIR: '$CI_PROJECT_DIR/.uv-cache'

.setup-uv: &setup-uv
  - pip install uv==${UV_VERSION} --quiet
  - uv sync --frozen
```

**poetry variant**: `pip install poetry && poetry install --no-root`
**pip variant**: `pip install -r requirements.txt`

## Cache Strategy

Source: <https://docs.gitlab.com/ci/caching/>

```yaml
.uv-cache: &uv-cache
  key:
    files: [uv.lock]
    prefix: ${CI_COMMIT_REF_SLUG}
  paths: [.uv-cache, .venv]
  policy: pull
```

## Install Job

```yaml
install:
  stage: install
  image: python:3.12-slim
  cache:
    <<: *uv-cache
    policy: pull-push
  script:
    - *setup-uv
  artifacts:
    paths: [.venv]
    expire_in: 1 hour
```

## Quality Jobs (parallel)

```yaml
lint:
  stage: quality
  image: python:3.12-slim
  needs: [install]
  cache:
    <<: *uv-cache
  script:
    - *setup-uv
    - uv run ruff check .
    - uv run ruff format --check .

typecheck:
  stage: quality
  image: python:3.12-slim
  needs: [install]
  cache:
    <<: *uv-cache
  script:
    - *setup-uv
    - uv run mypy .
```

## Test Job

Source: <https://docs.gitlab.com/ci/testing/unit_test_reports/>
Source: <https://docs.gitlab.com/ci/testing/code_coverage/>

```yaml
test:
  stage: test
  image: python:3.12-slim
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
  image: python:3.12-slim
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
