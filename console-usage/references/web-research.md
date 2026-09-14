# Querying the Internet

Escalate in this order. Each step is cheaper, better authenticated, and less likely to return a rendering of a page
instead of its data than the step below it.

1. **A dedicated CLI for the service.** `gh` for GitHub, `glab` for GitLab. These handle authentication, reach private
   resources, paginate correctly, and stay inside the service's rate limits.
2. **A machine-oriented endpoint.** Many sites now publish `/llms.txt` or `/llms-full.txt`, a compact map of their
   documentation written for language models. Try it before scraping the rendered site.
3. **firecrawl.** For search, for JavaScript-rendered pages, and for bulk extraction.
4. **A plain HTTP request.** Last, and only for a static document whose URL is already known.

## gh and glab

```bash
gh api repos/OWNER/REPO --jq .default_branch
gh api repos/OWNER/REPO/issues --paginate --jq '.[] | "\(.number)\t\(.title)"'
gh api /search/code -X GET -f q='legacy_fetch repo:OWNER/REPO' --jq '.items[].path'
gh pr view 42 --json title,state,files --jq '.files[].path'
gh release view --json tagName,publishedAt

glab api projects/:fullpath/merge_requests --paginate
glab mr view 42 -F json --jq '.title'
glab ci status --compact                # never pass --live; it redraws and does not exit
glab api 'projects/:fullpath/pipelines?per_page=5' --jq '.[] | "\(.id) \(.status)"'
```

Keep both quiet and non-interactive: `GH_PAGER=cat`, `GH_PROMPT_DISABLED=1`, `GLAB_NO_PROMPT=1`,
`GLAB_GLAMOUR_STYLE=notty`, and `NO_COLOR=1`. Verify authentication with `gh auth status` or `glab auth status` before
concluding that a private resource does not exist; an unauthenticated call returns a 404, not a 401.

Prefer `--jq` over piping to jq when the tool supports it: the filter runs against the parsed response, so pagination
and envelope differences are handled first.

## Documentation Endpoints

```bash
http --ignore-stdin --check-status --body GET https://docs.example.com/llms.txt
http --ignore-stdin --check-status --body GET https://docs.example.com/llms-full.txt
```

`llms.txt` is an index of titled links; `llms-full.txt` inlines the documentation itself and can be very large, so read
the index first and fetch only the sections that matter.

## firecrawl

```bash
firecrawl --status                     # authentication, concurrency, remaining credits
firecrawl search 'ripgrep pcre2 lookaround'
firecrawl scrape https://example.com/docs/page
firecrawl map https://example.com --search pricing
```

When the binary is absent, run it through a package runner: `bunx firecrawl-cli search 'query'`. A dedicated firecrawl
skill set is installed in most harnesses and covers crawling, monitoring, and interaction; prefer it for anything
beyond a single search or scrape.

## Source Quality

- Prefer upstream documentation, then the project's own source code or issue tracker, then everything else.
- Treat forums, news articles, social media posts, and video transcripts as leads, not as evidence. Flag them when they
  are the only support for a claim.
- Verify a version-specific claim against the installed version, not against the newest release notes.
- Cite what was used: the URL, and the date when the content is likely to change.

## Edge Cases and Mistakes

- **HTTP 404 on a resource that exists.** Almost always missing authentication. Check `gh auth status` or
  `glab auth status` first.
- **Only the first page arrived.** Forge APIs paginate at twenty or thirty items. Pass `--paginate`, and never infer a
  total from one page.
- **Rate limited.** Honor `Retry-After`, reduce concurrency, and prefer one paginated CLI call over many scrapes.
- **The scraped page is empty or a spinner.** The content is rendered client-side. Use firecrawl rather than adding
  selectors to a fetch that never receives the data.
- **A token leaked into the transcript.** Pass credentials through the environment and let the CLI read them; do not
  echo them, and do not paste them into a URL.
- **The answer came from a summary of a summary.** Follow the chain to the primary source before acting on it. When no
  primary source can be found, say so and ask the user for a pointer instead of guessing.
- **Robots and terms of service.** Respect them, and prefer an official API to scraping when one exists.
