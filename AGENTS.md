# AGENTS.md

Guidance for AI agents working in this repository.

## Scope

This repo contains reusable Agent Skills. Each top-level skill directory should be self-contained and centered on its `SKILL.md` file.

## Development Guidelines

- Keep skill instructions concise, actionable, and specific to agent behavior.
- Put long references, templates, or examples under `references/`, `assets/`, or `scripts/` instead of bloating `SKILL.md`.
- Ensure `SKILL.md` frontmatter `name` matches the directory name.
- Descriptions must clearly state when to use the skill.
- Prefer updating evals when changing expected skill behavior.
- Mark deprecated skills clearly and point to the replacement.

## Validation

Run before committing:

```bash
just ci
```

For a faster skills-only check:

```bash
python scripts/validate_skills.py
```

## Commits

Use Conventional Commits, for example:

```text
feat(image-prompt-crafter): add model inference guidance
fix(gitlab-ci): document edge cases
```
