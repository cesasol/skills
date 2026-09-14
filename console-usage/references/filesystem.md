# Filesystem: Listing, Search, Diffing, and Sizes

Four tools cover nearly all filesystem work from a shell: eza to look, fd to locate, rg to read across files, and dust
to account for space. Reading the contents of one known file is not on that list; that is the harness read tool's job.

## eza: Listing

| Need                   | Command                       | Note                                     |
| ---------------------- | ----------------------------- | ---------------------------------------- |
| Default listing        | `eza -l --git --icons=never`  | `--git` adds the per-file status column  |
| Include hidden entries | `eza -la --git --icons=never` | `-aa` also shows `.` and `..`            |
| Tree, bounded depth    | `eza -T -L 2 --icons=never`   | Unbounded trees flood the context window |
| One name per line      | `eza -1`                      | Safe to read line by line                |
| Newest last            | `eza -l --sort=date`          | `-r` reverses; `eza --help` lists fields |
| Skip ignored files     | `eza --git-ignore`            | Honors `.gitignore`                      |

Always pass `--icons=never`. Glyphs add bytes, may render as replacement characters, and shift column offsets. Do not
parse the long listing; it is aligned for people. Use `fd -0` plus `stat` when sizes or timestamps must be exact, and
remember that `--git` is silent outside a repository.

Fallback: `ls -l`, or `ls -1` when the output will be read programmatically.

## fd: Finding Files

fd takes a regular expression, matches against the file name, is case-insensitive until the pattern contains an
uppercase character, and skips hidden files and anything ignored by version control.

| Need                       | Command                  |
| -------------------------- | ------------------------ |
| By extension               | `fd -t f -e py`          |
| By name pattern            | `fd -t f 'test_.*\.py$'` |
| Glob semantics instead     | `fd --glob '*.tar.zst'`  |
| Directories only           | `fd -t d node_modules`   |
| Include hidden and ignored | `fd -H -I -t f secrets`  |
| Within one directory       | `fd -t f -e md . docs/`  |
| Bounded depth              | `fd -d 2 -t f`           |
| NUL-separated for pipes    | `fd -0 -t f -e py`       |
| Batch a command            | `fd -e py -X wc -l`      |

`-x` runs the command once per match; `-X` runs it once with all matches. Prefer `-X` for speed and `-x` when the
command takes a single path. Fallback: `find . -type f -name '*.py' -print0`.

## rg: Searching Contents

ripgrep compiles patterns with Rust's regular-expression engine, which matches on bytes and has no backtracking, so
lookaround and backreferences are unavailable unless the build includes PCRE2. Check with `rg --pcre2-version`, then
pass `-P` to opt in. Like fd, rg respects ignore files and skips hidden and binary files.

| Need                      | Command                        |
| ------------------------- | ------------------------------ |
| Match with line numbers   | `rg -n --no-heading 'pattern'` |
| Files with a match        | `rg -l 'pattern'`              |
| Count per file            | `rg -c 'pattern'`              |
| Literal string, no regex  | `rg -F 'a.b[c]'`               |
| Whole word                | `rg -w 'id'`                   |
| One language only         | `rg -t py 'import requests'`   |
| Exclude a directory       | `rg -g '!dist/**' 'pattern'`   |
| Context lines             | `rg -C 3 'panic'`              |
| Search ignored files too  | `rg -uu 'pattern'`             |
| Machine-readable results  | `rg --json 'pattern'`          |
| List candidate files only | `rg --files -g '*.toml'`       |

`-u` relaxes filtering one step at a time: `-u` searches ignored files, `-uu` also searches hidden files, and `-uuu`
also searches binaries. The `--json` stream emits one object per line with `type` values of `begin`, `match`, `end`,
and `summary`; filter with `jq -r 'select(.type == "match")'`. Fallback: `grep -rn --exclude-dir=.git`.

## Printing a File from a Shell

Use the harness read tool. It returns the file with line numbers, without a pager, and without spending a subprocess.
A shell is warranted only when the bytes must flow into another command:

```bash
sed -n '40,80p' src/main.py        # a slice, for a pipeline
wc -l src/main.py                  # a measurement, not a read
```

Syntax highlighters such as bat exist for human readers. They add escape codes, decoration, and a pager to output that
an agent must parse, so they have no place in this workflow.

## Diffing

For a diff an agent will read, keep it plain. delta is a pager-side renderer: it emits colors and box drawing that are
useless in a transcript and hostile to a parser.

```bash
git --no-pager diff -- src/               # plain unified diff
git -c core.pager=cat diff --stat         # bypass a configured delta pager
git --no-pager diff --name-only           # machine-readable file list
diff -u old.txt new.txt                   # outside a repository
```

Read delta's rendering only when the user will look at it. Note that `diff` exits `1` when files differ, which is not
a failure; `git diff --quiet` exits `1` for the same reason and is the right check for "is the tree dirty."

## dust: Disk Usage

| Need                         | Command                | Note                                      |
| ---------------------------- | ---------------------- | ----------------------------------------- |
| Quiet, parseable tree        | `dust -bP -d 2`        | No percent bars, no progress indicator    |
| JSON for large trees         | `dust -j`              | Pipe to jq; the tree can be enormous      |
| Apparent size, not on disk   | `dust -s`              | Matches `du --apparent-size`              |
| Largest files, not folders   | `dust -F`              | `-D` restricts to directories             |
| Exclude a path               | `dust -X node_modules` | Repeatable                                |
| Count files instead of bytes | `dust -f`              | Useful when inodes, not bytes, are scarce |
| Plain text, no color         | `dust -c`              | Combine with `-P` in scripts              |

dust follows no symlinks by default and stays on one filesystem with `-x`. On a network mount it is as slow as the
mount; scope it with a path and `-d`. Fallback: `du -sh -- * | sort -h`.

## Edge Cases and Mistakes

- **The file is there but nothing finds it.** It is hidden or ignored. `fd -H -I`, `rg -uu`, `eza -la`.
- **A pattern with `(`, `[`, or `.` returns nothing.** It was read as a regular expression. Use `rg -F` or `fd --glob`.
- **Lookaround fails in rg.** The default engine has none; add `-P` when `rg --pcre2-version` reports a PCRE2 build.
- **A path begins with a hyphen.** Terminate options first: `rg -n 'x' -- -weird-name.txt`.
- **Filenames contain spaces or newlines.** Use `fd -0` or `find -print0` with `xargs -0`; never a bare `for` loop over
  unquoted output.
- **A tree listing floods the output.** Always bound depth (`eza -L 2`, `fd -d 2`, `dust -d 2`) before listing an
  unfamiliar directory.
- **Sizes disagree with `du`.** dust reports disk usage by default and apparent size with `-s`; sparse files and
  compressed filesystems make the two differ legitimately.
- **eza shows no git column.** The path is outside a repository, or the repository is unreadable.
