---
## ============================================================
##  RESUME TEMPLATE — Pandoc Markdown → PDF
##
##  HOW TO TAILOR THIS FILE:
##  1. Fill in your personal info (name, email, links)
##  2. Update "title" to match the exact job title in the JD
##  3. Rewrite "summary" using keywords from the JD (3-4 sentences)
##  4. In "skills": promote categories most relevant to the role
##  5. In "experience": keep max 4-5 bullets per role, lead with metrics
##  6. In "projects": pick the 2-3 most relevant
##  7. Run: pandoc resume.md -o resume.pdf --template resume-template.latex --pdf-engine=xelatex
## ============================================================

name: "Your Name"
location: "City, Country (Remote)"
email: "you@example.com"

## ── Links (all optional — remove any you don't use) ──────────
linkedin: "https://linkedin.com/in/yourhandle"
linkedin_label: "linkedin.com/in/yourhandle"
github: "https://github.com/yourhandle"
github_label: "github.com/yourhandle"
# gitlab: "https://gitlab.com/yourhandle"
# gitlab_label: "gitlab.com/yourhandle"
website: "https://yoursite.dev"
website_label: "yoursite.dev"

## ── [TAILOR] Role-specific title — mirror the JD's exact title
title: "Software Engineer"

## ── [TAILOR] 3-4 sentence summary. Lead with your strongest angle.
##    Inject keywords from the JD. This is the highest-leverage field.
summary: >
  Experienced Software Engineer with N+ years building production systems
  across [your domains]. Specializing in [your key strengths].
  Proven track record of [your top achievement with metric].

## ── [TAILOR] Reorder categories — most relevant to the role first
skills:
  - category: "Languages"
    items: "Python, TypeScript, Go, Java"
  - category: "Frameworks"
    items: "React, Next.js, FastAPI, Spring Boot"
  - category: "Infrastructure"
    items: "Docker, Kubernetes, Terraform, AWS, CI/CD"
  - category: "Data"
    items: "PostgreSQL, Redis, MongoDB, ETL Pipelines"

## ============================================================
##  EXPERIENCE ENTRIES
##  Keep max 4-5 bullets per role. Lead with highest-impact metric.
##  Each bullet: strong verb + what you did + measurable result
## ============================================================

experience:

  - company: "Company Name"
    title: "Your Title"
    dates: "Mon YYYY – Mon YYYY"
    context: "Brief context about the team, product, or scope"
    bullets:
      - "Led [initiative] resulting in **X% improvement** in [metric]"
      - "Built [system/feature] processing **N+ [units]** daily using [tech stack]"
      - "Reduced [problem] by **X%** through [approach], saving [time/cost]"

  - company: "Previous Company"
    title: "Your Title"
    dates: "Mon YYYY – Mon YYYY"
    context: "Brief context"
    bullets:
      - "Designed and implemented [project] serving **N+ users**"
      - "Migrated [old system] to [new system], cutting [metric] by **X%**"
      - "Mentored N engineers and established [process/standards]"

## ============================================================
##  PROJECTS — pick 2-3 most relevant per application
## ============================================================

projects:

  - name: "Project Name"
    stack: "Tech · Stack · Used"
    bullets:
      - "Built [what] for [whom], achieving [measurable result]"
      - "Key technical challenge: [what you solved and how]"

  - name: "Another Project"
    stack: "Tech · Stack · Used"
    bullets:
      - "Designed [system] that [impact with metric]"

## ============================================================
##  EDUCATION
## ============================================================

education:
  - institution: "University Name"
    dates: "YYYY – YYYY"
    description: >
      B.S. in Computer Science. Relevant coursework or honors.
---
