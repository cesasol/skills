---
name: gitlab-workflow
description: >
  Use when working on normal single-branch GitLab Flow tasks with glab: create or update a merge
  request, start one MR from an issue, review an MR, check pipeline status, break one issue into
  tasks, or write GitLab Flavored Markdown for issues/MRs. Do not use for parallel implementation
  of multiple independent features with separate worktrees and one draft MR per item.
---

# GitLab Workflow

Follow GitLab Flow for ordinary single-branch collaboration: issues, feature branches, MRs, reviews, and pipelines using the `glab` CLI.

**Prerequisite:** The `glab` skill must be available. Read its `SKILL.md` and relevant reference files when you need detailed command flags.

## Choose the right workflow

Use this skill for one issue, one branch, or one MR at a time.

| User intent | Use this skill? | What to do |
| --- | ---: | --- |
| Create/update/review one MR | Yes | Follow the MR workflow below |
| Start work from one issue | Yes | Create one branch and one MR |
| Check pipeline status or failed jobs | Yes | Use the CI status recipes below |
| Break one issue into a task list | Yes | Update the issue with GLFM task items |
| Write GLFM for an issue/MR | Yes | Use this skill and read the GLFM reference if needed |
| Implement multiple independent feature requests in parallel | No | Use a separate orchestration workflow with isolated worktrees and one draft MR per item |
| Create separate worktrees, branches, docs/workitems, and draft MRs for many items | No | Use a parallel worktree dispatch workflow instead |
| Generate or rewrite `.gitlab-ci.yml` | No | Use a GitLab CI pipeline-generation workflow |

If the user says "these features", "in parallel", "separate worktrees", or asks for one MR per item, do not continue with this single-branch workflow.

## GitLab Flow at a Glance

GitLab Flow uses `main` as the single default branch. All feature work happens on short-lived
feature branches that merge directly back into `main`. Environment-specific branches
(`staging`, `production`) and release branches (`v1.x`, `v2.x`) are optional add-ons, not
required for every project.

```text
main ────●────●────●────●────●────●  (always deployable)
          \   /    \   /    \
   feat/a──●─●      ●──●    feat/b──●──●
```

The philosophy:

- **Small MRs** — Each MR represents one logical change. Small MRs are reviewed faster and
  merged with fewer conflicts.
- **Feature branches** — Branch from `main`, merge back to `main`.
- **Issue-driven** — Every branch and MR ties back to an issue. Use GitLab references to
  link them.
- **CI validates everything** — The pipeline must pass before merging.

## The Standard Workflow

When a user asks to work on one GitLab issue or branch, follow this sequence. Skip steps that are already done, but verify before skipping. For multiple independent work items, stop and use a parallel
worktree orchestration workflow instead.

### Phase 1: Plan

1. **Ensure there's an issue.** If the user mentions work without an issue, create one:

   ```bash
   glab issue create --title "Descriptive title" --description "..." --label "relevant-label" --yes
   ```

   Use GLFM in descriptions — see `references/glfm-cheatsheet.md` for syntax.

2. **Break work into tasks** (when appropriate). If an issue is large, add task list items
   in the description:

   ```markdown
   - [ ] Research approach
   - [ ] Implement core logic
   - [ ] Add tests
   - [ ] Update docs
   ```

   Tasks can be promoted to full work items in GitLab (the UI offers "Convert to child item"
   on hover). Mention this to the user when a task list item grows complex enough to warrant
   its own tracking.

3. **Assign and label.** Set milestone, assignee, weight, and labels so the issue appears
   on boards and filters correctly.

### Phase 2: Develop

1. **Create a feature branch from `main`.**
   Branch naming convention: `<type>/<issue-ref>-<short-description>`.
   Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

   ```bash
   git checkout -b feat/42-oauth-login main
   ```

