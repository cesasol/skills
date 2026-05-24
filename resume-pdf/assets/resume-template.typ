// ============================================================
//  Resume Template — Typst Layout Helpers
//  Compatible with Typst 0.14+
// ============================================================

#let accent = rgb("#1A1A2E")
#let accent-light = rgb("#2D4A7A")
#let subtle = rgb("#555555")

#set page(
  paper: "us-letter",
  margin: (top: .55in, bottom: .55in, left: .6in, right: .6in),
)

#set text(font: ("Liberation Sans", "DejaVu Sans"), size: 9.5pt, fill: subtle)

// ── Section Heading ─────────────────────────────────────────
#let section-heading(title) = {
  v(8pt)
  text(size: 8.5pt, weight: "bold", fill: accent)[#upper(title)]
  v(2pt)
  line(length: 100%, stroke: .6pt + accent-light)
  v(4pt)
}

// ── Bullet helper ───────────────────────────────────────────
#let item(body) = {
  h(1.2em)
  text(fill: accent-light)[\u{2022}]
  h(0.3em)
  text(fill: subtle, size: 9pt)[#body]
  v(2pt)
}

// ── Name + Title Header ─────────────────────────────────────
#let resume-header(name, title,
  location: none, email: none,
  linkedin: none, linkedin-label: none,
  github: none, github-label: none,
  website: none, website-label: none) = {
  let contact-parts = ()
  if location != none { contact-parts.push(location) }
  if email != none { contact-parts.push(link("mailto:" + email)[#email]) }
  if linkedin != none and linkedin-label != none { contact-parts.push(link(linkedin)[#linkedin-label]) }
  if github != none and github-label != none { contact-parts.push(link(github)[#github-label]) }
  if website != none and website-label != none { contact-parts.push(link(website)[#website-label]) }

  grid(
    columns: (2fr, 1fr),
    [
      #text(size: 22pt, weight: "bold", fill: accent)[#name]
      #text(size: 12pt, fill: accent-light, style: "italic")[#title]
    ],
    [
      #align(
        right + top,
        text(size: 8.5pt, fill: subtle)[
          #contact-parts.join([ \\\ ])
        ],
      )
    ],
  )

  v(6pt)
  line(length: 100%, stroke: 1.2pt + accent)
  v(4pt)
}

// ── Summary ─────────────────────────────────────────────────
#let resume-summary(body) = {
  v(2pt)
  text(size: 9.5pt, fill: subtle)[#body]
  v(4pt)
}

// ── Job Entry ───────────────────────────────────────────────
#let job-entry(company, role, dates, note: none, ..items) = {
  grid(
    columns: (1fr, auto),
    [
      #text(size: 10.5pt, weight: "bold", fill: accent)[#company]
      #h(4pt)
      #text(size: 10pt, fill: accent-light, style: "italic")[— #role]
    ],
    [
      #text(size: 9pt, fill: subtle)[#align(right, [#dates])]
    ],
  )
  if note != none {
    v(2pt)
    text(size: 8.5pt, fill: subtle, style: "italic")[#note]
  }
  v(2pt)
  for bullet in items.at(0) {
    item(bullet)
  }
  v(6pt)
}

// ── Project Entry ───────────────────────────────────────────
#let project-entry(name, stack, ..items) = {
  grid(
    columns: (1fr, auto),
    [
      #text(size: 10pt, weight: "bold", fill: accent-light)[#name]
    ],
    [
      #text(size: 8.5pt, fill: subtle, style: "italic")[#align(right, [#stack])]
    ],
  )
  v(2pt)
  for bullet in items.at(0) {
    item(bullet)
  }
  v(4pt)
}

// ── Skill Row ───────────────────────────────────────────────
#let skill-row(category, items) = {
  text(size: 9pt)[
    #text(weight: "bold", fill: accent)[#category:] #h(2pt)
    #text(fill: subtle)[#items]
  ]
  v(2pt)
}

// ── Education Entry ─────────────────────────────────────────
#let education-entry(institution, dates, description) = {
  grid(
    columns: (1fr, auto),
    [
      #text(size: 10pt, weight: "bold", fill: accent)[#institution]
    ],
    [
      #text(size: 9pt, fill: subtle)[#align(right, [#dates])]
    ],
  )
  text(size: 9pt, fill: subtle, style: "italic")[#description]
  v(4pt)
}
