// ============================================================
//  RESUME — Typst Source
//  TAILOR THIS FILE per role (top section only)
//  Build: typst compile resume.typ resume.pdf
// ============================================================

#import "resume-template.typ": *

// ═══════════════════════════════════════════════════════════
//  DATA  —  Edit these fields per role
// ═══════════════════════════════════════════════════════════

#let name = "César Valadez"
#let location = "Mexico City, MX — Remote"
#let email = "me@cesasol.com.mx"
#let linkedin = "https://linkedin.com/in/cesasol"
#let linkedin-label = "linkedin.com/in/cesasol"
#let github = "https://github.com/cesasol"
#let github-label = "github.com/cesasol"
#let website = "https://cesasol.dev"
#let website-label = "cesasol.dev"

// [TAILOR] Mirror the exact job title from the JD
#let title = "AI Engineer"

// [TAILOR] 3-4 sentence summary. Inject JD keywords. Lead with strongest angle.
#let summary = [
  AI Engineer and Full-Stack Developer with 12+ years building production systems
  across data engineering, web infrastructure, and AI/ML. Specializing in
  Retrieval-Augmented Generation (RAG) systems, agentic workflows, and LLM
  deployment — both GPU-accelerated and edge-optimized. Proven track record of
  reducing operational overhead by up to 90% through internal tooling and
  automation, and delivering scalable solutions processing millions of data
  points daily at Zillow and PayPal.
]

// [TAILOR] Reorder categories — most relevant to the role first
#let skills = (
  (category: "AI/ML",       items: "LLMs, RAG Systems, Agentic Workflows, LangChain, LangGraph, Ollama, Open WebUI, Vector Databases, HuggingFace"),
  (category: "Backend",     items: "Python, FastAPI, Laravel, Node.js, Express, Spring Boot, REST APIs, PostgreSQL, Redis"),
  (category: "Frontend",    items: "Vue.js / Nuxt, React, TypeScript, TailwindCSS, D3.js"),
  (category: "Data",        items: "Apache Flink, AWS Kinesis, Scala, Java, ETL Pipelines, Serverless Architecture"),
  (category: "DevOps",      items: "Docker, Kubernetes, Terraform, GitLab CI, AWS, Linux (12yr), Self-Hosted Infra"),
)

// [TAILOR] Pick 2-3 most relevant projects; reorder experience
#let experience = (
  (
    company: "ValkymIA",
    title: "Director & Founder (AI Consultancy)",
    dates: "2024 – Present",
    note: "AI consultancy serving Mexican SMBs — RAG systems, agentic workflows, business automation",
    bullets: (
      "Architected multi-agent RAG platform for small business knowledge bases, reducing client response time by 80%",
      "Built custom LLM-powered tools integrating LangChain, Ollama, and vector databases for document retrieval",
      "Delivered end-to-end AI solutions: from requirement analysis through production deployment on self-hosted GPU infrastructure",
      "Developed tailored image generation applications and company-wide knowledge retrieval systems for clients",
    ),
  ),
  (
    company: "Zillow",
    title: "Data Engineer",
    dates: "Aug 2024 – Jul 2025",
    note: "Real-time data pipelines powering property data infrastructure",
    bullets: (
      "Architected real-time streaming solutions processing millions of property data points daily via Apache Flink and AWS Kinesis",
      "Reduced data anomalies by 40% through automated validation pipelines and quality frameworks",
      "Improved pipeline throughput by 35% through Scala and Java performance optimizations",
      "Enhanced infrastructure to support 3x data volume growth without proportional resource increase",
    ),
  ),
  (
    company: "PayPal",
    title: "Software Engineer",
    dates: "May 2023 – Aug 2024",
    note: "Automation tools and frontend performance for legal and compliance operations",
    bullets: (
      "Automated legal page review with Playwright, reducing review cycles from 10 hours to 1 hour (90% reduction)",
      "Built performance-oriented browser extensions processing 10,000+ legal documents monthly in TypeScript",
      "Reduced asset delivery size by 60% through Python-based image processing pipelines",
      "Migrated build system from Webpack to Vite, cutting build times from 8 minutes to 45 seconds",
    ),
  ),
  (
    company: "Nagarro",
    title: "Full-Stack Developer",
    dates: "Mar 2022 – May 2023",
    note: "Enterprise lending platform serving 100,000+ active users",
    bullets: (
      "Led Vue.js 1.x → 2.x migration affecting 50+ components with zero service disruption",
      "Implemented Vuex state management, reducing component complexity by 35%",
      "Reduced deployment failures by 60% through improved CI/CD testing with Terraform, Docker, and Jenkins",
    ),
  ),
  (
    company: "Dinamo",
    title: "Full-Stack Developer → Senior",
    dates: "Sep 2016 – Sep 2020",
    note: "Design agency — grew dev team from 1 to 5, built internal tooling ecosystem",
    bullets: (
      "Built automated image processing pipeline reducing designer workflow from 30 min to 30 sec per batch (98% reduction)",
      "Developed Vue.js component library reused across 30+ projects, reducing project setup time by 75%",
      "Created internal Lead Management System (Vue.js/Laravel) capturing and routing 1,000+ monthly leads",
      "Managed 15+ production servers, established CI/CD pipelines, and automated document generation saving 10 hrs/week",
    ),
  ),
)

