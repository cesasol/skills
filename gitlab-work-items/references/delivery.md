# GitLab delivery reference

Read with `SKILL.md`. Reuse repository conventions before adding process.
GitLab documentation can describe upcoming releases: verify against the actual
instance, enabled features, subscription and permissions, not the docs landing
page alone. A feature listed under the work-item umbrella is not available for
every item type or namespace.

## Command and API selection

1. Read `glab --version`, `glab work-items --help` and the relevant command's
   `--help`. Newer CLIs have native `list`, `create` and `update` commands;
   installed glab 1.124.0 labels this command family experimental. Older CLIs may
   lack it. Native coverage does not imply every widget has a flag.
2. Select scope explicitly: `--repo group/project` for project work or
   `--group group/subgroup` for group work. These are alternatives, not combined
   flags. Use the item's owning namespace, not merely the current checkout.
3. For a genuine project issue, `glab issue` or the Issues REST API remains
   appropriate. Tasks and group items are not interchangeable with project issues.
4. For an uncovered operation, query the instance through `glab api graphql`.
   Inspect namespace work-item types, item widgets, allowed parent types and
   permissions; resolve real global IDs rather than constructing them from IIDs.
   Verify query/mutation names and input fields against the instance schema or
   version-matched API reference. Use variables for user content. Inspect both
   top-level GraphQL `errors` and mutation payload `errors`; HTTP 200 alone is
   not success. Re-fetch the changed field or relationship.
5. If neither API nor permissions supports the action, state the limitation and
   provide a supported UI/manual step. Do not install or upgrade tools silently.

Run network commands with bounded timeouts, explicit host/scope, complete
non-interactive inputs and machine-readable output when supported. Follow
pagination (`--after` cursors for native work-item lists; connection cursors for
GraphQL; REST pagination) before claiming a complete search. Do not retry an
ambiguous create response blindly: search for the created object first.

Current native update help exposes assignee, description-file, milestone,
iteration and weight, but not generic parent, blocker or status flags. Recheck
help at execution time instead of inventing those flags. Write rich bodies to
files and use supported file inputs; for API JSON specify the content type
explicitly for compatibility with older glab versions. Read the `glab` skill for
notes, threaded replies and uploads rather than duplicating those rules here.

## Planning fields and features

| Need | Use when supported | Semantics and fallback |
| --- | --- | --- |
| Outcome breakdown | Epic → issues → tasks; child-item widgets | Parentage is containment, not a dependency. Verify allowed types, scope and hierarchy depth. A checklist is a lightweight fallback, not an independently assigned work item. |
| Delivery dependency | Linked items: blocks / is blocked by | State direction: “B is blocked by A.” Verify both endpoints and avoid cycles. `relates to` is non-blocking; a text link does not enforce a dependency. |
| Responsibility | Assignee, reviewers, participants | Choose an accountable owner; a reviewer is not the implementation owner. Preserve existing assignments unless a change is requested. |
| Release scope | Milestone | A release or delivery grouping, potentially across projects. Confirm its scope; do not invent a milestone to match a branch name. |
| Sprint cadence | Group iteration/cadence | A timebox, distinct from a release milestone; both can be useful together. If unavailable, record the timebox in agreed text, without calling it a native iteration. |
| Workflow visibility | Existing native status/lifecycle, saved views and boards | Native status differs from open/closed state. If unavailable, reuse ordinary or scoped workflow labels supported by the instance; do not create a second conflicting lifecycle. |
| Priority and estimation | Existing labels, weights, custom fields | Reuse vocabulary and relative estimation. Feature availability varies. Do not manufacture precision or create fields without approval. |
| Scope consistency | Issue/MR description templates, quick actions | Inspect `.gitlab/issue_templates/` and `.gitlab/merge_request_templates/`. Quick actions execute mutations; verify support, permissions and resulting fields. |
| Safe integration | Draft MRs, reviewers, CODEOWNERS, approval rules, resolved threads | Assignment and a CODEOWNERS file alone do not prove enforced approval. Inspect actual rules and target-branch protections. |
| Change validation | MR pipelines, test/coverage reports, merged-results pipelines, merge trains | Use enabled features to test the proposed integration. A green source-branch pipeline may not test the merged result; verify pipeline type and commit SHA. |
| Delivery feedback | Review Apps/environments, deployment approvals, feature flags, releases | Separate review, merge and rollout. Use existing flags to decouple incomplete capability from release; include cleanup and rollback. |

Epics, iterations, directional links, custom statuses/fields, advanced review
controls and CI features have independent tier/version/type restrictions.
Missing permissions and missing product features are different blockers: report
which is known and which is unknown. Recommend the smallest useful feature set,
not every GitLab feature for every item.

## Branching decision and routing

First inspect CONTRIBUTING/architecture decisions, remote branches, release
tags, MR targets and CI deployment rules. Do not infer policy just because
`main` is the default branch. Preserve explicit policy; discuss migration as a
separate decision with its costs and required approvals.

