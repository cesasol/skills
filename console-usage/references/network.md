# Network: HTTP, DNS, and Sockets

## HTTPie

HTTPie changes its defaults when standard output is not a terminal: it prints the response body only, applies no
colors, and does not suppress binary data. Piped output is therefore already parseable, which is why `http ... | jq .`
needs no extra flags.

Two flags belong on nearly every non-interactive call:

- `--ignore-stdin`, because when stdin is redirected HTTPie assumes a request body is coming and waits for it. Inside a
  loop, a pipeline, or a job runner, that wait is the classic apparent hang.
- `--check-status`, because without it an HTTP 404 or 500 exits zero and the error page is handed back as if it were
  data. With it, the exit code is `4` for a 4xx response and `5` for a 5xx response.

```bash
http --ignore-stdin --check-status GET https://api.example.com/v1/runs limit==10
http --ignore-stdin --check-status POST https://api.example.com/v1/runs name=nightly retries:=3
http --ignore-stdin --check-status --follow --timeout=10 GET https://example.com/redirecting
http --ignore-stdin GET https://api.example.com/v1/runs Authorization:"Bearer $TOKEN" | jq -r '.items[].id'
http --ignore-stdin --print=h HEAD https://example.com          # headers only
http --ignore-stdin --offline POST https://example.com a=1       # show the request, send nothing
http --ignore-stdin --download --output archive.tgz GET https://example.com/archive.tgz
```

Syntax worth remembering: `key=value` is a JSON string field, `key:=value` is raw JSON (numbers, booleans, arrays),
`key==value` is a query-string parameter, `Header:value` is a header, and `-f` switches the body to form encoding.
Redirects are not followed unless `--follow` is passed.

Fallback with curl, where the equivalent safety flags are `-f` for status checking and `--max-time` for the deadline:

```bash
curl -fsSL --max-time 10 https://api.example.com/v1/runs | jq .
curl -fsS --max-time 10 -X POST -H 'Content-Type: application/json' -d '{"name":"nightly"}' https://api.example.com/v1/runs
```

`-f` fails on HTTP errors, `-s` silences the progress meter, `-S` keeps error messages, and `-L` follows redirects.
Never use a bare `curl URL` in a pipeline: it succeeds on an error page and floods the transcript with a progress bar.

## doggo: DNS

```bash
doggo example.com A                                 # human-readable answer
doggo example.com A --short                         # answer data only, one line per record
doggo example.com A -J | jq -r '.responses[].answers[].address'
doggo example.com MX @1.1.1.1                       # ask a specific resolver
doggo example.com A @tcp://1.1.1.1                  # force TCP
doggo example.com A @tls://1.1.1.1                  # DNS over TLS
doggo example.com A @https://dns.google/dns-query   # DNS over HTTPS
doggo example.com A --color=false --time            # no escape codes, report latency
```

doggo queries DNS directly, so it never consults `/etc/hosts`, `nsswitch.conf`, or a container's resolver overrides.
When the question is "what will this program actually connect to," ask the system resolver instead:

```bash
getent hosts example.com                # what the OS resolves, including /etc/hosts
```

`dig +short example.com A` is the universal fallback.

## Sockets and Interfaces

```bash
ss -tulpn                               # listening TCP and UDP sockets with owning process
ss -tp state established                # current connections
ss -tn 'dport = :443'                   # filter by port
ip -brief address                       # interfaces and addresses, one line each
ip route get 1.1.1.1                    # which interface and gateway a destination uses
```

`ss` needs privileges to show process names for sockets it does not own; without them the `users:` column is simply
empty, which is not an error worth escalating over. Fallbacks: `netstat -tulpn` and `ifconfig -a` on hosts without
iproute2.

## Edge Cases and Mistakes

- **HTTPie seems to hang.** Stdin was redirected. Add `--ignore-stdin`.
- **A failed request looked successful.** `--check-status` or `curl -f` was missing. The body of an error page parses
  as text and silently poisons whatever consumes it.
- **A request stalls behind a proxy.** Honor `HTTPS_PROXY`, `HTTP_PROXY`, and `NO_PROXY`; both HTTPie and curl read
  them. A hung request against an internal host is usually a proxy that should have been bypassed.
- **TLS verification fails.** Do not reach for `--verify=no` or `curl -k`. Report the failure; a bad certificate is
  either a real problem or a decision for the user.
- **Rate limiting.** Treat HTTP 429 and 403-with-a-reset-header as backoff signals: honor `Retry-After`, and prefer a
  forge CLI, which handles pagination and throttling itself. See [web-research.md](web-research.md).
- **The name resolves in the shell but not in doggo.** The entry lives in `/etc/hosts` or a local resolver. Confirm with
  `getent hosts`.
- **Secrets in the transcript.** Pass tokens through environment variables (`Authorization:"Bearer $TOKEN"`), never as
  a literal on the command line, and avoid `-v` on authenticated calls, which echoes the header.
- **A download is silently truncated.** Use `--download` with HTTPie or `-o` with curl, verify the size or checksum,
  and set a timeout so that a stalled transfer fails instead of hanging.
