---
name: console-usage
description: >
  Use when running shell commands: choosing which command-line tool to reach for, keeping every invocation
  non-interactive, and reading structured output instead of scraping text meant for human eyes. Prefers modern
  replacements — eza, fd, rg, dust, jq, yq, htmlq, mlr, httpie, doggo, batdoc, uv, bun — over the POSIX defaults when
  they are installed, and falls back to ls, find, grep, du, dig, and curl when they are not. Covers filesystem
  navigation and search, diffs, disk metrics, data parsing, document text extraction, HTTP and DNS, git and process
  inspection, archives and file transfer, Python through uv, Node.js through bun or pnpm, and querying the internet
  through gh, glab, llms.txt, or firecrawl. It does not replace the harness's own read, edit, and search tools.
compatibility: Requires a POSIX shell. Every preferred tool is optional and has a named fallback. Commands must run without a pager, a prompt, or a full-screen interface.
metadata:
  writing-style: Chicago Manual of Style
---

# console-usage — Running Commands in a Terminal

A shell command written for a person and a shell command written for an agent are not the same command. The first may
page its output, ask a question, or paint a full-screen interface. The second must finish on its own, write plain text
to standard output, and fail loudly enough that the caller can tell success from silence.

This skill answers two questions: which tool to reach for, and how to invoke it so that the output can be parsed and
the command can never hang. It is a preference list, not a dependency list. Nothing here is required, every entry names
its POSIX fallback, and none of it replaces the harness's own read, edit, and search tools, which remain the first
choice for reading and modifying files.

## The Substitution Table

| Job                      | POSIX fallback      | Preferred | Canonical invocation                           |
| ------------------------ | ------------------- | --------- | ---------------------------------------------- |
| List a directory         | `ls -l`             | eza       | `eza -l --git --icons=never`                   |
| Find files by name       | `find . -name`      | fd        | `fd -t f -e py`                                |
| Search file contents     | `grep -rn`          | rg        | `rg -n --no-heading 'pattern'`                 |
| Directory sizes          | `du -sh -- *`       | dust      | `dust -bP -d 2`                                |
| Query JSON               | none                | jq        | `jq -r '.items[].name'`                        |
| Query YAML, TOML, or XML | none                | yq family | `yq -r '.stages[]' .gitlab-ci.yml`             |
| Query HTML               | none                | htmlq     | `htmlq -t 'h1'`                                |
| Query CSV or TSV         | `awk -F,`           | mlr       | `mlr --icsv --ojson cat data.csv`              |
| Extract document text    | `pdftotext`, catdoc | batdoc    | `batdoc -m report.docx`                        |
| HTTP request             | `curl -fsSL`        | httpie    | `http --ignore-stdin --check-status GET URL`   |
| DNS lookup               | `dig +short`        | doggo     | `doggo example.com A --short`                 |
| Socket list              | `netstat -tulpn`    | ss        | `ss -tulpn`                                    |
| Run a Python script      | `python3 script.py` | uv        | `uv run script.py`                             |
| Run a Python tool once   | `pipx run ruff`     | uvx       | `uvx ruff format`                              |
| Run a Node package once  | `npx --yes pkg`     | bunx      | `bunx pkg`                                     |
| Read forge data          | `curl` plus a token | gh, glab  | `gh api repos/OWNER/REPO --jq .default_branch` |
| Search or scrape the web | none                | firecrawl | `firecrawl search 'query'`                     |

Every flag above was checked against eza 0.23, fd 10.4, ripgrep 15.2, dust 1.2, jq 1.8, yq 4.1, htmlq 0.4,
Miller 6.21, HTTPie 3.2, doggo 1.4, batdoc 1.5, uv 0.12, bun 1.4, pnpm 11, gh 2, and glab 1.117. When a flag is
rejected, the installed version differs from the one documented here; read the tool's own help rather than guessing a
synonym.

## Probe Once, Substitute Silently

Resolve each tool once per session, keep the answer, and move on. A missing tool is not an error and not a reason to
install anything:

```bash
# Resolve the lister once; reuse "$LS" for the rest of the session.
if command -v eza >/dev/null 2>&1; then LS='eza -l --git --icons=never'; else LS='ls -l'; fi
$LS
```

Three rules govern the fallback:

1. Probe with `command -v`, never with `which`, and never by running the tool and inspecting the error.
2. Fall back without comment. The user asked for a directory listing, not for a report on the host's package selection.
3. Never install a tool, add a repository, or call a package manager unless the user asked for exactly that.

