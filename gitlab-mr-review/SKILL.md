---
name: gitlab-mr-review
description: >
  Review GitLab merge requests by analyzing diffs and posting signed review comments.
  Use this skill whenever the user asks to review an MR, review a merge request, check code
  on a GitLab PR, do a code review, or wants feedback on changes in a GitLab project.
  Also trigger when the user says "review my changes", "check this MR", "look at the diff",
  "code review", or asks for feedback before merging. Posts comments signed with the
  invoking tool and model name for transparency.
---

# GitLab MR Review

Review GitLab merge requests by analyzing diffs and posting structured, signed review comments.

## Prerequisites

- `glab` CLI authenticated (`glab auth status`)
- Project linked to a GitLab remote (auto-detected from git config)

## Comment Signature

Every review comment must end with a signature block:

```markdown
---

*Reviewed by **{tool-name}** using `{model-name}`*
```

**Determining the tool name:** Check the environment for context clues:

- If running in CommandCode: `CommandCode`
- If running in Claude Code: `Claude Code`
- If running in Pi: `Pi`
- If running in Cursor: `Cursor`
- If running in Windsurf: `Windsurf`
- If running in Cline: `Cline`
- If uncertain: use the shell `$PROGRAMNAME` env var or fall back to `AI Agent`

**Determining the model name:** Use the model powering the current session. If uncertain: check env vars (`$CLAUDE_MODEL`, `$ANTHROPIC_MODEL`, `$MODEL`), then fall back to omitting the model

## Review Workflow

### 1. Identify the Target MR

```bash
# Current branch's MR
glab mr view -F json

# By MR number
glab mr view 123 -F json

# List open MRs to find one
glab mr list -F json --per-page 10
```

### 2. Fetch the Diff

```bash
# Full diff for analysis
glab mr diff <mr-number> --color=never > /tmp/mr-diff.txt

# Also get MR metadata for context
glab mr view <mr-number> -F json > /tmp/mr-meta.json
```

Read the diff file rather than piping — large diffs need careful analysis.

### 3. Analyze the Changes

Review the diff against the requested review focus (see below). Focus on changed code, not untouched files.

### 4. Post Review Comments

**Rule: Comment format depends on whether the finding targets specific code or spans across files.**

#### Code-Specific Findings (single file, specific line)

For each actionable finding tied to a file and line, post an inline diff comment using `glab mr note create`:

```bash
# Code-related comment on a specific line
glab mr note create <mr-number> \
  --file path/to/file.ts \
  --line 42 \
  -m "Avoid swallowing errors here — log the exception before rethrowing.

---
*Reviewed by **[AI_TOOL]** using `[MODEL]`*"
```

Use `--line N:M` for a line range, and `--old-line N` for commenting on removed lines. Omitting both `--line` and `--old-line` places a file-level comment.

**Keep code-specific comments atomic:** one finding per comment. If there are two separate issues on the same line, post two comments.

#### Cross-Cutting / Non-Code Findings

For findings that span multiple files, are architectural concerns, or aren't tied to a specific line, use a task-list summary note with `- [ ]` checkboxes:

```bash
cat > /tmp/review-summary.md << 'EOF'
## Code Review — Cross-Cutting Items

- [ ] **Auth middleware is duplicated across 3 files.** Extract to a shared `auth.ts` module.
- [ ] **Error responses lack consistent format.** Define a standard error envelope used by all handlers.
- [ ] **Logging level is set to `debug` in production config.** Switch to `info` or `warn`.

### Positive

- Clean separation of routes and handlers
- Good test coverage on new endpoints

---
*Reviewed by **[AI_TOOL]** using `[MODEL]`*
EOF

glab api "projects/:id/merge_requests/<mr-number>/notes" \
  --method POST \
  --field "body=@/tmp/review-summary.md" \
  --output json
```

**Use `glab api` for multi-line comments** — inline `-m` doesn't support markdown well for longer content. Only use `-m` for short inline diff comments that fit on one or two lines.

### 5. Summary Note

