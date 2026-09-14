# Git and System Inspection

## Git Without a Pager, a Prompt, or Color

Git is built for an interactive terminal. Three settings make it safe for a script, and they can be passed per command
or exported once:

```bash
git --no-pager log --oneline -n 20            # per command
export GIT_PAGER=cat GIT_TERMINAL_PROMPT=0 NO_COLOR=1
git -c color.ui=false -c core.pager=cat diff  # override a configured pager such as delta
```

`GIT_TERMINAL_PROMPT=0` turns a credential prompt into an immediate failure, which is the desired outcome: a prompt
that no one can answer is a hang.

## Machine-Readable Git

| Question                  | Command                                                 |
| ------------------------- | ------------------------------------------------------- |
| What changed?             | `git --no-pager status --porcelain`                     |
| Is the tree dirty?        | `git diff --quiet` and `git diff --cached --quiet`      |
| Which files changed?      | `git --no-pager diff --name-only`                       |
| Current branch            | `git branch --show-current`                             |
| Current commit            | `git rev-parse HEAD`                                    |
| Recent history, one line  | `git --no-pager log --oneline -n 20`                    |
| Structured history        | `git --no-pager log -n 20 --format='%H%x09%an%x09%s'`   |
| Commits ahead of a base   | `git --no-pager log --oneline origin/main..HEAD`        |
| Who last touched a line   | `git --no-pager blame -L 80,90 --porcelain src/main.py` |
| Read state without a lock | `git --no-optional-locks status --porcelain`            |

`--porcelain` output is stable across versions; the human forms are not. `--no-optional-locks` keeps a read-only
inspection from writing the index, which matters when another process — an editor, a watcher, a second agent — holds
it.

`git diff --quiet` exits `1` when there are differences. That is information, not a failure, so check it deliberately
rather than letting a strict shell abort the script.

## Git Commands That Need Consent

Inspection is free. These are not, and each needs an explicit request: `git push`, `git push --force` (prefer
`--force-with-lease`), `git reset --hard`, `git clean -fdx`, `git checkout` over uncommitted work, `git rebase`,
`git commit --amend` on a pushed commit, and any history rewrite. Run `git status --porcelain` before anything that
moves the working tree, and never open an interactive rebase or an editor-based commit: pass `-m`, or let the user do
it.

## Processes

```bash
ps -eo pid,ppid,etime,rss,comm --sort=-rss | head -n 15   # heaviest processes
ps -o pid,etime,cmd -p "$PID" -ww                          # one process, untruncated
pgrep -af 'node .*vite'                                    # find by pattern, with arguments
pkill -TERM -f 'vite --watch'                              # terminate by pattern
```

`-ww` disables the column truncation that hides the end of a long command line. Full-screen monitors such as top, htop,
and btop redraw the terminal and never exit on their own; do not launch them. When a tool such as `procs` is installed,
`procs --tree` is a readable alternative, but `ps` is always present.

Stopping something politely: send `TERM`, wait, then escalate. `kill -9` leaves no chance to flush state or remove a
lockfile, so it is the last step, not the first.

```bash
kill -TERM "$PID"; sleep 2; kill -0 "$PID" 2>/dev/null && kill -KILL "$PID"
```

## Bounding a Command

```bash
timeout 30 npm run build               # SIGTERM at thirty seconds
timeout -k 5 30 ./flaky-script.sh      # SIGKILL five seconds after the SIGTERM
```

`timeout` exits `124` when it fires, which distinguishes a deadline from the command's own failure.

## Services and Logs

On a systemd host, both tools page by default:

```bash
systemctl --no-pager --plain status nginx
systemctl --no-pager list-units --type=service --state=running
journalctl --no-pager -n 200 -u nginx -o cat
journalctl --no-pager --since '10 min ago' -u nginx -o json | jq -r .MESSAGE
```

`-o cat` prints the message alone, and `-o json` gives structured fields. On a host without systemd, the logs are files
under `/var/log`; read them with the harness tools or `tail -n`.

## Edge Cases and Mistakes

- **A git command hangs.** The pager or a credential prompt. `--no-pager` and `GIT_TERMINAL_PROMPT=0`.
- **`git diff` output is full of escape codes.** delta or another pager is configured. Add `-c core.pager=cat`.
- **`index.lock` exists.** Another process is mid-operation. Wait and retry; do not delete the lock file, and prefer
  `--no-optional-locks` for reads.
- **Detached HEAD.** `git branch --show-current` prints nothing. Use `git rev-parse --abbrev-ref HEAD` and handle the
  literal `HEAD` result before assuming a branch name.
- **A checkout destroys uncommitted work.** Check `git status --porcelain` first, and stash or ask.
- **A submodule or worktree looks empty.** Submodules need `git submodule update --init --recursive`; a linked worktree
  has its own HEAD and index.
- **`ps` shows a truncated command.** Add `-ww`.
- **A process refuses to die.** It is in uninterruptible sleep on I/O, or it is a zombie whose parent has not reaped
  it. Neither is fixed by a bigger signal; report it.
- **A background command keeps the session open.** Anything that watches or serves must be bounded by `timeout`, or
  started and stopped deliberately rather than left running.