## Non-Interactive by Default

Most apparent hangs are a pager, a prompt, or a full-screen interface waiting for a keystroke that will never arrive.

| Hazard              | Symptom                                            | Fix                                                                      |
| ------------------- | -------------------------------------------------- | ------------------------------------------------------------------------ |
| Pager               | Command never returns, or output ends mid-file     | `PAGER=cat`, `git --no-pager`, `GH_PAGER=cat`, `systemctl --no-pager`    |
| Prompt              | Command waits for a password or a yes-or-no answer | `GIT_TERMINAL_PROMPT=0`, `GH_PROMPT_DISABLED=1`, `GLAB_NO_PROMPT=1`      |
| Escape codes        | Output is littered with `\x1b[` sequences          | `NO_COLOR=1`, `CLICOLOR=0`, `--color=never`, `dust -c`                   |
| Full-screen program | Output is a redrawn screen, or nothing at all      | Never launch btop, top, lazygit, or bare fzf; use `fzf --filter 'query'` |
| Redirected stdin    | HTTPie or a REPL waits for input that never comes  | `http --ignore-stdin`, `ssh -n`, `git ... </dev/null`                    |
| Unbounded wait      | A network call hangs past any useful deadline      | `timeout 30 cmd`, `http --timeout=10`, `curl --max-time 10`              |

Export the defaults once, at the start of a session that will run many commands:

```bash
export PAGER=cat GIT_PAGER=cat NO_COLOR=1 CLICOLOR=0 GIT_TERMINAL_PROMPT=0 GH_PROMPT_DISABLED=1 GLAB_NO_PROMPT=1
```

Two further habits keep a command honest. Write `--` before any path that might begin with a hyphen, and separate
machine-read file lists with NUL bytes (`fd -0`, `find -print0`, `xargs -0`) so that a newline in a filename cannot
split one path into two.

## Structured Output over Scraped Text

Human-formatted output is a presentation layer; it changes between versions, wraps at the terminal width, and hides
data behind alignment. Ask for the structured form instead, then parse it with jq:

| Tool     | Structured flag      | Example                                                                 |
| -------- | -------------------- | ----------------------------------------------------------------------- |
| rg       | `--json`             | `rg --json 'TODO' \| jq -r 'select(.type=="match") \| .data.path.text'` |
| dust     | `-j`                 | `dust -j \| jq -r '.name'`                                              |
| doggo    | `-J`                 | `doggo example.com A -J \| jq -r '.responses[].answers[].address'`     |
| httpie   | body only when piped | `http --ignore-stdin GET URL \| jq .`                                   |
| gh, glab | `--jq`, `-F json`    | `gh api /user --jq .login`                                              |
| git      | `--porcelain`, `-z`  | `git --no-pager status --porcelain`                                     |
| Miller   | `--ojson`            | `mlr --icsv --ojson head -n 3 data.csv`                                 |

When a tool has no structured mode, prefer its narrowest human mode — `doggo --short`, `git log --format=%H`, `eza -1` — over
parsing a table that exists for readability.

## Ask the Tool, Not Your Memory

When unsure of a flag, consult the installed tool in this order: `tldr <cmd>` for the common cases, `<cmd> --help` for
the authoritative flag list of the installed version, and `man <cmd>` for semantics and exit codes. Prefer `--help`
over recollection whenever a command will touch the network, delete files, or write outside the working tree.

## Domain References

| Domain                                     | Read for                                                             |
| ------------------------------------------ | -------------------------------------------------------------------- |
| [Filesystem](references/filesystem.md)     | eza, fd, rg, and dust: listing, search, diffing, and disk accounting |
| [Data](references/data.md)                 | jq, the two rival yq programs, xq, tomlq, htmlq, Miller, and batdoc  |
| [Network](references/network.md)           | HTTPie, curl, doggo, resolver order, and socket inspection           |
| [Python](references/python.md)             | uv, uvx, virtual environments, and PEP 723 single-file scripts       |
| [Node.js](references/node.md)              | bun, bunx, pnpm dlx, lockfiles, and the npx fallback                 |
| [Web research](references/web-research.md) | gh, glab, `llms.txt`, firecrawl, and source quality                  |
| [Git and system](references/git-system.md) | Non-interactive git, process inspection, signals, and service logs   |
| [Transfer](references/transfer.md)         | tar, zstd, rsync, ssh in batch mode, and disk capacity               |

## Critical Rules for Agents