After posting individual findings, add a summary note to the MR:

```bash
cat > /tmp/review-summary.md << 'EOF'
## Code Review Summary

### Critical Issues
- Issue 1 description
- Issue 2 description

### Important Issues
- Issue 1 description

### Suggestions
- Suggestion 1

### Positive Observations
- What's done well

---
*Reviewed by **[AI_TOOL]** using `[MODEL]`*
EOF

glab api "projects/:id/merge_requests/<mr-number>/notes" \
  --method POST \
  --field "body=@/tmp/review-summary.md" \
  --output json
```

## Review Aspects

Focus the review based on what the user requests or what's relevant to the changes.

### `code` — General Code Review (default, always applicable)

Review for:

- Logic errors, bugs, edge cases
- Code clarity and readability
- Naming consistency with project conventions
- Security concerns (injection, auth bypass, data exposure)
- Performance issues (N+1 queries, unnecessary allocations, blocking I/O)
- Missing error handling at system boundaries

Confidence scoring (0-100):

- 91-100: Critical bug or security issue — must fix
- 80-90: Important issue — should fix
- Below 80: Skip unless specifically asked

### `tests` — Test Coverage

Review for:

- Critical paths without test coverage
- Missing edge cases and boundary conditions
- Tests that test implementation instead of behavior
- Brittle assertions tied to internal details
- Missing negative/error test cases

Rate gaps 1-10 (10 = critical, must add before merge).

### `errors` — Error Handling

Review for:

- Silent failures in catch blocks
- Broad exception catching that hides unrelated errors
- Missing error logging or user feedback
- Fallback behavior that masks real problems
- Empty catch blocks (never acceptable)

Severity: CRITICAL (silent failure), HIGH (poor message), MEDIUM (missing context).

### `comments` — Comment Accuracy

Review for:

- Comments that don't match the actual code
- Outdated documentation referencing old behavior
- Comments that just restate obvious code (remove them)
- Missing documentation for complex logic
- Misleading or ambiguous phrasing

### `simplify` — Code Simplification

Review for:

- Unnecessary complexity and deep nesting
- Redundant code that could be consolidated
- Overly clever one-liners that hurt readability
- Dead code or unreachable branches
- Inconsistent patterns with the rest of the codebase

Preserve all functionality — only improve clarity.

## When to Use Each Aspect

| Scenario | Aspects |
| ---------- | --------- |
| General review request | `code` |
| "Review my tests" | `tests` |
| "Check error handling" | `errors` |
| "Are the comments accurate?" | `comments` |
| "Simplify this" | `simplify` |
| "Full review before merge" | `code`, `tests`, `errors` |
| "Comprehensive review" | all aspects |

## Handling Large Diffs

For diffs over ~500 lines, spawn subagents to parallelize the review:

1. **Identify file groups.** Split the changed files into logical clusters by domain (e.g., auth, API routes, models, tests).
2. **Spawn one subagent per group.** Each subagent reviews its assigned files independently, posting `--file`/`--line` comments for code-specific findings.
3. **Aggregate cross-cutting findings.** After all subagents finish, review their output for patterns that span groups and post a single `- [ ]` task-list summary note.
4. **If any subagent finds a critical issue, flag it immediately** — don't wait for all subagents to finish.

Subagents should be given clear, focused prompts:

```text
Review only {file-group} in MR !{mr-number}. Post atomic inline comments
using `glab mr note create <mr-number> --file <path> --line <N> -m "..."`.
Report cross-cutting concerns back for the aggregate summary.
```

## What NOT to Review

- Generated code (minified files, auto-generated bindings)
- Vendored dependencies
- Lock files (package-lock.json, go.sum)
- Configuration files with only format changes
- Trivial formatting-only changes (whitespace, line endings)

## Error Handling

If `glab` commands fail:

- Check auth: `glab auth status`
- Check repo link: `glab repo view -F json`
- Verify the MR exists: `glab mr list -F json`
- For API errors, check the HTTP status and response body

If the diff is empty or the MR is already merged, inform the user and stop.
