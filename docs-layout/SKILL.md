---
name: docs-layout
description: >
  Use when setting up a project's `docs/` folder or deciding where a new decision,
  spec, plan, roadmap, runbook, report, handoff, wireframe, or reference document belongs
  and what to name it. Applies to both backend and frontend projects. Covers a shared
  spine plus project-type extras, with naming conventions for phased, dated, and flat files.
---

# docs-layout

## Overview

Use this skill to place documentation in a predictable `docs/` structure and choose filenames that communicate document lifecycle.
**Create folders only when adding the first file; never scaffold empty folders.** Naming conventions encode time semantics: phased files for ordered work, dated files for time-anchored events, and
flat names for living references.

## Placement workflow

1. Identify the document's lifecycle: decision, spec, implementation plan, roadmap, dated report, runbook, handoff, reference, brand asset, or wireframe.
2. Choose the destination from the placement table below.
3. Create only the needed parent folder.
4. Name the file with the convention for that folder.
5. If none of the categories fit, add a domain-specific folder only when it answers a clear lookup question.

## Layout

**Shared spine** — applies to every project:

```text
docs/
├── decisions/     # architectural decisions / trade-off rationale
├── specs/         # feature, product, and technical specifications
├── plans/         # implementation and execution plans
├── roadmap/       # phased multi-step roadmaps / product direction
├── reports/       # dated analyses, investigations, postmortems
├── runbooks/      # operational guides (deploy, rollback, recovery, routine ops)
└── reference/     # schemas, API contracts, long-lived reference material
```

**Backend extras** — add on top of the spine:

```text
docs/
└── handoffs/      # session-to-session handoffs (in-flight work, next steps)
```

**Frontend extras** — add on top of the spine:

```text
docs/
├── brand/         # brand guidelines, visual identity
└── wireframes/    # UX wireframes (locale-suffixed: .en.md, .es.md, ...)
```

## Placement table

| I want to add…                                 | Goes in       | Naming                              |
| ---------------------------------------------- | ------------- | ----------------------------------- |
| Architectural decision / trade-off rationale   | `decisions/`  | `YYYY-MM-DD-topic.md`               |
| Feature or technical specification             | `specs/`      | `topic.md` (flat kebab)             |
| Implementation or execution plan               | `plans/`      | `YYYY-MM-DD-topic.md` or `topic.md` |
| Phase of a multi-step roadmap                  | `roadmap/`    | `phase-N-topic.md`                  |
| Operational guide (deploy, rollback, recovery) | `runbooks/`   | `topic.md` (flat kebab)             |
| Dated analysis tied to a specific event        | `reports/`    | `YYYY-MM-DD-topic.md`               |
| Session-to-session handoff (backend only)      | `handoffs/`   | `YYYY-MM-DD-topic.md`               |
| Schema, API contract, reference material       | `reference/`  | `topic.md` (flat kebab)             |
| Brand guidelines (frontend only)               | `brand/`      | `topic.md` (flat kebab)             |
| UX wireframe (frontend only)                   | `wireframes/` | `feature-name.LOCALE.md`            |

## Naming conventions

- **Phase prefix** (`phase-N-topic.md`) — `roadmap/` only. Encodes ordered work within a roadmap. Flat inside the folder; only split into subfolders when multiple concurrent roadmaps exist.
- **ISO date prefix** (`YYYY-MM-DD-topic.md`) — `decisions/`, `reports/`, `handoffs/`, dated `plans/`. Chronological sort is the natural sort; no registry needed to avoid collisions.
- **Flat kebab-case** (`topic.md`) — `specs/`, `plans/`, `runbooks/`, `reference/`, `brand/`. Living documents and specifications; revisions happen in-place with git history as the audit trail. Date
  or number prefixes here imply staleness or ordering that don't apply unless the plan is dated.
- **Locale suffix** (`topic.LOCALE.md`) — `wireframes/` only. `en`, `es`, etc. Applied *after* the kebab slug, before the extension.

## Examples

- New architectural decision about queue technology → `docs/decisions/2026-05-08-queue-selection.md`
- Feature specification for user auth → `docs/specs/user-authentication.md`
- Implementation plan for auth refactor → `docs/plans/2026-05-10-auth-refactor.md`
- Multi-phase migration roadmap → `docs/roadmap/phase-1-schema-prep.md`, then `phase-2-cutover.md`
- Frontend checkout wireframe in Spanish → `docs/wireframes/checkout.es.md`

## Gotchas

- Put work-in-progress implementation tracking in `docs/workitems/` only when another workflow explicitly asks for workitems; it is not part of the shared spine.
- Do not move existing project docs just to match this layout unless the user asked for a docs reorganization. For a new file, follow this layout from now on.
- Prefer a short, descriptive slug over mirroring the full document title.

## Common mistakes

- **Naming the folder `adr/` with sequential `NNNN-` prefixes.** Use `decisions/` with ISO date prefix. Sequential numbering requires a registry to avoid collisions across concurrent branches; dates
  don't.
- **Confusing `plans/` and `roadmap/`.** Use `plans/` for feature/task implementation plans; use `roadmap/` for multi-phase high-level product roadmaps.
- **Nesting every plan or spec in its own subfolder.** Flat files inside `plans/` and `specs/` work until you have complex sub-domains — don't pre-structure for hypothetical future files.
- **Scaffolding empty folders with `.gitkeep`.** The pattern is documentation, not scaffolding. Folders appear when the first file of that type is created.
- **Putting wireframes in `reference/`.** Wireframes are frontend-domain-specific and locale-variant; they need their own folder with the locale-suffix naming convention.

## Scope

This covers the shared docs layout. A project may add domain-specific folders (`prompts/`, `migrations/`, `schemas/`, etc.) alongside `docs/` without touching the shared layout.
