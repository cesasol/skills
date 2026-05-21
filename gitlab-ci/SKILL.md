---
name: gitlab-ci
description: >
  Generate production-grade .gitlab-ci.yml pipelines from scratch for Node.js, Python, Go, Docker, and Rust projects.
  Use this skill whenever the user mentions GitLab CI, .gitlab-ci.yml, pipeline configuration, CI/CD setup,
  or wants to create or rewrite a GitLab pipeline. Also trigger when the user asks about pipeline stages,
  job configuration, cache/artifacts setup, security scanning, deployment environments, or says
  "add CI to my GitLab project". If the user has an existing .gitlab-ci.yml and wants to improve it, use this skill too.
---

# gitlab-ci — Pipeline Generator

Generate or improve GitLab CI pipelines using GitLab-native patterns. Prefer adapting to the repository's existing tools over introducing new ones.

## Workflow

### Step 1: Confirm this is a GitLab CI task

Use this skill for GitLab repositories and `.gitlab-ci.yml` work. Do not use it for GitHub Actions, generic Dockerfiles, or local-only task runners unless the user is migrating them into GitLab CI.

### Step 2: Detect project type

Scan the project root for these signals (check in order):

| Signal file | Stack |
| --- | --- |
| `pnpm-lock.yaml` | Node.js + pnpm |
| `yarn.lock` | Node.js + yarn |
| `package-lock.json` | Node.js + npm |
| `package.json` (no lockfile) | Node.js (ask which package manager) |
| `uv.lock` | Python + uv |
| `poetry.lock` | Python + poetry |
| `requirements.txt` (no pyproject.toml) | Python + pip |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `Dockerfile` (no other signals) | Docker-only |

Also check for framework indicators: `nuxt.config.ts` / `next.config.js` / `vite.config.ts` → note framework; `playwright.config.ts` → note e2e tests; `.golangci.yaml` → note golangci-lint;
`rust-toolchain.toml` → note pinned toolchain.

**Monorepo (v1 limitation)**: If multiple stacks detected (e.g. `package.json` + `go.mod`), ask the user which stack to generate for. Do NOT generate multi-stack pipelines.

**Existing pipeline**: If `.gitlab-ci.yml` already exists, inspect it first. Write proposed replacements to `.gitlab-ci.new.yml` unless the user explicitly approves editing the existing file.

### Step 3: Interview the user

Ask only what you couldn't detect. Cover:

1. **Deploy target** — Cloudflare Workers, AWS, Kubernetes, Docker Registry, none?
2. **Stages needed** — Beyond lint/test/build: security scanning? e2e tests? preview environments?
3. **Environment strategy** — Auto-deploy on main? Manual gates? Preview apps on MRs?
4. **Required CI/CD variables** — What secrets are already configured?

Keep it to 2–4 questions. Don't ask about things already detected. If deploy details are unclear, generate lint/test/build only and leave deployment out.

### Step 4: Load reference files

Always read `references/_common.md` for shared GitLab CI patterns. Then read the detected stack reference:

| Stack | Reference |
| --- | --- |
| Node.js | `references/nodejs.md` |
| Python | `references/python.md` |
| Go | `references/go.md` |
| Docker | `references/docker.md` |
| Rust | `references/rust.md` |

If the pipeline uses components, templates, `include:inputs`, `trigger:inputs`, or reusable configuration parameters, also read `references/inputs.md`.

If Container Registry, release, or advanced deploy patterns are needed, also read `references/advanced.md`.

### Step 5: Generate the pipeline

Build `.gitlab-ci.yml` (or `.gitlab-ci.new.yml`) with this structure:

1. **Header comment** — pipeline overview, required variables, key behaviors
2. **`include:`** — prefer GitLab CI/CD components for reusable pipeline units; use GitLab security templates only if the user opted in
3. **`stages:`** — explicit stage list (never rely on defaults)
4. **`variables:`** — global variables (tool versions, CI flags)
5. **`workflow:`** — MR + branch dedup rules (from _common.md)
6. **`default:`** — shared image, before_script, cache (not global keywords)
7. **Hidden job templates** (`.name:`) for local `extends:` reuse when components are not suitable
8. **Jobs by stage** — install → quality → test → security → build → deploy
9. **Matrix jobs** — use `parallel:matrix` for version/platform/database compatibility checks when appropriate

## Validation checklist

Before presenting, verify every requirement:

- [ ] `stages:` declared explicitly (never rely on defaults)
- [ ] `workflow:rules` present with MR dedup
- [ ] No `only:` or `except:` (use `rules:`)
- [ ] No global `image:`, `cache:`, `before_script:` (use `default:`)
- [ ] Every `artifacts:` block has `expire_in`
- [ ] Cache keys use `key.files` for lockfile-based invalidation
- [ ] Jobs use `needs:` for DAG execution
- [ ] Long-running jobs have `interruptible: true`
- [ ] Deploy jobs use `resource_group:` for serialization
- [ ] No hardcoded hostnames — use predefined CI variables (`$CI_REGISTRY_IMAGE`, `$CI_SERVER_FQDN`, etc.)
- [ ] Components are preferred for reusable cross-project logic and pinned to a safe version
- [ ] Matrix execution is considered for meaningful compatibility axes, not used for unnecessary fan-out

## Variables review

After generating the first draft, do a separate pass looking for values that should become variables or component inputs:

- language/tool versions (`NODE_VERSION`, `PYTHON_VERSION`, `GO_VERSION`, `RUST_VERSION`)
- cache/tool directories and repeated command flags
- registry paths, image tags, deploy regions, chart names, and environment URLs
- values repeated across multiple jobs

For reusable components/templates, prefer typed `spec:inputs` over variables for user-configurable structure. Do not put secrets in YAML variables or inputs. Secrets belong in GitLab CI/CD settings as
masked/protected variables.

## Validation via glab

When `glab` is available and the repository is connected to GitLab, compile included components/templates first, then lint before finalizing:

```bash
glab ci config compile --path .gitlab-ci.yml
glab ci lint --path .gitlab-ci.yml
```

If writing `.gitlab-ci.new.yml`, use that path for both commands. If compile or lint fails, fix the YAML or explain the GitLab-specific incompatibility.

## Example output

For a detected Node.js project with `pnpm-lock.yaml`, generate a pipeline with install,
quality, test, build, and optional deploy stages. Use pnpm cache keys based on the lockfile,
MR/branch deduplication in `workflow:rules`, and artifacts with explicit expiration.

For an existing project that already has `.gitlab-ci.yml`, write `.gitlab-ci.new.yml` and
explain that the user should review the diff before replacing the current pipeline.

## Gotchas and common mistakes

- If multiple stacks are present, ask which one to target instead of guessing.
- If deploy details are missing, generate lint/test/build only and leave deployment out.
- If security scanning is requested, include GitLab templates only when compatible with the stack.
- Avoid hardcoded registry paths, environment URLs, and secret values; use CI variables instead.
- Never overwrite an existing `.gitlab-ci.yml` without explicit user approval.
- Prefer `rules:` and `workflow:rules`; do not introduce legacy `only:` / `except:`.
- Use `default:` for shared `image`, `cache`, and `before_script`; avoid deprecated global-style keywords.
- Use explicit artifacts expiration and lockfile-based cache keys so pipelines do not accumulate stale outputs or caches.
