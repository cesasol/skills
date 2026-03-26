---
name: resume-pdf
description: >
  Generates a tailored, ATS-optimized PDF resume using a Pandoc + XeLaTeX pipeline.
  Use this skill whenever the user asks to create, tailor, update, or rebuild a resume — including
  when a job description is pasted, when targeting a specific role or company, or when the user says
  anything like "update my resume", "tailor my resume for this job", "generate a resume PDF",
  or "apply to this role". Also use it when the user pastes a job description and implies they need
  application materials, even without explicitly mentioning a resume.
---

# Resume PDF Skill

Generates a fully formatted, role-tailored PDF resume using:
- `assets/resume-base.md` — Pandoc Markdown with YAML front matter (the only file edited per role)
- `assets/resume-template.latex` — XeLaTeX template (layout/design, rarely changed)

**Build command:**
```bash
pandoc resume.md --template resume-template.latex --pdf-engine=xelatex -o resume.pdf
```

---

## Workflow

### Step 1 — Copy assets to a working directory
```bash
WORK_DIR=$(mktemp -d /tmp/resume-XXXXXX)
cp /path/to/skill/assets/resume-base.md "$WORK_DIR/resume.md"
cp /path/to/skill/assets/resume-template.latex "$WORK_DIR/resume-template.latex"
```

### Step 2 — Fill in or tailor `resume.md`

If the user provides their details or an existing resume, populate the YAML front matter fields.
If a job description was provided, extract the top 5-7 keywords and map them to the candidate's
experience before editing. Then make these targeted changes:

| Field | What to change |
|---|---|
| `name`, `email`, links | Candidate's personal info |
| `title` | Mirror the exact job title from the JD |
| `summary` | 3-4 sentences; inject JD keywords; lead with strongest angle |
| `skills` | Reorder categories — most JD-relevant first |
| `experience[*].bullets` | Promote bullets that match JD; demote or remove irrelevant ones |
| `projects` | Select 2-3 most relevant to the target role |

**Rules:**
- Never fabricate metrics or technologies the candidate hasn't used
- Keep bullets <= 5 per role; each must start with a strong verb + metric where possible
- ATS safety: no tables, columns, or special characters in bullet text
- The `summary` is the highest-leverage field — always rewrite it per role

### Step 3 — Build the PDF
```bash
pandoc "$WORK_DIR/resume.md" --template "$WORK_DIR/resume-template.latex" --pdf-engine=xelatex -o "$WORK_DIR/resume.pdf"
```

If build fails, check:
- `xelatex` available: `which xelatex`
- Liberation Sans font available: `fc-list | grep Liberation`
- Syntax errors in YAML front matter (quotes around strings with colons or special chars)

### Step 4 — Output

Present the files from `$WORK_DIR` to the user:
- `$WORK_DIR/resume.pdf` — the generated PDF
- `$WORK_DIR/resume.md` — the source Markdown (for inspection and iteration)

Copy to an outputs directory if one exists, or leave in place for the user to retrieve.

---

## Tailoring Reference

### Bullet Writing Formula

Every bullet should follow: **Strong verb + what you did + measurable result**

Examples:
- "Architected [system] processing **N+ [units] daily**, reducing [metric] by X%"
- "Led migration from [old] to [new], cutting [cost/time] by **X%**"
- "Built [tool/feature] that automated [process], saving N+ hours weekly"

### Skill Category Order — by Role Type

**Frontend Engineer:** Frontend → Backend → Infrastructure → Data
**Backend Engineer:** Backend → Data → Infrastructure → Frontend
**Full-Stack Engineer:** Frontend → Backend → Infrastructure → Data
**Data Engineer:** Data → Backend → Infrastructure → Frontend
**DevOps/SRE:** Infrastructure → Backend → Data → Frontend
**AI/ML Engineer:** AI/ML → Backend → Data → Infrastructure → Frontend

Reorder the `skills` list to match the target role. The first category gets the most visual weight.

---

## Asset Files

- `assets/resume-base.md` — Pandoc Markdown template with placeholder content; fill in per candidate
- `assets/resume-template.latex` — XeLaTeX template; navy/steel-blue palette; Liberation Sans; ATS-safe layout

To update the candidate's base profile, edit `assets/resume-base.md` directly.
To update layout/colors, edit `assets/resume-template.latex`.
