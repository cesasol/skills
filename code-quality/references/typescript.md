# TypeScript and JavaScript — pnpm, oxlint, tsc

The JavaScript baseline is pnpm for installs, oxlint for the fast lint pass, `tsc --noEmit` for types, and Prettier for formatting. eslint joins only when the project genuinely needs type-aware rules
or a plugin oxlint does not implement.

## Layout

| Concern | File | Notes |
| --- | --- | --- |
| Manifest | `package.json` | Must carry a `packageManager` field, and no tool block over forty lines. |
| Lock | `pnpm-lock.yaml` | Committed. CI installs with `--frozen-lockfile`. |
| Lint | `.oxlintrc.json` | Nested configs are supported; the nearest one wins per file. |
| Types | `tsconfig.json` | `"strict": true` is not optional. |
| Format | `.prettierrc.json` | One formatter only. |

## Package Manager

Pin the package manager in the manifest so Corepack and CI agree with the developer:

```json
{
  "packageManager": "pnpm@10.20.0",
  "scripts": {
    "lint": "oxlint --max-warnings 0",
    "lint:fix": "oxlint --fix",
    "typecheck": "tsc --noEmit",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "test": "vitest run --coverage"
  }
}
```

Install with `pnpm install --frozen-lockfile` in every CI job. A lockfile that CI is allowed to update is not a lockfile.

Keep the manifest thin. `package.json` holds dependencies, metadata, and a handful of script aliases; it is not a configuration file. Once `"scripts"`, `"eslintConfig"`, `"prettier"`, or `"jest"`
reaches forty lines, that block must move out: configuration to the tool's own file (`eslint.config.js`, `.prettierrc.json`, `jest.config.ts`), and a long script list to `just` recipes, leaving only
the few entries a tool or host platform genuinely requires. JSON has no comments, so a large block there cannot even explain itself.

## oxlint

oxlint is the default linter: it needs no plugin bootstrapping, runs in milliseconds on a large tree, and covers the rule sets most projects actually enforce.

```json
{
  "$schema": "https://raw.githubusercontent.com/oxc-project/oxc/main/npm/oxlint/configuration_schema.json",
  "plugins": ["typescript", "unicorn", "oxc", "import"],
  "categories": {
    "correctness": "error",
    "suspicious": "error",
    "perf": "warn"
  },
  "rules": {
    "no-console": "error",
    "typescript/no-explicit-any": "error"
  },
  "ignorePatterns": ["dist", "coverage", "**/*.generated.ts"]
}
```

```bash
pnpm dlx oxlint --max-warnings 0        # lint, warnings are errors
pnpm dlx oxlint --fix                   # autofix
pnpm dlx oxlint --type-aware            # opt into the type-aware rules that require a program
```

`--max-warnings 0` is mandatory in CI. A linter whose warnings accumulate has already stopped working.

## When eslint Is Justified

Add eslint only for a concrete, named need: framework plugins without an oxlint equivalent (`eslint-plugin-vue`, `@next/eslint-plugin-next`), or type-aware rule sets the project depends on. In that
case run oxlint first as the fast gate and eslint second, and turn off the eslint rules oxlint already covers with `eslint-plugin-oxlint`:

```js
// eslint.config.js (flat config)
import oxlint from "eslint-plugin-oxlint";

export default [
  // ...framework and type-aware configs...
  ...oxlint.configs["flat/recommended"], // must stay last
];
```

Record the reason for the second linter in the repository. Two linters without a written rationale become two sets of ignored warnings.

## TypeScript

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "verbatimModuleSyntax": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "target": "es2022",
    "skipLibCheck": true,
    "noEmit": true
  },
  "include": ["src", "tests"]
}
```

- `tsc --noEmit` is the type gate. A bundler that strips types is not a type checker.
- In Vue or Nuxt projects use `vue-tsc --noEmit`; in Svelte projects use `svelte-check`.
- Forbid `@ts-ignore`. Require `@ts-expect-error` with a reason, because it fails once the underlying error disappears.
- A monorepo uses one base `tsconfig.json` at the root, with each package extending it through `"extends"`.

## Formatting

Prettier remains the safe default, and `.prettierignore` should exclude generated output. `oxfmt` is the emerging oxc formatter; adopt it only when the team accepts pre-1.0 tooling, and never run
both.

## Hooks

```toml
[[repos]]
repo = "https://github.com/oxc-project/mirrors-oxlint"
rev = "v1.82.0"
hooks = [{ id = "oxlint", args = ["--max-warnings", "0"] }]

[[repos]]
repo = "local"
hooks = [
  { id = "typecheck", name = "tsc --noEmit", entry = "pnpm run typecheck", language = "system", files = "\\.(ts|tsx|vue)$", pass_filenames = false },
]
```

Type checking is whole-program work, so it must set `pass_filenames = false`. If the project is large enough that `tsc` takes longer than a few seconds, drop the hook and keep the CI job.

## just Recipes

The standard names, with pnpm bodies. [just-recipes.md](just-recipes.md) covers the app, library, and monorepo variants.

```make
# An app also gates on `build`: a type-clean project can still fail to bundle.
ci: fmt-check lint typecheck test build

setup:
    pnpm install --frozen-lockfile
    uvx prek install

# Read-only. `--fix` belongs in `fix`.
lint:
    pnpm exec oxlint --max-warnings 0

fix: && fmt
    pnpm exec oxlint --fix

fmt:
    pnpm exec prettier --write .

fmt-check:
    pnpm exec prettier --check .

# vue-tsc for Vue, svelte-check for Svelte.
typecheck:
    pnpm exec tsc --noEmit

test:
    pnpm exec vitest run --coverage

build:
    pnpm run build

# Dev server with HMR.
dev:
    pnpm run dev

# Serve the build output the way the deployment does.
start:
    node .output/server/index.mjs
```

The `package.json` scripts stay thin: `just` owns the workflow, and a script exists only where a tool or host platform demands one. Nuxt needs `nuxt prepare` in `setup`, not in `typecheck`.

## Failure Modes

- **`pnpm install` rewrites the lockfile in CI.** The manifest and lockfile disagree. Fix it locally, commit the lockfile, and keep `--frozen-lockfile` in CI.
- **oxlint passes but the build fails on types.** oxlint is not a type checker. Keep `tsc --noEmit` as a separate gate.
- **eslint and oxlint report the same rule twice.** `eslint-plugin-oxlint` is missing or not last in the flat config array.
- **Warnings pile up.** The `--max-warnings 0` flag is missing somewhere; add it to the script, not only to the CI invocation.
- **Generated clients fail the linter.** Exclude the generated directory in `ignorePatterns` and in `.prettierignore`, and check the generator output into the repository so CI diffs it.
- **A workspace package has no lint script.** Lint from the root with one command over the whole tree rather than adding per-package scripts that nobody runs.
