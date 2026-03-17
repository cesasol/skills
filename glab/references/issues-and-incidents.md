# Issues and Incidents

Complete reference for `glab issue` and `glab incident`.

## Table of Contents

- [Issues — Create](#issues--create)
- [Issues — List](#issues--list)
- [Issues — View](#issues--view)
- [Issues — Comment](#issues--comment)
- [Issues — Update](#issues--update)
- [Issues — Other Operations](#issues--other-operations)
- [Issues — Board](#issues--board)
- [Incidents](#incidents)

## Issues — Create

```bash
# Basic issue
glab issue create --title "Bug: login fails" --description "Steps to reproduce..." --yes

# With labels and assignee
glab issue create \
  --title "feat: add dark mode" \
  --description "Implement dark mode toggle in settings" \
  --label "feature,frontend" \
  --assignee myuser \
  --milestone "v2.0" \
  --yes

# Confidential issue
glab issue create --title "Security: XSS vulnerability" --confidential --label security --yes

# With due date
glab issue create --title "Release prep" --due-date 2025-06-01 --yes

# With time tracking
glab issue create --title "Refactor auth module" --time-estimate "3h" --yes

# With weight (for planning)
glab issue create --title "API redesign" --weight 5 --yes

# Link to existing MR
glab issue create --title "Fix CVE-2025-1234" --linked-mr 456 --label security --yes

# Link to other issues
glab issue create --title "Parent task" --linked-issues 10,11,12 --yes

# With epic
glab issue create --title "Sub-task" --epic 7 --yes
```

### Key flags

| Flag | Description |
|------|-------------|
| `-t, --title` | Issue title (required) |
| `-d, --description` | Description (use `-` for editor — avoid in agent context) |
| `-l, --label` | Labels (comma-separated or repeat) |
| `-a, --assignee` | Assignees by username |
| `-m, --milestone` | Milestone ID or title |
| `-c, --confidential` | Mark as confidential |
| `--due-date` | Due date in `YYYY-MM-DD` format |
| `-e, --time-estimate` | Time estimate (e.g., `3h`, `1d`) |
| `-s, --time-spent` | Time already spent |
| `-w, --weight` | Issue weight (>= 0) |
| `--epic` | Epic ID to add issue to |
| `--linked-issues` | IIDs of issues to link |
| `--linked-mr` | MR IID to link |
| `--link-type` | Link type (default: `relates_to`) |
| `-y, --yes` | Skip confirmation prompt |

## Issues — List

```bash
# Open issues (default)
glab issue list -F json

# All issues
glab issue list --all -F json

# My issues
glab issue list --assignee=@me -F json

# By label
glab issue list --label bug -F json

# Exclude labels
glab issue list --not-label "wontfix" -F json

# By milestone
glab issue list --milestone "v2.0" -F json

# Search by text
glab issue list --search "login" -F json

# Confidential only
glab issue list --confidential -F json

# By author
glab issue list --author someuser -F json

# Date filters
glab issue list --created-after 2025-01-01 -F json

# Ordering
glab issue list --order updated_at --sort desc -F json

# Pagination
glab issue list --page 1 --per-page 50 -F json

# Closed issues
glab issue list --closed -F json

# In a specific group (across projects)
glab issue list --group my-group -F json
```

## Issues — View

```bash
# By ID
glab issue view 42 -F json

# With comments
glab issue view 42 --comments -F json

# By URL
glab issue view https://gitlab.com/group/project/-/issues/42 -F json

# With system logs
glab issue view 42 --system-logs -F json
```

## Issues — Comment

```bash
# Add a comment
glab issue note 42 -m "This is fixed in MR !123."

# Multi-line (pass as string)
glab issue note 42 -m "Status update:
- Fixed the auth bug
- Added tests
- Ready for review"
```

## Issues — Update

```bash
# Update title
glab issue update 42 --title "Bug: login fails on SSO (updated)"

# Update description
glab issue update 42 --description "Updated reproduction steps..."

# Add labels
glab issue update 42 --label "in-progress"

# Remove labels
glab issue update 42 --unlabel "needs-triage"

# Change assignee
glab issue update 42 --assignee newuser

# Unassign
glab issue update 42 --unassign user1

# Set milestone
glab issue update 42 --milestone "v2.1"

# Lock discussion
glab issue update 42 --lock-discussion

# Mark confidential
glab issue update 42 --confidential
```

## Issues — Other Operations

```bash
# Close issue
glab issue close 42

# Reopen issue
glab issue reopen 42

# Delete issue
glab issue delete 42

# Subscribe to notifications
glab issue subscribe 42

# Unsubscribe
glab issue unsubscribe 42
```

## Issues — Board

```bash
# List boards
glab issue board list

# View a specific board
glab issue board view 1

# Create a board
glab issue board create --name "Sprint Board"
```

## Incidents

Incidents use a similar pattern to issues but with the `glab incident` command.

```bash
# List incidents
glab incident list -F json

# View an incident
glab incident view 15 -F json

# View with comments
glab incident view 15 --comments -F json

# Comment on incident
glab incident note 15 -m "Root cause identified: misconfigured DNS."

# Close an incident
glab incident close 15

# Reopen an incident
glab incident reopen 15

# Subscribe
glab incident subscribe 15

# Unsubscribe
glab incident unsubscribe 15
```

### Incident list filters

Same filters as issues: `--assignee`, `--label`, `--milestone`, `--author`, `--search`, `--confidential`, `--order`, `--sort`, `--page`, `--per-page`.
