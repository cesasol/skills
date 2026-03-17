# Merge Requests

Complete reference for `glab mr` — create, review, merge, and manage merge requests.

## Table of Contents

- [Create](#create)
- [List](#list)
- [View](#view)
- [Diff](#diff)
- [Merge](#merge)
- [Approve / Revoke](#approve--revoke)
- [Comment (Note)](#comment-note)
- [Update](#update)
- [Rebase](#rebase)
- [Checkout](#checkout)
- [Other Operations](#other-operations)

## Create

```bash
# Minimal: push + create from commits (non-interactive)
glab mr create --fill --target-branch main --yes

# Full options
glab mr create \
  --title "feat: add OAuth support" \
  --description "Implements OAuth2 flow for SSO integration" \
  --target-branch main \
  --source-branch feat/oauth \
  --label "feature,auth" \
  --assignee myuser \
  --reviewer reviewer1,reviewer2 \
  --milestone "v2.0" \
  --draft \
  --squash-before-merge \
  --remove-source-branch \
  --yes

# Fill title from commits, fill description with commit bodies
glab mr create --fill --fill-commit-body --target-branch main --yes

# Create MR for an existing issue (copies issue title if --title omitted)
glab mr create --related-issue 42 --copy-issue-labels --fill --yes

# Create as draft
glab mr create --fill --draft --target-branch main --yes

# Push branch and create MR in one step
glab mr create --fill --push --target-branch main --yes
```

### Key flags

| Flag | Description |
|------|-------------|
| `-f, --fill` | Use commit info for title/description, auto-push. **Required for non-interactive.** |
| `--fill-commit-body` | Include all commit bodies in description (with `--fill`) |
| `-t, --title` | MR title |
| `-d, --description` | MR description (use `-` to open editor — avoid in agent context) |
| `-b, --target-branch` | Target branch (defaults to project default branch) |
| `-s, --source-branch` | Source branch (defaults to current branch) |
| `-l, --label` | Labels (comma-separated or repeat flag) |
| `-a, --assignee` | Assignees by username (comma-separated or repeat flag) |
| `--reviewer` | Reviewers by username (comma-separated or repeat flag) |
| `-m, --milestone` | Milestone ID or title |
| `--draft` | Mark as draft |
| `--squash-before-merge` | Squash on merge (true/false/omit for project default) |
| `--remove-source-branch` | Delete branch after merge (true/false/omit for project default) |
| `--allow-collaboration` | Allow commits from other members |
| `--push` | Push the branch before creating MR |
| `-i, --related-issue` | Link to issue (uses issue title if `--title` not set) |
| `--copy-issue-labels` | Copy labels from linked issue |
| `-y, --yes` | Skip confirmation prompt |

## List

```bash
# Open MRs (default)
glab mr list -F json

# All MRs including closed/merged
glab mr list --all -F json

# My MRs (as assignee)
glab mr list --assignee=@me -F json

# MRs I need to review
glab mr list --reviewer=@me -F json

# Filter by label
glab mr list --label needs-review -F json

# Exclude labels
glab mr list --not-label waiting-maintainer-feedback -F json

# Filter by source or target branch
glab mr list --source-branch feat/oauth -F json
glab mr list --target-branch main -F json

# Search by text
glab mr list --search "OAuth" -F json

# Merged MRs
glab mr list --merged -F json

# Closed MRs
glab mr list --closed -F json

# Draft MRs only
glab mr list --draft -F json

# Non-draft only
glab mr list --not-draft -F json

# By author
glab mr list --author someuser -F json

# Date filters
glab mr list --created-after 2025-01-01 -F json
glab mr list --deployed-after 2025-01-01 --environment production -F json

# Ordering
glab mr list --order updated_at --sort desc -F json

# Pagination
glab mr list --page 2 --per-page 10 -F json
```

### Key flags

| Flag | Description |
|------|-------------|
| `-A, --all` | All states |
| `-a, --assignee` | Filter by assignee username(s) |
| `-r, --reviewer` | Filter by reviewer username(s) |
| `--author` | Filter by author username |
| `-l, --label` | Filter by label(s) |
| `--not-label` | Exclude by label(s) |
| `--search` | Text search in title/description |
| `-d, --draft` | Draft MRs only |
| `--not-draft` | Non-draft only |
| `-M, --merged` | Merged only |
| `-c, --closed` | Closed only |
| `-s, --source-branch` | Filter by source branch |
| `--target-branch` | Filter by target branch |
| `-o, --order` | Order by: `created_at`, `updated_at`, `merged_at`, `title`, `priority`, `label_priority`, `milestone_due`, `popularity` |
| `-S, --sort` | Sort direction: `asc` or `desc` |

## View

```bash
# By ID
glab mr view 123 -F json

# By branch name
glab mr view feat/oauth -F json

# Include comments
glab mr view 123 --comments -F json

# Only unresolved discussions
glab mr view 123 --unresolved -F json

# Only resolved discussions
glab mr view 123 --resolved -F json

# Include system logs
glab mr view 123 --system-logs -F json
```

## Diff

```bash
# View changes
glab mr diff 123

# Current branch MR
glab mr diff

# Raw diff (pipeable)
glab mr diff 123 --raw

# No color (for processing)
glab mr diff 123 --color=never
```

## Merge

```bash
# Merge MR by ID
glab mr merge 123 --yes

# Squash and merge
glab mr merge 123 --squash --yes

# Custom merge commit message
glab mr merge 123 --message "Merge feat/oauth into main" --yes

# Rebase then merge
glab mr merge 123 --rebase --yes

# Remove source branch after merge
glab mr merge 123 --remove-source-branch --yes

# Squash with custom message
glab mr merge 123 --squash --squash-message "feat: OAuth support (#123)" --yes

# Auto-merge (merge when pipeline succeeds)
glab mr merge 123 --auto-merge --yes

# Safety: only merge if HEAD matches expected SHA
glab mr merge 123 --sha abc123def --yes

# Merge MR from current branch
glab mr merge --yes
```

## Approve / Revoke

```bash
# Approve by MR ID
glab mr approve 123

# Approve multiple
glab mr approve 123 456

# Approve by branch name
glab mr approve feat/oauth

# Approve with SHA check
glab mr approve 123 --sha abc123def

# Approve current branch's MR
glab mr approve

# Revoke approval
glab mr revoke 123

# List eligible approvers
glab mr approvers 123
```

## Comment (Note)

```bash
# Add comment
glab mr note 123 -m "Looks good, just one suggestion on line 42."

# Comment on current branch's MR
glab mr note -m "LGTM"

# Unique comment (skip if identical comment exists)
glab mr note 123 -m "CI passed" --unique

# Resolve a discussion by note ID
glab mr note 123 --resolve 3107030349

# Unresolve a discussion
glab mr note 123 --unresolve 3107030349
```

## Update

```bash
# Update title
glab mr update 123 --title "feat: OAuth2 support"

# Update description
glab mr update 123 --description "Updated implementation plan"

# Add/change labels
glab mr update 123 --label "approved,ready-to-merge"

# Change assignees
glab mr update 123 --assignee newuser

# Remove draft status
glab mr update 123 --draft=false

# Mark as draft
glab mr update 123 --draft

# Change target branch
glab mr update 123 --target-branch develop

# Lock discussion
glab mr update 123 --lock-discussion

# Set milestone
glab mr update 123 --milestone "v2.0"
```

## Rebase

```bash
# Rebase MR source branch onto target
glab mr rebase 123

# Rebase and skip CI
glab mr rebase 123 --skip-ci
```

## Checkout

```bash
# Checkout MR locally by ID
glab mr checkout 123

# By branch name
glab mr checkout feat/oauth

# By URL
glab mr checkout https://gitlab.com/group/project/-/merge_requests/123

# Set a custom local branch name
glab mr checkout 123 --branch local-review-branch
```

## Other Operations

```bash
# Close MR
glab mr close 123

# Reopen MR
glab mr reopen 123

# Delete MR
glab mr delete 123

# Subscribe to MR notifications
glab mr subscribe 123

# Unsubscribe
glab mr unsubscribe 123

# Add to your GitLab to-do list
glab mr todo 123

# Get issues related to MR
glab mr issues 123

# Create MR for an issue
glab mr for --related-issue 42 --yes
```