2. **Write code, commit often.** Use [conventional commits](https://www.conventionalcommits.org/):

   ```text
   feat(auth): add OAuth token exchange
   fix(auth): handle expired refresh tokens
   test(auth): add OAuth flow integration tests
   ```

   Push frequently — this triggers CI early and backs up your work.

### Phase 3: Create the Merge Request

1. **Check for an MR template.** GitLab resolves templates in this order:
   1. Project UI setting
   2. Group `default.md`
   3. Instance `default.md`
   4. Project `default.md`
   To check, look for `.gitlab/merge_request_templates/` in the repo or a template
   configured in project settings. If a template exists, follow its structure.

2. **Create the MR.** Push the branch, then:

   ```bash
   # From the feature branch — auto-fills title from commits, links to issue
   glab mr create --fill --fill-commit-body --target-branch main --yes
   ```

   Or with full control:

   ```bash
   glab mr create \
     --title "feat: OAuth login support" \
     --description "..." \
     --target-branch main \
     --label "feature,frontend" \
     --assignee @me \
     --reviewer reviewer-user \
     --related-issue 42 \
     --yes
   ```

3. **Write a strong MR description in GLFM.** A good MR description includes:
   - **What** this change does (summary)
   - **Why** it's needed (link to issue with `#123` or `Closes #123`)
   - **How** it was implemented (approach, key decisions)
   - **Testing** instructions (how to verify)
   - **Screenshots** or screen recordings (if UI changes)

   See `references/glfm-cheatsheet.md` for the Markdown to make descriptions clear and
   well-structured.

### Phase 4: CI/CD

1. **Watch the pipeline:**

   ```bash
   glab ci status -F json
   glab ci list --branch feat/42-oauth-login -F json
   ```

2. **If a job fails**, get the trace:

   ```bash
   glab ci trace <job-id>
   ```

   Fix the issue, amend or create a new commit, and push again.

### Phase 5: Review

1. **Check MR status:**

   ```bash
   glab mr view <mr-id> -F json --comments
   ```

2. **Address feedback.** Push new commits to the same branch — the MR updates automatically.

3. **Resolve threads** when they're addressed:

   ```bash
   glab mr note <mr-id> --resolve <discussion-id>
   ```

4. **Approve** (if you're a reviewer):

   ```bash
   glab mr approve <mr-id>
   ```

### Phase 6: Merge

Once all threads are resolved, approvals are in place, and the pipeline passes:

```bash
glab mr merge <mr-id> --yes
```

Use `--squash` if the branch has messy commit history, `--remove-source-branch` to clean up.

## Primary Use Cases

These are the most common tasks for this skill. Keep the workflow scoped to one branch/MR unless the user explicitly asks for orchestration across multiple worktrees.

### Create MR from this branch

When the user is on a feature branch and wants to create an MR:

1. Check what branch they're on and what issue it relates to (look at branch name, recent
   commits, or ask the user).
2. Look for an MR template (see Phase 3, step 1 above).
3. Inspect the diff (`git diff main...HEAD --stat`) to understand what changed.
4. Build a description using the diff context and the template structure (if one exists).
   Use GLFM for formatting.
5. Run `glab mr create` with appropriate flags. Use `--fill` for quick MRs, or
   `--title`/`--description` for crafted ones.

### Update MR description

When the user asks to update an MR description:

1. Get the current MR: `glab mr view <id> -F json`.
2. Evaluate what changed: `git diff main...HEAD --stat` or `glab mr diff <id>`.
3. Check if a template exists and whether the current description follows it.
4. Rewrite the description to reflect the current state of the branch and the template.
5. Apply: `glab mr update <id> --description "..."`.

### Break down this issue into tasks

When the user wants to decompose an issue:

1. Read the issue: `glab issue view <id> -F json --comments`.
2. Analyze the requirements and identify discrete, independently verifiable units of work.
3. Write a task list in GLFM using `- [ ]` items.
4. If the task list goes in the issue description:

   ```bash
   glab issue update <id> --description "..."
   ```

5. Remind the user that each task list item can be converted to a full task work item in
   the GitLab UI ("Convert to child item" on hover).

### Start MR from issue

When the user says "start MR from issue #123":

1. Read the issue: `glab issue view <id> -F json`.
2. Create a branch following the naming convention:

   ```bash
   git checkout -b feat/<id>-<slug> main
   ```

3. Make the initial commit (at minimum, something that references the issue).
4. Push and create the MR linked to the issue:

   ```bash
   glab mr create --fill --related-issue <id> --copy-issue-labels --target-branch main --yes
   ```

### Review MR / Review MR !123

When the user wants to review a specific MR:

1. Get MR details: `glab mr view <id> -F json --comments`.
2. View the diff: `glab mr diff <id>`.
3. Check pipeline status: `glab ci status --branch <source-branch> -F json`.
4. Evaluate: code quality, test coverage, alignment with issue requirements, security
   concerns, performance implications.
5. Provide feedback as comments or summary:
   - For inline feedback: note specific files and lines
   - For overall review: use `glab mr note <id> -m "..."` with a summary and
     recommendation (approve / request changes / comment)
6. If approving: `glab mr approve <id>`.

### Check pipeline / CI status

```bash
glab ci status -F json               # current branch
glab ci status --branch main -F json # specific branch
glab ci list -F json --per-page 5    # recent pipelines
```

## Gotchas and common mistakes

- Do not use this skill to fan out multiple feature implementations. That workflow needs isolated worktrees and one branch/MR per item.
- Do not use this skill to author full GitLab CI pipelines; use a pipeline-generation workflow for `.gitlab-ci.yml` generation or refactoring.
- Prefer draft MRs when work is not review-ready; a visible draft MR still gives CI and reviewers early context.
- Never merge solely because local tests pass. Check GitLab pipeline status and unresolved threads first.
- Preserve MR/issue templates when they exist; they encode project review expectations.

## Example Interaction

User: "Start work on issue #42 and open a draft MR."

Agent flow:

1. Read the issue with `glab issue view 42 -F json`.
2. Create `feat/42-short-slug` from `main`.
3. Make or guide the initial changes, commit with a Conventional Commit message, and push.
4. Create a draft MR with `glab mr create --draft --fill --related-issue 42 --yes`.
5. Return the MR URL and current pipeline status.

## GLFM Quick Reference

When writing issue/MR descriptions and comments, always use GitLab Flavored Markdown.
The full reference is in `references/glfm-cheatsheet.md`. Here are the essentials:

**GitLab-specific references:**

| Syntax | Renders as |
| -------- | ----------- |
| `#123` | Link to issue #123 |
| `!456` | Link to MR !456 |
| `&789` or `[epic:789]` | Link to epic |
| `@username` | Mention a user |
| `~bug` | Link to label "bug" |
| `%v2.0` | Link to milestone |
| `9ba12248` | Link to commit |

**Linking and closing:**

```markdown
Closes #123 # auto-close issue when MR merges
Related to #456 # link without closing
```

**Task lists:**

```markdown
- [x] Done
- [~] Not applicable
- [ ] Pending
```

**Show titles and summaries:**

```markdown
# 123+ # renders as: Issue Title (#123)

## 123+s    # renders with assignee, milestone, health status
```

**Structure helpers:**

```markdown
[[_TOC_]]            # auto-generated table of contents
> [!note]            # alert callout (also: [!tip], [!important], [!warning], [!caution])
```

For tables, diagrams (Mermaid/PlantUML), math, colors, collapsible sections, and
other advanced GLFM features, read `references/glfm-cheatsheet.md`.

## Tips for Effective GitLab Flow

- **Keep MRs small.** If you find yourself writing "and also..." in the description,
  split it into two MRs.
- **Push early, push often.** A draft MR that CI can see is better than a perfect
  local branch nobody knows about.
- **Use drafts** (`--draft` flag) for work-in-progress MRs that aren't ready for
  full review. Remove draft status when ready.
- **Squash wisely.** Squash when the commit history is messy. Keep individual commits
  when each one is meaningful and well-described.
- **Link everything.** Every MR should reference an issue. Every issue should have
  a milestone (when release planning). Use `#ref` and `!ref` liberally.
- **Read the pipeline.** The CI pipeline is your safety net. Never merge with failing
  checks (unless it's a known flaky test with an issue filed).
- **Resolve threads before merging.** Open threads block merging (if the project
  setting is enabled). Address or move them to an issue.
- **Clean up branches.** Use `--remove-source-branch` on merge, or delete manually
  afterward. Stale branches create confusion.
