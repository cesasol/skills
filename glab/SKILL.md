---
name: glab
description: >
  Interact with GitLab using the `glab` CLI tool. Use when working with GitLab merge requests,
  issues, CI/CD pipelines, releases, labels, milestones, variables, runners, tokens, schedules,
  incidents, snippets, deploy keys, or making direct API requests. Covers both gitlab.com and
  self-hosted GitLab instances. Use this skill instead of `gh` (GitHub CLI) when the project
  is hosted on GitLab.
---

# glab — GitLab CLI

`glab` brings GitLab to the terminal. All commands assume glab is authenticated (`glab auth status` to verify).

## Critical Rules for Agents

1. **Never use interactive mode.** Always pass `--yes`/`-y` to skip prompts and `--no-editor` where available.
2. **Prefer JSON output.** Use `-F json` or `--output json` for parseable data. Fall back to `text` only for human display.
3. **Repo context.** When inside a git repo linked to GitLab, glab auto-detects the project. Use `-R OWNER/REPO` or `-R GROUP/NAMESPACE/REPO` to target a different project.
4. **Never expose tokens.** Do not log, print, or embed tokens in commands. Use `glab auth status` to check auth, never `glab config get token`.
5. **Avoid TUI commands.** `glab ci view` launches a TUI — use `glab ci status -F json` or `glab ci list -F json` instead.

## Command Domains

| Domain | Command | Reference | Key Operations |
|--------|---------|-----------|----------------|
| Merge Requests | `glab mr` | [merge-requests.md](references/merge-requests.md) | create, view, list, merge, approve, note, diff, update, rebase |
| Issues | `glab issue` | [issues-and-incidents.md](references/issues-and-incidents.md) | create, view, list, note, update, close |
| Incidents | `glab incident` | [issues-and-incidents.md](references/issues-and-incidents.md) | list, view, note, close, reopen |
| CI/CD Pipelines | `glab ci` | [ci-cd.md](references/ci-cd.md) | status, list, run, trace, retry, lint, cancel |
| CI/CD Jobs | `glab job` | [ci-cd.md](references/ci-cd.md) | list, trace, play, retry |
| Schedules | `glab schedule` | [ci-cd.md](references/ci-cd.md) | create, list, run, update, delete |
| Runners | `glab runner` | [ci-cd.md](references/ci-cd.md) | list, assign, unassign, update, delete |
| API | `glab api` | [api.md](references/api.md) | REST, GraphQL, pagination, placeholders |
| Releases | `glab release` | [project-management.md](references/project-management.md) | create, list, view, download, upload |
| Labels | `glab label` | [project-management.md](references/project-management.md) | create, list, edit, delete |
| Milestones | `glab milestone` | [project-management.md](references/project-management.md) | create, list, get, edit, delete |
| Variables | `glab variable` | [project-management.md](references/project-management.md) | set, get, list, update, delete, export |
| Snippets | `glab snippet` | [project-management.md](references/project-management.md) | create |
| Changelog | `glab changelog` | [project-management.md](references/project-management.md) | generate |
| Tokens | `glab token` | [infrastructure.md](references/infrastructure.md) | create, list, revoke, rotate |
| Deploy Keys | `glab deploy-key` | [infrastructure.md](references/infrastructure.md) | add, list, get, delete |
| Secure Files | `glab securefile` | [infrastructure.md](references/infrastructure.md) | create, download, list, remove |
| SSH/GPG Keys | `glab ssh-key` / `glab gpg-key` | [infrastructure.md](references/infrastructure.md) | add, list, get, delete |
| Clusters | `glab cluster` | [infrastructure.md](references/infrastructure.md) | agent management |
| Repo/Project | `glab repo` | [infrastructure.md](references/infrastructure.md) | view, search, clone, fork, create, members |
| Auth | `glab auth` | [infrastructure.md](references/infrastructure.md) | login, logout, status |
| Config | `glab config` | [infrastructure.md](references/infrastructure.md) | get, set |

## Common Workflow Examples

### Create MR from current branch

```bash
# Push and create MR with commit info, skip prompts
glab mr create --fill --fill-commit-body --target-branch main --yes

# With labels and reviewers
glab mr create --fill --target-branch main --label "review-needed" --reviewer username --yes
```

### Check pipeline status

```bash
# Current branch pipeline as JSON
glab ci status -F json

# List recent pipelines
glab ci list -F json --per-page 5
```

### View and comment on MR

```bash
# View MR details
glab mr view 123 -F json

# View MR diff
glab mr diff 123

# Add comment
glab mr note 123 -m "LGTM, approved."
```

### Create an issue

```bash
glab issue create --title "Bug: login fails on SSO" --description "Steps to reproduce..." --label bug --yes
```

### Direct API call

```bash
# GET project details (auto-fills :id from current repo)
glab api projects/:id -F json

# POST with fields
glab api projects/:id/issues --method POST -f title="New issue" -f labels="bug"
```

## Global Flags

| Flag | Description |
|------|-------------|
| `-R, --repo OWNER/REPO` | Target a different project |
| `-F, --output json\|text` | Output format (prefer `json`) |
| `-h, --help` | Command help |
| `-p, --page N` | Page number for list commands |
| `-P, --per-page N` | Items per page (default varies: 20-30) |

## Anti-Patterns

- **Do not** use `glab ci view` — it's a TUI that requires keyboard interaction.
- **Do not** omit `--yes` on create/merge commands — they block on interactive prompts.
- **Do not** use `--web` flags — agents cannot interact with browsers.
- **Do not** parse text output with regex — use `-F json` and parse structured data.
- **Do not** use `glab mr create` without `--push` or `--fill` if the branch isn't pushed yet.
