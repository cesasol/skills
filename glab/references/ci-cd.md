# CI/CD — Pipelines, Jobs, Schedules, Runners

Complete reference for `glab ci`, `glab job`, `glab schedule`, and `glab runner`.

## Table of Contents

- [Pipeline Status](#pipeline-status)
- [Pipeline List](#pipeline-list)
- [Pipeline Run](#pipeline-run)
- [Pipeline Get (JSON)](#pipeline-get-json)
- [Pipeline Cancel and Delete](#pipeline-cancel-and-delete)
- [Job Trace / Logs](#job-trace--logs)
- [Job Retry and Trigger](#job-retry-and-trigger)
- [Job Artifacts](#job-artifacts)
- [CI Lint](#ci-lint)
- [Schedules](#schedules)
- [Runners](#runners)

## Pipeline Status

```bash
# Current branch status as JSON
glab ci status -F json

# Specific branch
glab ci status --branch main -F json

# Compact text output (human-readable summary)
glab ci status --compact
```

> **Warning:** Do NOT use `glab ci status --live` — it streams in real-time and blocks.

## Pipeline List

```bash
# Recent pipelines
glab ci list -F json

# With pagination
glab ci list --per-page 10 --page 1 -F json

# Specific branch
glab ci list --branch main -F json
```

## Pipeline Run

```bash
# Trigger pipeline on current branch
glab ci run

# Specific branch
glab ci run --branch main

# With variables
glab ci run --variables "DEPLOY_ENV:staging"
glab ci run --variables "KEY1:value1" --variables "KEY2:value2"

# Escaped commas in values
glab ci run --variables "KEY1:value,with,comma"

# With typed pipeline inputs (CI/CD inputs)
glab ci run --input "env:string(production)" --input "count:int(5)" --input "debug:bool(true)"
glab ci run --input "tags:array(web,api,worker)"

# Using a trigger token
glab ci run-trig --token "$TRIGGER_TOKEN" --branch main
glab ci run-trig --token "$TRIGGER_TOKEN" --variables "ENV:prod"
```

### Pipeline input types

| Type | Syntax | Example |
|------|--------|---------|
| string | `key:string(value)` or `key:value` | `env:string(staging)` |
| int | `key:int(N)` | `replicas:int(3)` |
| float | `key:float(N)` | `threshold:float(0.95)` |
| bool | `key:bool(true\|false)` | `debug:bool(false)` |
| array | `key:array(a,b,c)` | `regions:array(us,eu,ap)` |

## Pipeline Get (JSON)

```bash
# Get current branch pipeline details
glab ci get -F json

# Specific branch
glab ci get --branch main -F json

# Specific pipeline ID
glab ci get --pipeline-id 12345 -F json
```

## Pipeline Cancel and Delete

```bash
# Cancel running pipeline on current branch
glab ci cancel pipeline

# Cancel a specific job
glab ci cancel job <job-id>

# Delete a pipeline
glab ci delete 12345
```

## Job Trace / Logs

```bash
# Trace a job log (streams output)
glab ci trace <job-id>

# By job name (from current branch pipeline)
glab ci trace "rspec"

# Specific branch
glab ci trace <job-id> --branch main
```

> **Note:** `glab ci trace` streams log output to stdout. For agents, prefer `glab api` to fetch job logs as JSON if you need structured data:
> ```bash
> glab api projects/:id/jobs/<job-id>/trace
> ```

## Job Retry and Trigger

```bash
# Retry a failed job
glab ci retry <job-id>

# Trigger a manual job
glab ci trigger <job-id>

# Trigger with variables
glab ci trigger <job-id> --variables "KEY:value"
```

## Job Artifacts

```bash
# Download artifacts from latest pipeline
glab ci artifact <ref> <job-name>

# Example: download from main branch, job "build"
glab ci artifact main build

# Specify output path
glab ci artifact main build --path ./artifacts/
```

## CI Lint

```bash
# Validate .gitlab-ci.yml
glab ci lint

# Lint a specific file
glab ci lint path/to/.gitlab-ci.yml

# Include merged YAML (resolve includes)
glab ci lint --include-merged-yaml
```

## Schedules

```bash
# List schedules
glab schedule list -F json

# Create a schedule
glab schedule create \
  --description "Nightly build" \
  --ref main \
  --cron "0 2 * * *" \
  --cron-timezone "America/New_York" \
  --active

# Run a schedule immediately
glab schedule run <schedule-id>

# Update a schedule
glab schedule update <schedule-id> \
  --description "Updated nightly" \
  --cron "0 3 * * *"

# Delete a schedule
glab schedule delete <schedule-id>
```

### Schedule create flags

| Flag | Description |
|------|-------------|
| `--description` | Schedule description |
| `--ref` | Branch or tag to run on |
| `--cron` | Cron expression (e.g., `0 2 * * *`) |
| `--cron-timezone` | Timezone for cron (e.g., `UTC`, `America/New_York`) |
| `--active` | Activate schedule on creation |
| `--variables` | Pipeline variables (`KEY:value`, repeat flag) |

## Runners

```bash
# List project runners
glab runner list -F json

# List all available runners (including shared)
glab runner list --all -F json

# Assign a runner to a project
glab runner assign <runner-id>

# Unassign a runner
glab runner unassign <runner-id>

# Update runner settings
glab runner update <runner-id> --description "Updated runner" --tag-list "docker,linux"

# Delete/unregister a runner
glab runner delete <runner-id>
```
