# TypeScript / JavaScript Review Reference

Load when the diff touches TypeScript or JavaScript. Concrete patterns for the house rules in `house-rules.md`.

## Rule 1 — lint/type suppression directives

TS/JS suppression directives to flag (unless the verified-boundary exception applies — guard + reason):

- `// @ts-ignore` with no reason and no guard
- `// @ts-expect-error` with no reason and no guard (preferred over `@ts-ignore` because it errors if the suppression becomes unused, but still needs justification)
- `/* eslint-disable ... */` blanket disables, especially file-level
- `as any` / `as unknown as X` used to bypass type errors instead of fixing the types
- Non-null assertion `!` used to silence nullability instead of handling it

Acceptable form (all three: boundary + guard + reason):

```ts
// @ts-expect-error: third-party types missing .custom; guarded by typeof check below
```

A runtime guard compensates for the silence: `typeof`, `Array.isArray`, a zod `parse`/`safeParse`, or an explicit null check. The comment states *why* the suppression is safe.

## Rule 2 — zod schemas for boundaries & shared state

Use zod schemas to validate:

- Every `response.json()` / `JSON.parse(...)` result from an API call
- Any state object built from external/serialized data and passed to multiple functions

Flag:

```ts
// Bad — unvalidated external payload handed across boundaries
const data = await res.json();
processItems(data.items); // unvalidated shape
```

Prefer:

```ts
const OrderSchema = z.object({ items: z.array(ItemSchema) });

const order = OrderSchema.parse(await res.json()); // schema parse at the boundary
processItems(order.items); // typed, validated
```

For performance-sensitive or fallible paths, `safeParse` with explicit error handling is acceptable — flag only the missing parse, not the choice of throw-vs-safe.

Do NOT flag internal construction with known shape:

```ts
const config = { host: "...", port: 8080 } as const; // built in code, not external data
```

If the codebase already uses `valibot`, `arktype`, or `@sinclair/typebox`, treat that as the schema layer — flag only the missing parse, not the choice of library.
