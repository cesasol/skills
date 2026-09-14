# Node.js: bun, pnpm, and the npx Fallback

## Running a Package Once

| Runner | Command         | Note                                                     |
| ------ | --------------- | -------------------------------------------------------- |
| bun    | `bunx pkg`      | Fastest start; `bun x` is the same command               |
| pnpm   | `pnpm dlx pkg`  | `pnx` in pnpm 11 and later; `pnpx` is a deprecated alias |
| npm    | `npx --yes pkg` | Last resort; `--yes` suppresses the install prompt       |

```bash
bunx skills add cesasol/skills@console-usage
pnpm dlx firecrawl-cli search 'query'
bunx --bun vite build                  # force the Bun runtime instead of Node.js
npx --yes create-vite@latest my-app --template vue
```

Bare `npx pkg` prompts before installing a package that is not present, and that prompt is an apparent hang in a
non-interactive session. Either pass `--yes` or use another runner.

## Installing Dependencies

```bash
bun install --frozen-lockfile
pnpm install --frozen-lockfile
npm ci                                 # requires package-lock.json
```

Use the manager the repository already uses. The evidence is the lockfile — `bun.lock`, `pnpm-lock.yaml`,
`package-lock.json`, `yarn.lock` — and the `packageManager` field in `package.json`. Running a second manager rewrites
the lockfile, produces a large unrelated diff, and can change the resolved dependency tree; that is a decision for the
user, not a convenience.

## Running Project Scripts

```bash
bun run build
pnpm run build
pnpm exec tsc --noEmit                 # a local binary, without a package.json script
bunx --bun tsc --noEmit
```

`pnpm exec` and `bun run` invoke binaries already in `node_modules`; `pnpm dlx` and `bunx` fetch what is absent. Prefer
the local binary when the project declares the dependency, because it is the pinned version.

## Edge Cases and Mistakes

- **A package fails under Bun.** Bun's Node compatibility is close but not complete, most visibly with native addons
  and a few Node APIs. Retry with `pnpm dlx` or `node` before treating it as a broken package.
- **`pnpx` prints a deprecation notice.** It is an alias of `pnpm dlx`. Use the canonical form; do not fail the task.
- **The lockfile changed unexpectedly.** A different manager, or an install without `--frozen-lockfile`, was run.
  Restore it with git and repeat the install with the frozen flag.
- **`npm ci` fails with a lockfile error.** `package-lock.json` is missing or out of sync with `package.json`. Do not
  fix it with `npm install` in a CI context; report the mismatch.
- **A global install is proposed.** `npm i -g` writes outside the project and often needs privileges. Use a runner
  (`bunx`, `pnpm dlx`) instead, or ask.
- **Postinstall scripts are blocked.** pnpm and bun restrict them by design. Allow a specific package deliberately
  (`pnpm dlx --allow-build pkg`) rather than disabling the protection wholesale.
- **The build watches instead of exiting.** `vite`, `tsc --watch`, and `next dev` never return. Use the build or
  check-only form, and wrap anything uncertain in `timeout`.
- **`node_modules` is enormous.** Do not search it. fd and rg skip it through `.gitignore`; keep it that way instead of
  passing `--no-ignore` across the whole tree.
