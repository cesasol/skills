# Direct API Access

Complete reference for `glab api` — make authenticated requests to the GitLab REST and GraphQL APIs.

## Table of Contents

- [Basics](#basics)
- [Placeholders](#placeholders)
- [HTTP Methods](#http-methods)
- [Passing Data](#passing-data)
- [Pagination](#pagination)
- [Output Formats](#output-formats)
- [GraphQL](#graphql)
- [Common API Patterns](#common-api-patterns)

## Basics

```bash
# GET request (default when no data fields)
glab api projects/:id

# POST request (default when data fields present)
glab api projects/:id/issues -f title="New issue"

# Explicit method
glab api projects/:id/issues --method GET

# Different host
glab api projects/123 --hostname gitlab.example.com
```

## Placeholders

When inside a git repo linked to GitLab, these placeholders are auto-resolved:

| Placeholder | Resolves to |
|-------------|-------------|
| `:id` | Project ID |
| `:fullpath` | URL-encoded full project path |
| `:group` | Group/namespace |
| `:namespace` | Namespace |
| `:repo` | Project name |
| `:branch` | Current branch |
| `:user` | Authenticated user ID |
| `:username` | Authenticated username |

```bash
# These are equivalent when in a project repo:
glab api projects/:id
glab api projects/:fullpath

# Use in nested endpoints
glab api projects/:id/merge_requests
glab api projects/:id/pipelines
glab api projects/:id/issues
glab api projects/:id/members
```

## HTTP Methods

```bash
# GET (default for no-data requests)
glab api projects/:id

# POST (default when fields present)
glab api projects/:id/issues -f title="Bug report"

# PUT
glab api projects/:id/issues/42 --method PUT -f title="Updated title"

# PATCH
glab api projects/:id/merge_requests/123 --method PATCH -f title="New title"

# DELETE
glab api projects/:id/issues/42 --method DELETE
```

## Passing Data

### `--field` / `-f` (typed)

Auto-converts values based on format:
- `true`, `false`, `null` → JSON boolean/null
- Integers → JSON numbers
- Placeholders (`:namespace`, `:repo`, etc.) → resolved values
- `@filename` → file contents
- `@-` → stdin

```bash
# Boolean
glab api projects/:id/merge_requests/123 --method PUT -f squash=true

# Integer
glab api projects/:id/issues --method POST -f title="Issue" -f weight=5

# File content
glab api projects/:id/snippets --method POST -f content=@script.py

# Stdin
echo "content" | glab api projects/:id/snippets --method POST -f content=@-
```

### `--raw-field` / `-F` (string only)

All values are JSON-encoded strings — no type conversion.

```bash
glab api projects/:id/issues --method POST -F title="Bug" -F description="Details here"
```

### `--input` (raw body)

Send raw request body from a file:

```bash
# From file
glab api projects/:id/issues --method POST --input body.json

# From stdin
echo '{"title":"Issue"}' | glab api projects/:id/issues --method POST --input -
```

## Pagination

```bash
# Auto-paginate (fetches all pages)
glab api projects/:id/merge_requests --paginate

# Manual pagination
glab api projects/:id/issues --method GET -f per_page=100 -f page=1
glab api projects/:id/issues --method GET -f per_page=100 -f page=2
```

> **Tip:** `--paginate` fetches all pages sequentially. For large datasets, prefer manual pagination with `per_page` and `page`.

## Output Formats

```bash
# Pretty-printed JSON (default)
glab api projects/:id

# NDJSON (newline-delimited JSON — one object per line)
glab api projects/:id/merge_requests --output ndjson

# Combine with jq for processing
glab api projects/:id/merge_requests --paginate | jq '.[].title'
```

| Flag | Format | Best For |
|------|--------|----------|
| (default) | Pretty JSON | Single objects, small lists |
| `--output ndjson` | Newline-delimited JSON | Large datasets, streaming, piping to `jq` |

## GraphQL

```bash
# Simple query
glab api graphql -f query='
  query {
    currentUser {
      username
      name
    }
  }
'

# With variables
glab api graphql \
  -f query='
    query($projectPath: ID!) {
      project(fullPath: $projectPath) {
        name
        description
        mergeRequests(state: opened) {
          nodes {
            title
            iid
          }
        }
      }
    }
  ' \
  -f projectPath="group/project"

# Paginated GraphQL
glab api graphql --paginate -f query='
  query($endCursor: String) {
    project(fullPath: "group/project") {
      issues(after: $endCursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          title
          iid
          state
        }
      }
    }
  }
'
```

### GraphQL pagination requirements

For `--paginate` to work with GraphQL:
1. Query must accept `$endCursor: String` variable
2. Query must fetch `pageInfo { hasNextPage, endCursor }` from the collection

## Common API Patterns

### Get project details

```bash
glab api projects/:id
```

### List project members

```bash
glab api projects/:id/members --paginate
```

### Get merge request approvals

```bash
glab api projects/:id/merge_requests/123/approvals
```

### Get pipeline jobs

```bash
glab api projects/:id/pipelines/456/jobs
```

### Get job log/trace

```bash
glab api projects/:id/jobs/789/trace
```

### Create a project label

```bash
glab api projects/:id/labels --method POST -f name="priority::high" -f color="#FF0000"
```

### Search across projects

```bash
glab api projects -f search="my-project" -f membership=true
```

### Get merge request changes (file list)

```bash
glab api projects/:id/merge_requests/123/changes
```

### Get repository file content

```bash
glab api projects/:id/repository/files/path%2Fto%2Ffile/raw -f ref=main
```

### Trigger pipeline

```bash
glab api projects/:id/pipeline --method POST -f ref=main
```

### Get user info

```bash
glab api user
```

### Search globally

```bash
glab api search -f scope=projects -f search="keyword"
glab api search -f scope=merge_requests -f search="keyword"
glab api search -f scope=issues -f search="keyword"
```
