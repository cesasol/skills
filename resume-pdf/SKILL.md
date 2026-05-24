---
name: resume-pdf
description: >
  Generates a tailored, ATS-optimized PDF resume using Typst.
  Use this whenever the user asks to create, tailor, update, or rebuild a resume — including
  when a job description is pasted, when targeting a specific role or company, or when the user says
  anything like "update my resume", "tailor my resume for this job", "generate a resume PDF",
  or "apply to this role". Also use it when the user pastes a job description and implies they need
  application materials, even without explicitly mentioning a resume.
---

# Resume PDF Skill

Generates a fully formatted, role-tailored PDF resume using Typst.

- `assets/resume-base.typ` — Typst source with data + template (the only file edited per role)
- `assets/resume-template.typ` — Separated layout helpers (rarely changed)

**Build command:**

```bash
typst compile resume.typ resume.pdf
```

Or watch for live preview:

```bash
typst watch resume.typ resume.pdf
```

---

## Workflow

### Step 1 — Copy assets to a working directory

```bash
WORK_DIR=$(mktemp -d /tmp/resume-XXXXXX)
cp assets/resume-base.typ "$WORK_DIR/resume.typ"
cp assets/resume-template.typ "$WORK_DIR/"
```

### Step 2 — Fill in or tailor `resume.typ`

The file has two clear zones:

1. **DATA** — top of file, YAML-like `#let` assignments. Edit these per role.
2. **TEMPLATE** — bottom of file, layout and rendering. Rarely touched.

| Field | What to change |
| --- | --- |
| `name`, `email`, `links` | Personal info |
| `title` | Mirror exact job title from the JD |
| `summary` | 3-4 sentences; inject JD keywords; lead with strongest angle |
| `skills` | Reorder array — most JD-relevant first |
| `experience` | Promote bullets matching JD; demote/remove irrelevant ones |
| `projects` | Select 2-3 most relevant to target role |

**Rules:**

- Never fabricate metrics or technologies
- Keep bullets ≤ 5 per role; each starts with strong verb + metric where possible
- ATS safety: keep it simple — no columns, tables, or special glyphs
- The `summary` is the highest-leverage field — always rewrite it per role

### Step 3 — Build the PDF

```bash
typst compile "$WORK_DIR/resume.typ" "$WORK_DIR/resume.pdf"
```

Builds in <1s. If it fails, check:

- Syntax errors in Typst data (quotes around strings with special chars)
- Font availability: `typst fonts | rg Liberation`

### Step 4 — Output

Present to the user:

- `$WORK_DIR/resume.pdf` — the generated PDF
- `$WORK_DIR/resume.typ` — the source (for inspection and iteration)

---

## Tailoring Reference

### Bullet Writing Formula

Every bullet: **Strong verb + what you did + measurable result**

Examples:

- `"Architected [system] processing N+ [units] daily, reducing [metric] by X%"`
- `"Led migration from [old] to [new], cutting [cost/time] by X%"`
- `"Built [tool/feature] that automated [process], saving N+ hours weekly"`

### Skill Category Order — by Role Type

**Frontend:** Frontend → Backend → Infrastructure → Data
**Backend:** Backend → Data → Infrastructure → Frontend
**Full-Stack:** Frontend → Backend → Infrastructure → Data
**Data Engineer:** Data → Backend → Infrastructure → Frontend
**DevOps/SRE:** Infrastructure → Backend → Data → Frontend
**AI/ML Engineer:** AI/ML → Backend → Data → Infrastructure → Frontend

---

## Asset Files

- `assets/resume-base.typ` — Base resume with placeholder data and template embedded; edit per role
- `assets/resume-template.typ` — Typst template; navy/steel-blue palette; ATS-safe layout