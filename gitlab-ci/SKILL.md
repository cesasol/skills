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

## Step 1: Detect project type

Scan the project root for these signals (check in order):

| Signal file | Stack |
|---|---|
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

Also check for framework indicators: `nuxt.config.ts` / `next.config.js` / `vite.config.ts` → note framework; `playwright.config.ts` → note e2e tests; `.golangci.yaml` → note golangci-lint; `rust-toolchain.toml` → note pinned toolchain.

**Monorepo (v1 limitation)**: If multiple stacks detected (e.g. `package.json` + `go.mod`), ask the user which stack to generate for. Do NOT generate multi-stack pipelines.

**Existing pipeline**: If `.gitlab-ci.yml` already exists, write to `.gitlab-ci.new.yml` instead. Tell the user to diff before replacing.

## Step 2: Interview the user

Ask only what you couldn't detect. Cover:

1. **Deploy target** — Cloudflare Workers, AWS, Kubernetes, Docker Registry, none?
2. **Stages needed** — Beyond lint/test/build: security scanning? e2e tests? preview environments?
3. **Environment strategy** — Auto-deploy on main? Manual gates? Preview apps on MRs?
4. **Required CI/CD variables** — What secrets are already configured?

Keep it to 2–4 questions. Don't ask about things already detected.

## Step 3: Load the reference file

Based on the detected stack, load the matching reference:

| Stack | Reference |
|---|---|
| Node.js | `Read("gitlab-ci/references/nodejs.md")` |
| Python | `Read("gitlab-ci/references/python.md")` |
| Go | `Read("gitlab-ci/references/go.md")` |
| Docker | `Read("gitlab-ci/references/docker.md")` |
| Rust | `Read("gitlab-ci/references/rust.md")` |

Always also read `gitlab-ci/references/_common.md` for shared patterns.

If Container Registry or Release pipeline patterns are needed, also read `gitlab-ci/references/advanced.md`.

## Step 4: Generate the pipeline

Build `.gitlab-ci.yml` (or `.gitlab-ci.new.yml`) with this structure:

1. **Header comment** — pipeline overview, required variables, key behaviors
2. **`include:`** — GitLab security templates (only if user opted in)
3. **`stages:`** — explicit stage list (never rely on defaults)
4. **`variables:`** — global variables (tool versions, CI flags)
5. **`workflow:`** — MR + branch dedup rules (from _common.md)
6. **`default:`** — shared image, before_script, cache (not global keywords)
7. **Hidden job templates** (`.name:`) for `extends:`
8. **Jobs by stage** — install → quality → test → security → build → deploy

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
- [ ] No hardcoded hostnames — use predefined CI variables (`$CI_REGISTRY_IMAGE`, etc.)

## Validation via glab

If the user has the `glab` skill installed, they can lint the generated pipeline:

```
glab ci lint --path .gitlab-ci.yml
```

See the `glab` skill for details.