// [TAILOR] Pick 2-3 most relevant projects
#let projects = (
  (
    name: "Sigrun — Multi-Agent RAG Platform",
    stack: "Python · LangChain · Ollama · PostgreSQL · Nuxt",
    bullets: (
      "Designed and deployed a multi-agent AI platform for Mexican SMBs providing RAG-powered knowledge retrieval across client knowledge bases",
      "Built agentic workflow orchestration layer enabling autonomous document processing, summarization, and query routing",
    ),
  ),
  (
    name: "Hermes Agent — AI Engineering Assistant",
    stack: "Python · LangGraph · LLMs · RAG · CLI",
    bullets: (
      "Contributed to an open-source AI agent with persistent memory, browser automation, and subagent delegation capabilities",
      "Integrated Playwright CDP automation for LinkedIn recruiter pipeline management",
    ),
  ),
  (
    name: "Cadefi — Legal Code Navigation Platform",
    stack: "Nuxt.js · Laravel Lumen · PostgreSQL · Tiptap",
    bullets: (
      "Built hierarchical legal text system modeling ~100,000 content nodes with PostgreSQL adjacency lists and full-text search",
      "Developed Kindle-like reading interface with bookmarking, cross-law referencing, and reading progress tracking",
    ),
  ),
)

#let education = (
  (
    institution: "Self-Taught Engineer",
    dates: "12+ years",
    description: "Continuous learning across web development, data engineering, and AI/ML. Rapid technology adoption — proficiency in new languages/frameworks within 1 month.",
  ),
)

// ═══════════════════════════════════════════════════════════
//  RENDER  —  layout code (rarely edited)
// ═══════════════════════════════════════════════════════════

#resume-header(
  name,
  title,
  location: location,
  email: email,
  linkedin: linkedin,
  linkedin-label: linkedin-label,
  github: github,
  github-label: github-label,
  website: website,
  website-label: website-label,
)

#resume-summary(summary)

// ── Core Skills ────────────────────────────────────────────
#section-heading("Core Skills")
#for cat in skills {
  skill-row(cat.category, cat.items)
}
#v(4pt)

// ── Professional Experience ────────────────────────────────
#section-heading("Professional Experience")
#for job in experience {
  job-entry(
    job.company,
    job.title,
    job.dates,
    note: job.note,
    job.bullets,
  )
}

// ── Notable Projects ───────────────────────────────────────
#section-heading("Notable Projects")
#for proj in projects {
  project-entry(
    proj.name,
    proj.stack,
    proj.bullets,
  )
}

// ── Education ──────────────────────────────────────────────
#section-heading("Education")
#for edu in education {
  education-entry(edu.institution, edu.dates, edu.description)
}
