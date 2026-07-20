# House Rules — Always Enforced

Load this file on **every** review, regardless of stack or requested aspect. These are enforced opinions that apply across all languages. Stack-specific reference files (`python.md`, `typescript.md`)
show the concrete directives and patterns for each rule.

These rules use the same confidence scoring as the `code` aspect:

- 80-90: Important — should fix (house rules default here unless specified otherwise)
- 91-100: Critical — escalate when a suppression hides a real error path or an unvalidated boundary handles untrusted input

When posting a comment for a house-rule violation, include the rule's one-line rationale so the MR author understands the *why*, not just the *what*.

## Rule 1 — No unjustified lint/type suppression

Flag any lint or type-checker suppression directive that lacks **both** a compensating runtime guard at a verified boundary **and** a one-line reason in the comment itself.

The specific directives by stack are listed in `python.md` / `typescript.md`.

**Acceptable exception (the only one):** the suppression sits at a verified boundary, a runtime guard compensates for the silence, and the comment states the reason. All three must be present.
Otherwise flag it.

Flag:

- Bare suppressions with no comment (`# noqa`, `// @ts-ignore`, `/* eslint-disable */`)
- Suppressions with a comment but no runtime guard
- Blanket file-level disables that survive past the specific line that needed them
- `as any` / non-null `!` assertions used to bypass type errors instead of fixing the types

Do NOT flag:

- Suppressions at a verified boundary with a runtime guard + stated reason (all three present)

Severity: 80-90. Escalate to 91-100 if the suppression hides an error path or untrusted-input handling.

Rationale: a suppressed warning is a silent claim that "I know better than the checker." Without a guard and a reason, that claim is unverifiable and rots as the code changes.

## Rule 2 — Schema-validate every external boundary and shared state

Every response from an API call and every large state object passed down to multiple functions must be validated against a schema before use.

Schema tools by stack: pydantic (`python.md`), zod (`typescript.md`).

Flag:

- `JSON.parse(...)` / `response.json()` / `json.loads(...)` results used directly without a schema parse
- Unvalidated dicts/objects handed to multiple functions (a shared mutable shape with no contract)
- `Any` / `unknown` left unvalidated at a function boundary that consumes external data

Do NOT flag:

- Internal data constructed in code with known shape (no external/serialized source)
- Test fixtures and mock data (already excluded from review)

Severity: 80-90. Escalate to 91-100 if the boundary handles untrusted/user input.

Rationale: a type annotation on an unvalidated payload is a hope, not a guarantee. The schema parse is the actual contract; without it, every downstream function inherits a silent assumption that
breaks at runtime, far from the source.

## Rule 3 — Keep comments minimal; refactor workarounds instead of explaining them

Comments should be brief and explain intent that cannot be made clear in the code itself. Long explanatory comments that document a workaround are a red flag: reject the change and require a refactor
that removes the workaround or makes the design self-explanatory. Decorative comments are acceptable only when needed to distinguish sections of a script or similar file. File-header comments follow
separate size limits.

Flag:

- Multi-paragraph or unusually long comments explaining why confusing code must remain
- Comments that document fragile ordering, hidden coupling, special cases, or compensating behavior instead of removing them
- Workaround comments that ask future maintainers to preserve non-obvious behavior
- Decorative section comments that are unnecessary, 70 or more characters wide, or three or more lines tall
- File-header comments wider than 100 characters, longer than 40 lines, or wrapped in decorative opening or closing lines
- File-header documentation that exceeds those limits instead of being extracted to a separate text file

Do NOT flag:

- Short comments explaining non-obvious business intent, external constraints, or safety invariants
- API documentation that describes a public contract
- Decorative comments required to distinguish sections of a script or similar file when they are less than 70 characters wide and less than three lines tall
- File-header comments no more than 100 characters wide and 40 lines long, without decorative opening or closing lines
- Longer file-level documentation extracted to a separate text file and referenced by a concise file header
- Temporary workarounds with a tracked removal issue and a clear, near-term expiry condition

### Markdown formatting

Markdown-formatted comments and extracted documentation must follow the target repository's effective rumdl configuration. Check `.rumdl.toml`, `rumdl.toml`, and `[tool.rumdl]` in `pyproject.toml`; do
not impose this repository's full profile on another project.

If the target repository has no rumdl configuration, enforce only this minimal fallback:

- `MD013` — limit lines to 200 characters, reflow prose, check code blocks and headings, and exclude tables
- `MD029` — number ordered-list items sequentially
- `MD033` — allow only `<br>`, `<details>`, and `<summary>` inline HTML elements
- `MD060` — format table cells consistently

For diagrams in Markdown, prefer fenced Mermaid diagrams over ASCII art. Flag new or modified ASCII diagrams when Mermaid can express the same information clearly. Allow ASCII only when the target
renderer does not support Mermaid or the exact monospaced text layout is itself significant.

Treat Markdown-formatting violations as severity 80-90. Do not reject for formatting alone unless the comment also violates the workaround or size constraints above.

Severity: 91-100. Reject and require refactoring before merge unless the temporary-workaround exception applies.

Rationale: comments cannot make a fragile workaround safe; refactoring the design removes the hidden constraint instead of transferring its risk to future maintainers.

## Extending the house rules

Adding a new enforced opinion: state the principle, what to flag, the acceptable exception (if any), severity, and a one-line rationale here. Put the concrete directives, library patterns, and code
examples in the matching stack file under `references/`.

Adding a new stack: create `references/<lang>.md` showing the concrete form of each existing house rule for that language.
