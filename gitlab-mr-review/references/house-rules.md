# House Rules — Always Enforced

Load this file on **every** review, regardless of stack or requested aspect. These are enforced opinions that apply across all languages. Stack-specific reference files (`python.md`, `typescript.md`)
show the concrete directives and patterns for each rule.

These rules use the same confidence scoring as the `code` aspect:

- 80-90: Important — should fix (both house rules default here)
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

## Extending the house rules

Adding a new enforced opinion: state the principle, what to flag, the acceptable exception (if any), severity, and a one-line rationale here. Put the concrete directives, library patterns, and code
examples in the matching stack file under `references/`.

Adding a new stack: create `references/<lang>.md` showing the concrete form of each existing house rule for that language.
