---
name: gitlab-mr-review
description: >
  Review GitLab merge requests in isolated git worktrees and post signed review comments.
  Use this skill whenever the user asks to review an MR, review a merge request, check code
  on a GitLab PR, do a code review, or wants feedback on changes in a GitLab project.
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
# Current branch's MR with comments
glab mr view -c -F json | jq '{title, description, state, source_branch, target_branch, labels, Discussions}'

# By MR number
glab mr view -c 123 -F json | jq '{title, description, state, source_branch, target_branch, labels, Discussions}'

# List open MRs to find one
glab mr list -F json --per-page 10
```

### 2. Prepare an Isolated MR Worktree

Use `glab` only to read MR metadata and post comments. Fetch the MR's Git refs with `git`, then
review the source tree from a detached temporary worktree. **Do not use `glab mr diff`, the MR
changes API, `glab mr checkout`, or switch/reset the user's current worktree.**

```bash
# Save metadata and extract the refs to review.
glab mr view <mr-number> -F json > /tmp/mr-meta.json
MR_IID=$(jq -r '.iid' /tmp/mr-meta.json)
TARGET_BRANCH=$(jq -r '.target_branch' /tmp/mr-meta.json)

# Use the remote linked to the GitLab project. Override when it is not named origin.
ROOT=$(git rev-parse --show-toplevel)
REMOTE=${GITLAB_REMOTE:-origin}
RUN_ID="${MR_IID}-$$"
MR_HEAD_REF="refs/gitlab-mr-review/${RUN_ID}/head"
TARGET_REF="refs/gitlab-mr-review/${RUN_ID}/target"
WORKTREE_DIR="${TMPDIR:-/tmp}/gitlab-mr-review-${RUN_ID}"

# Fetch private temporary refs without altering local branches or remote-tracking branches.
git -C "$ROOT" fetch --no-tags "$REMOTE" \
  "+refs/merge-requests/${MR_IID}/head:${MR_HEAD_REF}" \
  "+refs/heads/${TARGET_BRANCH}:${TARGET_REF}"

# Materialize the exact MR head and calculate the comparison base locally.
git -C "$ROOT" worktree add --detach "$WORKTREE_DIR" "$MR_HEAD_REF"
BASE_SHA=$(git -C "$ROOT" merge-base "$TARGET_REF" "$MR_HEAD_REF")
```

Record `ROOT`, `WORKTREE_DIR`, `MR_HEAD_REF`, `TARGET_REF`, and `BASE_SHA`; they are needed throughout
the review and for cleanup. If another process is reviewing the same MR, use a distinct `RUN_ID`.

Inspect changes with local Git commands, always from the temporary worktree:

```bash
# Establish scope first.
git -C "$WORKTREE_DIR" diff --stat "$BASE_SHA"..HEAD
git -C "$WORKTREE_DIR" diff --name-status "$BASE_SHA"..HEAD
git -C "$WORKTREE_DIR" diff --check "$BASE_SHA"..HEAD

# Then inspect each relevant patch and its complete surrounding source.
git -C "$WORKTREE_DIR" diff "$BASE_SHA"..HEAD -- path/to/file.ts
```

Run all reads, searches, builds, and tests with `WORKTREE_DIR` as the working directory. This makes
the full MR source available for call-site tracing and test execution without disturbing the user's
checkout. Review only changes between `BASE_SHA` and `HEAD`, while using unchanged files for context.

### 3. Load Review References

Before analyzing, load the review references (see **House Rules** below):

1. **Always load** `references/house-rules.md` — language-agnostic enforced opinions.
2. **Load each matching stack reference** for every language present in the diff: `references/python.md` (pydantic), `references/typescript.md` (zod). One MR can touch multiple stacks — load all that
   match.

Enforce the house rules on every review regardless of the requested aspect.

### 4. Analyze the Changes

Review the local `BASE_SHA..HEAD` changes against the requested focus (see below). Use the complete files
and repository in `WORKTREE_DIR` to verify call sites, invariants, project conventions, and tests. Findings
must still be caused by the MR; do not report pre-existing issues in untouched code.

### 5. Post Review Comments

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

### 6. Summary Note

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

### 7. Clean Up the Worktree

The review is read-only. After all comments are posted—or after any failure occurring after worktree
creation—remove only the temporary worktree and refs created for this review:

```bash
git -C "$ROOT" worktree remove --force "$WORKTREE_DIR"
git -C "$ROOT" update-ref -d "$MR_HEAD_REF"
git -C "$ROOT" update-ref -d "$TARGET_REF"
git -C "$ROOT" worktree prune
```

Never delete or reset the user's existing branches or worktrees. Use `--force` only for the temporary
review worktree created above.

## House Rules (always enforced)

These opinions apply to every review, regardless of which aspect is requested. They live in `references/house-rules.md` (principles + rationale) plus per-stack files (concrete directives and code
patterns).

- **Always load** `references/house-rules.md` before analyzing the diff.
- **Load each matching stack reference** for every language present in the diff: `references/python.md` (pydantic patterns), `references/typescript.md` (zod patterns). One MR can touch multiple stacks
  — load all that match.
- Apply house rules at the same confidence scoring as the `code` aspect (80-90 important, 91-100 critical).
- Include the rule's one-line rationale in any comment posted for a house-rule violation.
- Do not apply house rules to generated/vendored code, test fixtures, or mock data (already excluded from review).

Adding a new enforced opinion: add the principle to `references/house-rules.md` and the concrete patterns to the relevant stack file under `references/`. Adding a new stack: create
`references/<lang>.md` with the concrete form of each existing house rule.

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

## Handling Large Changes

For changes over ~500 lines, spawn subagents to parallelize the review:

1. **Identify file groups locally.** Use `git -C "$WORKTREE_DIR" diff --name-only "$BASE_SHA"..HEAD`, then split files into logical clusters by domain (e.g., auth, API routes, models, tests).
2. **Share the worktree and base.** Give every subagent the absolute `WORKTREE_DIR`, `BASE_SHA`, MR number, and its assigned files. Subagents must not fetch the GitLab diff or create another checkout.
3. **Review assigned files.** Each subagent inspects its local patches plus relevant complete files and posts `--file`/`--line` comments for code-specific findings.
4. **Aggregate cross-cutting findings.** After all subagents finish, review their output for patterns that span groups and post a single `- [ ]` task-list summary note.
5. **If any subagent finds a critical issue, flag it immediately** — don't wait for all subagents to finish.

Subagents should be given clear, focused prompts:

```text
Review only {file-group} in MR !{mr-number}. The MR is already materialized at
{worktree-dir}; compare {base-sha}..HEAD locally and inspect full files there.
Do not fetch or checkout anything. Post atomic inline comments using
`glab mr note create <mr-number> --file <path> --line <N> -m "..."`.
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

If Git/worktree setup fails:

- Confirm `REMOTE` points to the target GitLab project: `git remote -v`
- Verify `TARGET_BRANCH` exists on that remote
- Verify the target project exposes `refs/merge-requests/<iid>/head`
- Remove any temporary worktree and refs already created before stopping
- Do not fall back to `glab mr diff` or the MR changes API

If `git diff --quiet "$BASE_SHA"..HEAD` reports no changes or the MR is already merged, inform the
user, clean up the temporary worktree/refs, and stop.
