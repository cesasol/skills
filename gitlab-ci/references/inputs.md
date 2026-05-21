# GitLab CI Inputs Reference

Use CI/CD inputs for typed, validated parameters in reusable GitLab CI templates and components.

Source: <https://docs.gitlab.com/ci/inputs/>

## When to use inputs vs variables

Use `spec:inputs` when a value configures pipeline structure or reusable configuration at pipeline creation time:

- component/template options such as stage, job name/prefix, enabled features, target environment, runner tags, or compatibility versions
- values that should be type-checked or constrained with `options` / `regex`
- values passed to included files with `include:inputs` or downstream pipelines with `trigger:inputs`

Use CI/CD variables when a value must exist in the job runtime environment or can change during execution:

- secrets and credentials from GitLab settings
- predefined variables such as `$CI_REGISTRY_IMAGE`, `$CI_SERVER_FQDN`, `$CI_COMMIT_SHA`
- dotenv outputs passed between jobs
- values used directly by scripts/tools at runtime

Inputs are interpolated when the configuration is fetched and remain fixed for the pipeline. They are only available in the file where they are defined unless explicitly passed to another include or
trigger.

## Component input pattern

Define inputs in the `spec:` header, add `---`, then use `$[[ inputs.<name> ]]` in jobs.

```yaml
spec:
  inputs:
    job-name:
      description: "Name for the generated job"
      default: test
    job-stage:
      description: "Stage to run the job in"
      default: test
    python-version:
      description: "Python version used by the uv image"
      default: "3.14"
      regex: '^3\.\d+$'
    run-coverage:
      type: boolean
      default: true
---

"$[[ inputs.job-name ]]":
  stage: $[[ inputs.job-stage ]]
  image: ghcr.io/astral-sh/uv:0.11.15-python$[[ inputs.python-version ]]-trixie-slim
  script:
    - uv sync --frozen
    - if $[[ inputs.run-coverage ]]; then uv run pytest --cov=.; else uv run pytest; fi
```

Use `include:inputs` when consuming a component or included file:

```yaml
include:
  - component: $CI_SERVER_FQDN/my-org/ci-components/python-test@1.2.0
    inputs:
      job-name: test:python
      job-stage: test
      python-version: "3.14"
      run-coverage: true
```

## Input configuration options

| Option | Use |
| --- | --- |
| `default` | Make an input optional and provide a safe fallback |
| `description` | Document the contract for component users |
| `options` | Restrict values to an allowed list |
| `regex` | Validate strings such as versions or environment names |
| `type` | Use `string`, `array`, `number`, or `boolean` |
| `rules` | Change default/options based on other input values |

Inputs without `default` are mandatory. For pipeline-level inputs in `.gitlab-ci.yml`, usually provide defaults so branch, tag, and merge request pipelines can start automatically.

## Typed examples

```yaml
spec:
  inputs:
    environment:
      options: [staging, production]
      default: staging
    concurrency:
      type: number
      default: 1
    allow-failure:
      type: boolean
      default: false
    needs-list:
      type: array
      default: []
---

deploy:
  stage: deploy
  needs: $[[ inputs.needs-list ]]
  allow_failure: $[[ inputs.allow-failure ]]
  script:
    - ./deploy.sh $[[ inputs.environment ]] --concurrency $[[ inputs.concurrency ]]
```

When an input replaces an entire YAML value, it keeps its type. When inserted inside a larger string, it becomes a string.

## Gotchas and common mistakes

- Add the YAML document separator `---` after a `spec:` header when the same file also contains jobs.
- Inputs are scoped to the file that defines them. Pass values explicitly with `include:inputs` for each include entry.
- Do not use inputs for secrets. Store secrets as masked/protected GitLab CI/CD variables.
- Array inputs cannot use complex YAML features such as `!reference` inside the array value.
- Pipeline-level inputs can take up to 20 inputs.
- Quote input interpolation inside `rules:if` expressions when the result must be a string, for example `if: $CI_COMMIT_REF_NAME == "$[[ inputs.branch ]]"`.
- Use `options`, `regex`, `number`, or `boolean` validation for user-controlled values. Do not rely on `posix_escape` as a security boundary.

## Validation checklist for components

Before publishing or using a component with inputs:

- [ ] Inputs have clear `description` values.
- [ ] User-selectable values use `options` where possible.
- [ ] Versions and structured strings use `regex`.
- [ ] Boolean and numeric settings use `type` instead of string conventions.
- [ ] Job names/stages that could collide are configurable with inputs.
- [ ] Secrets remain CI/CD variables, not inputs.
- [ ] `glab ci config compile --path .gitlab-ci.yml` renders the expected final configuration.
