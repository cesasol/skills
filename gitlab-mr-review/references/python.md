# Python Review Reference

Load when the diff touches Python. Concrete patterns for the house rules in `house-rules.md`.

## Rule 1 — lint/type suppression directives

Python suppression directives to flag (unless the verified-boundary exception applies — guard + reason):

- `# noqa` (bare or with a code) with no reason and no guard
- `# type: ignore` / `# type: ignore[...]` with no reason and no guard
- `# pylint: disable=...` / `# ruff: noqa` blanket disables
- File-level `# flake8: noqa` or section disables left on past the line that needed them

Acceptable form (all three: boundary + guard + reason):

```python
# type: ignore[attr-defined]  # pydantic v2 private setter; guarded by model_validate below
```

A runtime guard compensates for the silence: `model_validate`, `isinstance`, an explicit field check, or a try/except that surfaces the error. The comment states *why* the suppression is safe.

## Rule 2 — pydantic schemas for boundaries & shared state

Use pydantic models to validate:

- Every HTTP response parsed from JSON (`httpx`, `requests`, `aiohttp`, FastAPI `TestClient`)
- Any state object constructed from external/serialized data and passed to multiple functions

Flag:

```python
# Bad — unvalidated external payload handed across boundaries
data = response.json()
process_order(data["items"])  # dict with no contract
```

Prefer:

```python
class Order(BaseModel):
    items: list[Item]

order = Order.model_validate(response.json())  # schema parse at the boundary
process_order(order.items)  # typed, validated
```

Do NOT flag internal construction with known shape:

```python
config = ServerConfig(host="...", port=...)  # built in code, not from external data
```

If the codebase already uses `dataclasses` with manual validation or `attrs` + `cattrs`, treat that as the schema layer — flag only the missing parse, not the choice of library.