1. **The harness first.** Read, edit, and write files with the harness tools. Shell commands are for work the harness
   cannot do: searching at scale, inspecting the system, and running builds.
2. **Read before you write.** Inspect with a read-only command before any command that mutates: `tar -tf` before
   extraction, `rsync --dry-run` before a sync, `git status` before a checkout.
3. **Never install silently.** Substitution is free; installation is a change to the user's machine and needs consent.
4. **Bound every wait.** Any command that touches the network or another host gets a timeout.
5. **Quote and terminate.** Quote every variable expansion, and end option lists with `--` before untrusted paths.
6. **Check exit codes, not prose.** Use `--check-status` for HTTPie and `-f` for curl so that an HTTP 500 fails the
   command instead of returning an error page as if it were data.
7. **One tool per job.** Do not pipe `ls` into `grep` into `awk` when `fd` or `rg` answers the question directly, and
   do not parse a formatted table when the tool offers JSON.
8. **Respect the ignore files, then override deliberately.** fd and rg skip hidden files and anything listed in an
   ignore file; eza hides dotfiles until `-a`. Reach for `--hidden`, `--no-ignore`, or `-uu` only when the target is
   genuinely inside `.git`, `dist`, or `node_modules`.
9. **Nothing destructive by reflex.** `rm -rf`, `git clean -fdx`, `rsync --delete`, `kill -9`, and `git push --force`
   require an explicit request; a dry run precedes each one where the tool supports it.
10. **Report the substitution only when it matters.** Mention the fallback when it changed the result — a truncated
    listing, a skipped ignored file, an unparsed field — and stay quiet otherwise.

## Worked Example

Find every Python file that still calls a deprecated helper, in a repository whose host lacks fd:

```bash
# 1. Probe. fd is absent, rg is present.
command -v fd >/dev/null 2>&1; echo "fd=$?"      # fd=1
command -v rg >/dev/null 2>&1; echo "rg=$?"      # rg=0

# 2. Search with the structured mode, not the pretty one.
rg --json -t py 'legacy_fetch\(' \
  | jq -r 'select(.type == "match") | "\(.data.path.text):\(.data.line_number)"'

# 3. Fall back only for what is missing: no fd, so use the POSIX form, NUL-separated.
find . -name '*.py' -print0 | xargs -0 -n 50 grep -l 'legacy_fetch(' 2>/dev/null
```

```text
src/client.py:88
src/client.py:214
tests/test_client.py:31
```

The report to the user names the files and the count. It does not mention that fd was missing, because the answer is
the same either way.

## Edge Cases, Mistakes, and Failure Handling

- **The command appears to hang.** Suspect a pager or a prompt before suspecting the network. Re-run with `--no-pager`,
  `--ignore-stdin`, or `</dev/null`, and wrap it in `timeout`.
- **A search finds nothing that plainly exists.** fd and rg honor `.gitignore` and skip hidden files. Re-run with
  `--hidden --no-ignore` before concluding the string is absent.
- **`yq` behaves unlike the documented flags.** Two different programs are named `yq`. Run `yq --version`: output that
  names jq is the Python wrapper that takes jq filters, and output that names mikefarah is the Go tool with its own
  expression language. See [references/data.md](references/data.md) before writing either.
- **A tool exists but is stale.** `pnpx` is a deprecated alias of `pnpm dlx`. It still works. Prefer the maintained
  form when it is installed, and do not fail the task over it.
- **jq exits zero on an empty result.** A filter that matches nothing prints nothing and succeeds. Use `jq -e` when
  emptiness should fail the command.
- **The output is escape codes, not text.** A tool detected a terminal that is not there, or a wrapper such as delta is
  configured as the pager. Set `NO_COLOR=1` and bypass the pager rather than filtering the codes out afterward.
- **Filenames with spaces, newlines, or leading hyphens.** Word splitting is the cause of most accidental deletions.
  Use `-print0` or `fd -0` with `xargs -0`, quote expansions, and pass `--` before paths.
- **A flag is rejected outright.** The installed version predates the flag. Check `<cmd> --help`, then use the older
  spelling instead of inventing one; GNU and BSD builds of `ls`, `sed`, `date`, and `tar` differ in exactly this way.
- **`sudo` would fix it.** Stop and ask. Privilege escalation is a decision for the user, not a workaround for a
  permission error.
- **The tool writes outside the working tree.** Caches, lockfiles, and global configuration belong to the user. Prefer
  the project-local form (`uv run`, `bunx`, `--cache-dir`) and say so when a command must write to a home directory.