| Project evidence | Recommendation when no policy exists | Tradeoff |
| --- | --- | --- |
| Frequent deploys, one current production line, fast automated checks | Trunk-based development: short-lived branches → protected trunk | Small integration batches; needs reliable checks and incomplete-feature isolation. Trunk need not mean direct pushes. |
| Scheduled releases, separate stabilization, parallel maintained versions | Consider Git Flow; compare trunk plus release/maintenance branches | Git Flow adds develop/release synchronization and more porting work. Multiple supported versions alone do not require develop. |
| Unknown release cadence, support policy or merge gates | Ask targeted questions before proposing branch creation | Language, framework, team size and “professionalism” are insufficient evidence. |

### Trunk-based routing

- Base a small branch on the current remote trunk; target trunk explicitly in
  the MR. Prefer roughly daily integration and a deployable trunk.
- Release tags and environments identify deployment; do not add `develop` or
  permanent environment branches as a prerequisite.
- If maintenance versions exist, use explicit supported release branches and
  reviewed backports. For production emergencies, follow the documented deployed
  revision/maintenance policy and reconcile the fix into trunk.

### Git Flow routing

- Feature: branch from `develop`, MR back to `develop`.
- Release: branch from `develop` to `release/<version>`; stabilize there. Finish
  through reviewed integration into `main` and reconciliation into `develop`;
  tag the production release according to repository policy.
- Hotfix: branch from the affected production tag/line, not unreleased develop.
  Target `main` for the current production line or its maintenance branch for an
  older affected version. Propagate into `develop`, affected active releases and
  every affected supported maintenance line through tracked MRs.
- Choose merge or traceable cherry-pick (for example `git cherry-pick -x`)
  according to repository policy and branch divergence. Never merge unreleased
  develop wholesale into a maintenance line. Verify whether a fix is already
  present before porting it, and re-test each affected line.

## Readiness and definition of done

An actionable item has: outcome/current behavior, acceptance checks, non-goals,
owner, dependencies, verification approach and delivery destination. For bugs,
include reproduction and regression coverage. For migrations or rollout risk,
include compatibility, observability and rollback. A blocked item is not ready
merely because it has a high priority; work on an authorized unblocker or ask.

Use a Draft MR early for collaboration, but one cohesive change per MR. Describe
why, full item URL, acceptance-check evidence, risks and rollout; use the existing
template. Keep discussions and decisions with the item/MR rather than only in
chat. Inspect previous notes before adding concise progress/blocker updates.

Automatic closing patterns normally act when changes reach the **default
branch**. A feature MR into `develop` does not by itself close its item when the
default is `main`. Inspect project automatic-closing configuration, actual item
support, MR closing links and commit messages. Do not promise automatic closure
for every work-item type or hierarchy. Native MR work-item links are an additional
version-dependent capability; verify their configured relationship and behavior.

When acceptance includes rollout or multiple release lines, use a non-closing
full-URL reference until those obligations are met. Track separately authorized
port/rollout items if the agreed definition of done permits earlier closure.
Check that a later release MR or commit does not accidentally close unrelated
or incomplete work. Re-read the final item status: a merged MR, a closed issue,
a release tag and a verified deployment are distinct observations.

## Worked example: a trunk-based API bug

Repository policy: protected `main`, daily deploys. Project issue 81 reproduces
a duplicate callback. Existing label `workflow::ready`; milestone `v2.4` means
release scope, iteration `Sprint 12` means the team's timebox. Owner and blocker
are confirmed. Acceptance: duplicate delivery changes the balance once; normal
callbacks remain valid. Existing CI, review and rollout gates apply.

After authorization, preserve unrelated edits and use an isolated branch based
on current remote `main`. Implement the regression check and focused fix using
repository commands. Discover current tracking support first:

```sh
# Read-only discovery; use the owning project's actual host and path.
glab work-items --help
glab work-items update --help
timeout 30 glab work-items list --repo acme/payments --type issue --output json
```

With a non-interactive MR body saved locally, create a Draft MR only after the
user authorizes pushing/creation (replace the example path and branch):

```sh
timeout 30 glab mr create --repo acme/payments --push \
  --source-branch fix/81-idempotent-callback --target-branch main \
  --title 'Draft: fix: handle repeated callbacks once' \
  --description "$(cat /tmp/callback-mr.md)"
```

The body contains `Related to https://gitlab.com/acme/payments/-/issues/81`,
regression results, pipeline evidence and rollback. This is deliberately
non-closing because acceptance includes deployment verification. Update only
requested tracking fields through verified commands, then re-read them. Once
required checks, authorized merge and deployment verification succeed, close
against the recorded acceptance evidence. If CI remains pending, report
`not complete`, the blocking gate and the next action rather than closing.

## Sources and refresh points

- [Work items and type/view evolution](https://docs.gitlab.com/user/work_items/)
- [Work-item status](https://docs.gitlab.com/user/work_items/status/)
- [Linked items](https://docs.gitlab.com/user/work_items/linked_items/)
- [Child items](https://docs.gitlab.com/user/work_items/child_items/)
- [Iterations](https://docs.gitlab.com/user/group/iterations/)
- [Automatic issue closing](https://docs.gitlab.com/user/project/issues/managing_issues/#closing-issues-automatically)
- [Branching strategies](https://docs.gitlab.com/user/project/repository/branches/strategies/)
- [GraphQL API usage and errors](https://docs.gitlab.com/api/graphql/getting_started/)

Refresh command claims against installed `glab` help; refresh feature claims
against version-matched documentation and the actual instance schema/widgets.
