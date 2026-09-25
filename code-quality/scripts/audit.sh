#!/usr/bin/env bash
#
# audit.sh — report deterministic quality-baseline gaps for a repository.
#
# The script never writes to the repository. It detects every stack in the tree,
# including nested packages in a monorepo, then reports what the baseline is
# missing: a prek hook config, a justfile with a `ci` recipe, a pipeline that
# runs those checks, a dependency lockfile, and the formatter, linter, and type
# checker that each stack requires.
#
# Usage:
#   audit.sh [--json] [--strict] [PATH]
#
# Options:
#   --json      emit machine-readable findings instead of the text report
#   --strict    treat warnings as failures
#   -h, --help  show this help
#
# Exit codes:
#   0  no gaps (warnings may remain unless --strict is given)
#   1  at least one gap, or a warning under --strict
#   2  usage error

set -euo pipefail

JSON=0
STRICT=0
ROOT="."
MAX_PROJECTS=8

# A tool's configuration may share the project manifest only while it stays
# small. Past this many lines it must move to the tool's own file.
INLINE_CONFIG_MAX_LINES=40

usage() {
	sed -e '1d' -e '/^[^#]/,$d' -e 's/^#\{1,\} \{0,1\}//' "$0" | sed '/./,$!d'
}

while [ $# -gt 0 ]; do
	case "$1" in
	--json) JSON=1 ;;
	--strict) STRICT=1 ;;
	-h | --help)
		usage
		exit 0
		;;
	-*)
		printf 'audit.sh: unknown option: %s\n' "$1" >&2
		exit 2
		;;
	*) ROOT="$1" ;;
	esac
	shift
done

if [ ! -d "$ROOT" ]; then
	printf 'audit.sh: not a directory: %s\n' "$ROOT" >&2
	exit 2
fi
ROOT="$(cd "$ROOT" && pwd)"

# ── file inventory ───────────────────────────────────────────────────────────
#
# The inventory lives in a temp file, never in a pipeline. Piping a large list
# into `grep -q` makes the writer die of SIGPIPE, and `set -o pipefail` then
# reports a false negative.

INVENTORY="$(mktemp -t quality-audit.XXXXXX)"
trap 'rm -f "$INVENTORY"' EXIT

VENDOR_RE='(^|/)(node_modules|vendor|\.venv|venv|target|dist|build|\.git|__pycache__)/'

if command -v git >/dev/null 2>&1 && git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
	git -C "$ROOT" ls-files >"$INVENTORY" 2>/dev/null || true
else
	find "$ROOT" -type f 2>/dev/null | sed "s|^${ROOT}/||" >"$INVENTORY" || true
fi
grep -Ev "$VENDOR_RE" "$INVENTORY" >"${INVENTORY}.clean" 2>/dev/null || true
mv "${INVENTORY}.clean" "$INVENTORY" 2>/dev/null || true

files_match() { grep -Eq -- "$1" "$INVENTORY"; }

count_match() { grep -Ec -- "$1" "$INVENTORY" || true; }

# abs DIR FILE — absolute path of FILE inside the relative project dir DIR.
abs() {
	if [ "$1" = "." ]; then printf '%s/%s' "$ROOT" "$2"; else printf '%s/%s/%s' "$ROOT" "$1" "$2"; fi
}

# rel DIR FILE — repository-relative path of FILE inside DIR.
rel() {
	if [ "$1" = "." ]; then printf '%s' "$2"; else printf '%s/%s' "$1" "$2"; fi
}

exists() { [ -e "${ROOT}/$1" ]; }

any_exists() {
	local candidate
	for candidate in "$@"; do
		if [ -e "${ROOT}/${candidate}" ]; then return 0; fi
	done
	return 1
}

# toml_tools FILE — distinct `tool.<name>` prefixes configured in a TOML file.
toml_tools() {
	[ -f "$1" ] || return 0
	grep -Eo '^[[:space:]]*\[+tool\.[A-Za-z0-9_-]+' "$1" 2>/dev/null |
		sed -e 's/^[[:space:]]*\[\+tool\.//' |
		sort -u
}

# toml_tool_lines FILE NAME — lines that `[tool.NAME...]` occupies in the file.
toml_tool_lines() {
	[ -f "$1" ] || {
		printf '0'
		return 0
	}
	awk -v prefix="tool.$2" '
		/^[[:space:]]*\[/ {
			inside = 0
			header = $0
			sub(/^[[:space:]]*\[+/, "", header)
			sub(/\]+.*$/, "", header)
			if (header == prefix || index(header, prefix ".") == 1) { inside = 1 }
		}
		inside { count++ }
		END { printf "%d", count + 0 }
	' "$1"
}

# json_key_lines FILE KEY — lines that a top-level JSON key occupies.
json_key_lines() {
	[ -f "$1" ] || {
		printf '0'
		return 0
	}
	awk -v key="$2" '
		BEGIN { pattern = "^[[:space:]]*\"" key "\"[[:space:]]*:"; state = 0; depth = 0; count = 0 }
		state == 0 && $0 ~ pattern { state = 1; depth = 0 }
		state == 1 {
			count++
			tmp = $0; opens = gsub(/[{[]/, "", tmp)
			tmp = $0; closes = gsub(/[}\]]/, "", tmp)
			depth += opens - closes
			if (depth <= 0) { state = 2 }
		}
		END { printf "%d", count + 0 }
	' "$1"
}

# extraction_target NAME — the dedicated file an oversized block belongs in.
extraction_target() {
	case "$1" in
	ruff) printf 'ruff.toml' ;;
	ty) printf 'ty.toml' ;;
	mypy) printf 'mypy.ini' ;;
	pytest) printf 'pytest.ini' ;;
	coverage) printf '.coveragerc' ;;
	pyright) printf 'pyrightconfig.json' ;;
	poetry | uv | hatch | setuptools) printf '' ;;
	eslintConfig) printf 'eslint.config.js' ;;
	prettier) printf '.prettierrc.json' ;;
	oxlint) printf '.oxlintrc.json' ;;
	jest) printf 'jest.config.ts' ;;
	stylelint) printf '.stylelintrc.json' ;;
	babel) printf 'babel.config.js' ;;
	commitlint) printf 'commitlint.config.js' ;;
	lint-staged) printf 'lint-staged.config.js' ;;
	scripts) printf 'just recipes' ;;
	*) printf '%s' "a dedicated config file" ;;
	esac
}

# contains PATTERN FILE... — extended-regex search over the files that exist.
contains() {
	local pattern="$1"
	shift
	local file
	for file in "$@"; do
		if [ -f "${ROOT}/${file}" ] && grep -Eq -- "$pattern" "${ROOT}/${file}"; then
			return 0
		fi
	done
	return 1
}

# find_up DIR PATTERN FILE... — walk DIR and its ancestors for the first FILE
# that exists and, when PATTERN is non-empty, matches it. Prints the relative
# path of the hit so the caller can tell local config from inherited config.
find_up() {
	local dir="$1" pattern="$2"
	shift 2
	local current="$dir" candidate path hit=""
	while :; do
		for candidate in "$@"; do
			path="$(abs "$current" "$candidate")"
			if [ -f "$path" ] || [ -d "$path" ]; then
				if [ -z "$pattern" ] || grep -Eq -- "$pattern" "$path" 2>/dev/null; then
					hit="$(rel "$current" "$candidate")"
					printf '%s' "$hit"
					return 0
				fi
			fi
		done
		if [ "$current" = "." ]; then return 1; fi
		current="$(dirname "$current")"
	done
}

# project_dirs BASENAME — relative directories that hold a manifest file.
project_dirs() {
	local base="$1"
	grep -E "(^|/)${base}\$" "$INVENTORY" 2>/dev/null |
		sed -e 's|[^/]*$||' -e 's|/$||' -e 's|^$|.|' |
		sort -u |
		head -n "$MAX_PROJECTS"
}

workflow_files() { grep -E '^\.github/workflows/.*\.ya?ml$' "$INVENTORY" 2>/dev/null || true; }

hook_config() {
	local candidate
	for candidate in prek.toml .pre-commit-config.yaml .pre-commit-config.yml; do
		if [ -f "${ROOT}/${candidate}" ]; then
			printf '%s' "$candidate"
			return 0
		fi
	done
	return 1
}

justfile_path() {
	local candidate
	for candidate in justfile Justfile .justfile; do
		if [ -f "${ROOT}/${candidate}" ]; then
			printf '%s' "$candidate"
			return 0
		fi
	done
	return 1
}

# recipe_list JUSTFILE — every recipe name the justfile exposes, one per line.
# `just --summary` is authoritative when the CLI is installed; the grep fallback
# keeps the audit usable on a machine that has no just.
recipe_list() {
	local just="$1" summary
	if command -v just >/dev/null 2>&1; then
		if summary="$(just --justfile "${ROOT}/${just}" --working-directory "$ROOT" --summary 2>/dev/null)"; then
			tr ' ' '\n' <<<"$summary"
			return 0
		fi
	fi
	grep -Eo '^[a-zA-Z_][a-zA-Z0-9_-]*([ \t][^:=]*)?:($|[^=])' "${ROOT}/${just}" 2>/dev/null |
		sed -E 's/[ \t:].*$//' || true
}

# has_recipe NAMES NAME — NAME appears in the newline-separated recipe list.
has_recipe() {
	printf '%s\n' "$1" | grep -qx -- "$2"
}

# recipe_body JUSTFILE NAME — the recipe's dependencies and body, when just can
# print them. Empty output means "unknown", never "clean".
recipe_body() {
	local just="$1" name="$2"
	command -v just >/dev/null 2>&1 || return 0
	just --justfile "${ROOT}/${just}" --working-directory "$ROOT" --show "$name" 2>/dev/null || true
}

contains_in_hooks() {
	local config
	config="$(hook_config || true)"
	[ -n "$config" ] || return 1
	grep -Eq -- "$1" "${ROOT}/${config}"
}

contains_in_ci() {
	local pattern="$1" file
	if contains "$pattern" .gitlab-ci.yml .gitlab-ci.yaml; then return 0; fi
	while IFS= read -r file; do
		[ -n "$file" ] || continue
		if [ -f "${ROOT}/${file}" ] && grep -Eq -- "$pattern" "${ROOT}/${file}"; then return 0; fi
	done < <(workflow_files)
	if [ -d "${ROOT}/.gitlab" ] && grep -RqE -- "$pattern" "${ROOT}/.gitlab" 2>/dev/null; then return 0; fi
	return 1
}

# gate_exists DIR PATTERN — the tool runs in a hook, a justfile recipe, a
# package script, or a pipeline job. A gate that exists nowhere is not a gate.
gate_exists() {
	local dir="$1" pattern="$2" just
	if contains_in_hooks "$pattern"; then return 0; fi
	just="$(justfile_path || true)"
	if [ -n "$just" ] && grep -Eq -- "$pattern" "${ROOT}/${just}"; then return 0; fi
	if [ "$dir" != "." ]; then
		if contains "$pattern" "$(rel "$dir" justfile)" "$(rel "$dir" package.json)"; then return 0; fi
	elif contains "$pattern" package.json; then
		return 0
	fi
	if contains_in_ci "$pattern"; then return 0; fi
	return 1
}

# ── findings ─────────────────────────────────────────────────────────────────

STATUSES=()
AREAS=()
CHECKS=()
DETAILS=()
STACKS=()

record() {
	STATUSES+=("$1")
	AREAS+=("$2")
	CHECKS+=("$3")
	DETAILS+=("$4")
}

ok() { record ok "$1" "$2" "$3"; }
gap() { record gap "$1" "$2" "$3"; }
warn() { record warn "$1" "$2" "$3"; }

add_stack() {
	local stack
	for stack in ${STACKS[@]+"${STACKS[@]}"}; do
		if [ "$stack" = "$1" ]; then return 0; fi
	done
	STACKS+=("$1")
}

# area STACK DIR — findings are labelled with the package they belong to.
area() {
	if [ "$2" = "." ]; then printf '%s' "$1"; else printf '%s (%s)' "$1" "$2"; fi
}

# audit_inline_config SCOPE MANIFEST — a tool block that outgrows the shared
# manifest must move to the tool's own file.
audit_inline_config() {
	local scope="$1" manifest="$2" name lines target
	[ -f "${ROOT}/${manifest}" ] || return 0

	case "$manifest" in
	*pyproject.toml)
		while IFS= read -r name; do
			[ -n "$name" ] || continue
			target="$(extraction_target "$name")"
			[ -n "$target" ] || continue
			lines="$(toml_tool_lines "${ROOT}/${manifest}" "$name")"
			if [ "$lines" -ge "$INLINE_CONFIG_MAX_LINES" ]; then
				gap "$scope" "config size" "[tool.${name}] spans ${lines} lines in ${manifest}; extract it to ${target} (limit ${INLINE_CONFIG_MAX_LINES})"
			fi
		done < <(toml_tools "${ROOT}/${manifest}")
		;;
	*package.json)
		for name in scripts eslintConfig prettier oxlint jest stylelint babel commitlint lint-staged; do
			lines="$(json_key_lines "${ROOT}/${manifest}" "$name")"
			if [ "$lines" -ge "$INLINE_CONFIG_MAX_LINES" ]; then
				target="$(extraction_target "$name")"
				gap "$scope" "config size" "\"${name}\" spans ${lines} lines in ${manifest}; move it to ${target} (limit ${INLINE_CONFIG_MAX_LINES})"
			fi
		done
		;;
	esac
}

# ── universal baseline ───────────────────────────────────────────────────────

audit_universal() {
	local config just pipeline count

	if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
		ok universal "version control" "git repository"
	else
		warn universal "version control" "not a git repository, so hooks cannot be installed"
	fi

	config="$(hook_config || true)"
	if [ -n "$config" ]; then
		ok universal "hook runner" "$config"
		if [ "$config" != "prek.toml" ]; then
			warn universal "hook format" "${config} found; prek.toml is preferred for new work"
		fi
		if contains_in_hooks 'gitleaks'; then
			ok universal "secret scanning" "gitleaks hook"
		else
			gap universal "secret scanning" "no gitleaks hook in ${config}"
		fi
		if contains_in_hooks 'trailing-whitespace|end-of-file-fixer|check-yaml'; then
			ok universal "hygiene hooks" "builtin hooks configured"
		else
			warn universal "hygiene hooks" "no builtin whitespace or syntax hooks in ${config}"
		fi
	else
		gap universal "hook runner" "no prek.toml and no .pre-commit-config.yaml"
		gap universal "secret scanning" "no gitleaks hook, because there is no hook config"
	fi

	# The recipe set itself is audited in audit_recipes, which runs after stack
	# detection so it can judge the conditional recipes too.
	just="$(justfile_path || true)"
	if [ -n "$just" ]; then
		ok universal "task runner" "$just"
	else
		gap universal "task runner" "no justfile"
		gap universal "ci recipe" "no justfile, so \`just ci\` cannot exist"
	fi

	pipeline=""
	if any_exists .gitlab-ci.yml .gitlab-ci.yaml; then
		pipeline="GitLab CI"
	elif [ -n "$(workflow_files)" ]; then
		pipeline="GitHub Actions"
	fi

	if [ -n "$pipeline" ]; then
		ok universal "pipeline" "$pipeline"
		if contains_in_ci 'prek run|just ci|pre-commit run'; then
			ok universal "pipeline gate" "the pipeline runs the hook suite or just ci"
		else
			gap universal "pipeline gate" "the pipeline never runs \`prek run --all-files\` or \`just ci\`"
		fi
		if contains_in_ci 'allow_failure: *true|continue-on-error: *true'; then
			warn universal "pipeline strictness" "allow_failure or continue-on-error is used; confirm no quality job is exempt"
		fi
	else
		gap universal "pipeline" "no .gitlab-ci.yml and no .github/workflows/*.yml"
		gap universal "pipeline gate" "no pipeline, so nothing enforces the checks on merge"
	fi

	if exists .editorconfig; then
		ok universal "editorconfig" ".editorconfig"
	else
		warn universal "editorconfig" "no .editorconfig"
	fi

	count="$(count_match '\.mdx?$')"
	if [ "$count" -gt 0 ]; then
		if any_exists rumdl.toml .rumdl.toml; then
			ok markdown "linter" "rumdl config"
		elif any_exists .markdownlint.json .markdownlint.yaml .markdownlint.yml .markdownlint-cli2.jsonc; then
			warn markdown "linter" "markdownlint config found; rumdl is preferred"
		else
			warn markdown "linter" "${count} Markdown files and no rumdl.toml"
		fi
	fi
}

# ── python ───────────────────────────────────────────────────────────────────

audit_python_project() {
	local dir="$1" workspace_root="$2" scope hit tests_re
	scope="$(area python "$dir")"

	if [ -f "$(abs "$dir" pyproject.toml)" ]; then
		if [ "$dir" = "." ]; then ok "$scope" "manifest" "pyproject.toml"; fi
	else
		gap "$scope" "manifest" "Python sources with no pyproject.toml"
	fi

	hit="$(find_up "$dir" "" uv.lock || true)"
	if [ -n "$hit" ]; then
		if [ "$dir" = "." ]; then ok "$scope" "lockfile" "uv.lock"; fi
	elif hit="$(find_up "$dir" "" poetry.lock Pipfile.lock || true)" && [ -n "$hit" ]; then
		warn "$scope" "lockfile" "${hit}; uv is the preferred resolver"
	else
		gap "$scope" "lockfile" "no dependency lockfile, so builds are not reproducible"
	fi

	hit="$(find_up "$dir" "" ruff.toml .ruff.toml || true)"
	if [ -z "$hit" ]; then hit="$(find_up "$dir" 'tool\.ruff' pyproject.toml || true)"; fi
	if [ -n "$hit" ]; then
		if [ "$dir" = "." ]; then ok "$scope" "lint + format" "ruff configured"; fi
	else
		gap "$scope" "lint + format" "no [tool.ruff] section and no ruff.toml"
	fi

	hit="$(find_up "$dir" "" ty.toml .ty.toml || true)"
	if [ -z "$hit" ]; then hit="$(find_up "$dir" 'tool\.ty\b' pyproject.toml || true)"; fi
	if [ -n "$hit" ]; then
		if [ "$dir" = "." ]; then
			ok "$scope" "type checker" "ty configured"
			if contains 'respect-type-ignore-comments *= *false' "$hit"; then
				ok "$scope" "type suppressions" "respect-type-ignore-comments = false"
			else
				warn "$scope" "type suppressions" "a blanket \`# type: ignore\` still silences ty"
			fi
		fi
	elif hit="$(find_up "$dir" "" mypy.ini .mypy.ini pyrightconfig.json || true)" && [ -n "$hit" ]; then
		warn "$scope" "type checker" "${hit}; ty is the preferred checker"
	else
		gap "$scope" "type checker" "no ty.toml, no [tool.ty], and no other type-checker config"
	fi

	audit_inline_config "$scope" "$(rel "$dir" pyproject.toml)"

	# A workspace root delegates tests to its members; audit them, not it.
	if [ "$workspace_root" -eq 1 ]; then return 0; fi

	if [ "$dir" = "." ]; then tests_re='^tests?/'; else tests_re="^${dir}/tests?/"; fi
	if [ -f "$(abs "$dir" pytest.ini)" ] || contains 'tool\.pytest' "$(rel "$dir" pyproject.toml)"; then
		if [ "$dir" = "." ]; then ok "$scope" "tests" "pytest configured"; fi
	elif files_match "$tests_re"; then
		warn "$scope" "tests" "test directory with no pytest configuration"
	else
		warn "$scope" "tests" "no pytest configuration and no test directory"
	fi
}

# Lint and typecheck gates are repository-wide, so they are reported once.
audit_python_gates() {
	if ! gate_exists "." 'ruff'; then
		gap python "lint gate" "ruff runs in no hook, recipe, or pipeline job"
	fi
	if ! gate_exists "." 'ty check'; then
		warn python "typecheck gate" "no \`ty check\` in hooks, justfile, or pipeline"
	fi
}

audit_python() {
	local dir count=0 index=0 workspace_root
	count="$(project_dirs 'pyproject\.toml' | grep -c . || true)"

	if [ "$count" -eq 0 ]; then
		if files_match '\.py$'; then
			add_stack python
			audit_python_project "." 0
			audit_python_gates
		fi
		return 0
	fi

	while IFS= read -r dir; do
		[ -n "$dir" ] || continue
		index=$((index + 1))
		add_stack python
		workspace_root=0
		if [ "$dir" = "." ] && [ "$count" -gt 1 ]; then workspace_root=1; fi
		audit_python_project "$dir" "$workspace_root"
	done < <(project_dirs 'pyproject\.toml')
	audit_python_gates
}

# ── typescript and javascript ────────────────────────────────────────────────

audit_node_project() {
	local dir="$1" scope hit manifest
	scope="$(area typescript "$dir")"
	manifest="$(rel "$dir" package.json)"

	if [ -f "${ROOT}/${manifest}" ]; then
		if contains '"packageManager"' "$manifest"; then
			if [ "$dir" = "." ]; then ok "$scope" "toolchain pin" "packageManager field"; fi
		else
			warn "$scope" "toolchain pin" "no \"packageManager\" field in ${manifest}"
		fi
		if contains '"typecheck"' "$manifest" || gate_exists "$dir" 'tsc --noEmit|tsc -p|vue-tsc'; then
			if [ "$dir" = "." ]; then ok "$scope" "typecheck gate" "tsc gate present"; fi
		else
			warn "$scope" "typecheck gate" "no typecheck script and no tsc gate"
		fi
	else
		gap "$scope" "manifest" "JS or TS sources with no package.json"
	fi

	hit="$(find_up "$dir" "" pnpm-lock.yaml || true)"
	if [ -n "$hit" ]; then
		if [ "$dir" = "." ]; then ok "$scope" "lockfile" "pnpm-lock.yaml"; fi
	elif hit="$(find_up "$dir" "" package-lock.json yarn.lock bun.lock bun.lockb || true)" && [ -n "$hit" ]; then
		warn "$scope" "lockfile" "${hit}; pnpm is the preferred package manager"
	else
		gap "$scope" "lockfile" "no lockfile, so installs are not reproducible"
	fi

	hit="$(find_up "$dir" "" .oxlintrc.json .oxlintrc.jsonc oxlint.config.ts oxlint.config.mts || true)"
	if [ -n "$hit" ]; then
		if [ "$dir" = "." ]; then ok "$scope" "linter" "oxlint configured"; fi
	elif hit="$(find_up "$dir" "" eslint.config.js eslint.config.mjs eslint.config.ts .eslintrc .eslintrc.js .eslintrc.json .eslintrc.cjs || true)" && [ -n "$hit" ]; then
		warn "$scope" "linter" "${hit}; add oxlint for the fast pass, or record why type-aware eslint rules are required"
	elif hit="$(find_up "$dir" "" biome.json biome.jsonc || true)" && [ -n "$hit" ]; then
		warn "$scope" "linter" "${hit}; oxlint is the preferred linter"
	else
		gap "$scope" "linter" "no oxlint and no eslint configuration"
	fi

	if files_match "^${dir#./}.*\.(ts|tsx)\$"; then
		hit="$(find_up "$dir" "" tsconfig.json || true)"
		if [ -n "$hit" ]; then
			if contains '"strict" *: *true' "$hit"; then
				if [ "$dir" = "." ]; then ok "$scope" "strict mode" "\"strict\": true"; fi
			elif contains '"extends"' "$hit"; then
				warn "$scope" "strict mode" "${hit} inherits its base config; confirm strict is on"
			else
				gap "$scope" "strict mode" "${hit} does not enable strict"
			fi
		else
			gap "$scope" "tsconfig" "TypeScript sources with no tsconfig.json"
		fi
	fi

	hit="$(find_up "$dir" "" .prettierrc .prettierrc.json .prettierrc.yaml .prettierrc.js prettier.config.js prettier.config.mjs oxfmt.json biome.json || true)"
	if [ -n "$hit" ] || contains '"prettier"' "$manifest"; then
		if [ "$dir" = "." ]; then ok "$scope" "formatter" "formatter configured"; fi
	else
		warn "$scope" "formatter" "no formatter configuration"
	fi

	audit_inline_config "$scope" "$manifest"
}

audit_node() {
	local dir found=0
	while IFS= read -r dir; do
		[ -n "$dir" ] || continue
		found=1
		add_stack typescript
		audit_node_project "$dir"
	done < <(project_dirs 'package\.json')

	if [ "$found" -eq 0 ] && files_match '\.(ts|tsx|js|jsx|mjs|cjs|vue|svelte)$'; then
		add_stack typescript
		audit_node_project "."
	fi
}

# ── go ───────────────────────────────────────────────────────────────────────

audit_go() {
	local dir scope hit
	while IFS= read -r dir; do
		[ -n "$dir" ] || continue
		add_stack go
		scope="$(area go "$dir")"
		hit="$(find_up "$dir" "" .golangci.yml .golangci.yaml .golangci.toml .golangci.json || true)"
		if [ -n "$hit" ]; then
			if [ "$dir" = "." ]; then ok "$scope" "linter" "golangci-lint configured"; fi
		else
			gap "$scope" "linter" "no .golangci.yml"
		fi
		if gate_exists "$dir" 'golangci-lint'; then
			if [ "$dir" = "." ]; then ok "$scope" "lint gate" "golangci-lint runs in hooks, recipes, or CI"; fi
		else
			gap "$scope" "lint gate" "golangci-lint runs nowhere"
		fi
		if ! gate_exists "$dir" 'go vet|gofmt|goimports'; then
			warn "$scope" "format + vet" "no gofmt or go vet gate"
		fi
	done < <(project_dirs 'go\.mod')
}

# ── rust ─────────────────────────────────────────────────────────────────────

audit_rust() {
	local dir scope
	while IFS= read -r dir; do
		[ -n "$dir" ] || continue
		add_stack rust
		scope="$(area rust "$dir")"
		if [ "$dir" = "." ] && ! exists Cargo.lock; then
			warn "$scope" "lockfile" "no Cargo.lock committed"
		fi
		if gate_exists "$dir" 'clippy'; then
			if [ "$dir" = "." ]; then ok "$scope" "linter" "clippy gate present"; fi
		else
			gap "$scope" "linter" "cargo clippy runs in no hook, recipe, or pipeline job"
		fi
		if gate_exists "$dir" 'cargo fmt|rustfmt'; then
			if [ "$dir" = "." ]; then ok "$scope" "formatter" "rustfmt gate present"; fi
		else
			gap "$scope" "formatter" "cargo fmt --check runs nowhere"
		fi
		if [ "$dir" = "." ] && ! any_exists rust-toolchain.toml rust-toolchain; then
			warn "$scope" "toolchain pin" "no rust-toolchain.toml, so CI and local builds can diverge"
		fi
	done < <(project_dirs 'Cargo\.toml')
}

# ── shell, containers, and workflows ─────────────────────────────────────────

audit_cross_cutting() {
	if files_match '\.(sh|bash)$'; then
		add_stack shell
		if gate_exists "." 'shellcheck'; then
			ok shell "linter" "shellcheck gate present"
		else
			gap shell "linter" "shell scripts with no shellcheck gate"
		fi
		if ! gate_exists "." 'shfmt'; then
			warn shell "formatter" "no shfmt gate"
		fi
	fi

	if files_match '(^|/)(Dockerfile|Containerfile)'; then
		add_stack containers
		if gate_exists "." 'hadolint'; then
			ok containers "linter" "hadolint gate present"
		else
			warn containers "linter" "container files with no hadolint gate"
		fi
	fi

	if [ -n "$(workflow_files)" ] && ! gate_exists "." 'actionlint'; then
		warn "github actions" "workflow lint" "no actionlint gate for .github/workflows"
	fi
}

# ── just recipes ─────────────────────────────────────────────────────────────
#
# Recipe names are the contract every caller shares, so they are audited as
# their own layer. Runs last, because the conditional recipes depend on which
# stacks and artifacts the earlier passes detected.

audit_recipes() {
	local just names name body stack code=0 artifact=0 service=0
	local before=${#STATUSES[@]}

	just="$(justfile_path || true)"
	# audit_universal already reported the missing justfile.
	[ -n "$just" ] || return 0

	names="$(recipe_list "$just")"
	if [ -z "$names" ]; then
		gap recipes "recipe set" "${just} exposes no recipes, or just cannot parse it"
		return 0
	fi

	# Required in every repository, including a docs-only one.
	for name in ci lint fix test setup hooks; do
		if ! has_recipe "$names" "$name"; then
			gap recipes "\`just ${name}\`" "${just} has no \`${name}\` recipe"
		fi
	done

	for stack in ${STACKS[@]+"${STACKS[@]}"}; do
		case "$stack" in
		python | typescript | go | rust) code=1 ;;
		esac
		case "$stack" in
		go | rust) artifact=1 ;;
		containers) artifact=1 service=1 ;;
		esac
	done
	if exists pyproject.toml && contains 'build-backend' pyproject.toml; then artifact=1; fi
	if contains '"build" *:' package.json; then artifact=1; fi
	if contains '"(dev|start)" *:' package.json; then service=1; fi
	if contains 'fastapi|uvicorn|gunicorn|django|flask' pyproject.toml; then service=1; fi

	# Conditional on what the repository actually has.
	if [ "$code" -eq 1 ]; then
		for name in fmt fmt-check; do
			if ! has_recipe "$names" "$name"; then
				warn recipes "\`just ${name}\`" "a formatter-bearing stack with no \`${name}\` recipe"
			fi
		done
	fi
	for stack in ${STACKS[@]+"${STACKS[@]}"}; do
		case "$stack" in
		python | typescript)
			if ! has_recipe "$names" typecheck; then
				warn recipes "\`just typecheck\`" "${stack} needs a type-check recipe separate from the compiler"
			fi
			break
			;;
		esac
	done
	if [ "$artifact" -eq 1 ] && ! has_recipe "$names" build; then
		warn recipes "\`just build\`" "the repository ships an artifact but has no \`build\` recipe"
	fi
	if [ "$service" -eq 1 ]; then
		if ! has_recipe "$names" start; then
			warn recipes "\`just start\`" "a runnable service with no \`start\` recipe for the production command"
		fi
		if ! has_recipe "$names" dev; then
			warn recipes "\`just dev\`" "a runnable service with no \`dev\` recipe for the local loop"
		fi
	fi

	# A gate that repairs its own input cannot fail. Comments are stripped so a
	# note about --fix does not read as a --fix invocation.
	body="$(recipe_body "$just" lint | grep -v '^[[:space:]]*#' || true)"
	if [ -n "$body" ] && printf '%s\n' "$body" | grep -Eq -- '(--fix|--write|--apply|--allow-dirty)'; then
		gap recipes "\`just lint\`" "the lint recipe rewrites files; move the fixing flags to \`fix\`"
	fi

	# ci composes the gates, and fix, dev, and start are not gates. Only the
	# recipe's own line carries its dependencies.
	body="$(recipe_body "$just" ci | grep -E '^ci[ :]' || true)"
	if [ -n "$body" ] && printf '%s\n' "$body" | grep -Eq -- '(^|[ (])(fix|dev|start)([ )]|$)'; then
		gap recipes "\`just ci\`" "ci depends on fix, dev, or start; a gate must not write files or block"
	fi

	if [ "${#STATUSES[@]}" -eq "$before" ]; then
		ok recipes "recipe set" "$(printf '%s\n' "$names" | tr '\n' ' ' | sed 's/  *$//')"
	fi
}

# ── reporting ────────────────────────────────────────────────────────────────

json_escape() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }

report_json() {
	local index total=${#STATUSES[@]} first=1
	printf '{\n'
	printf '  "root": "%s",\n' "$(json_escape "$ROOT")"
	printf '  "stacks": ['
	for index in ${STACKS[@]+"${!STACKS[@]}"}; do
		[ "$first" -eq 1 ] || printf ', '
		printf '"%s"' "$(json_escape "${STACKS[$index]}")"
		first=0
	done
	printf '],\n'
	printf '  "summary": {"ok": %d, "gap": %d, "warn": %d},\n' "$OK_COUNT" "$GAP_COUNT" "$WARN_COUNT"
	printf '  "findings": [\n'
	for ((index = 0; index < total; index++)); do
		printf '    {"status": "%s", "area": "%s", "check": "%s", "detail": "%s"}' \
			"${STATUSES[$index]}" \
			"$(json_escape "${AREAS[$index]}")" \
			"$(json_escape "${CHECKS[$index]}")" \
			"$(json_escape "${DETAILS[$index]}")"
		if [ "$index" -lt $((total - 1)) ]; then printf ','; fi
		printf '\n'
	done
	printf '  ]\n}\n'
}

report_text() {
	local index total=${#STATUSES[@]} label seen="" group
	printf 'Quality baseline audit — %s\n' "$ROOT"
	if [ ${#STACKS[@]} -gt 0 ]; then
		printf 'Stacks detected: %s\n\n' "$(
			IFS=,
			printf '%s' "${STACKS[*]}" | sed 's/,/, /g'
		)"
	else
		printf 'Stacks detected: none\n\n'
	fi
	# Two passes keep every finding of one area together, in first-seen order.
	for ((group = 0; group < total; group++)); do
		case "${seen}" in
		*"<${AREAS[$group]}>"*) continue ;;
		esac
		seen="${seen}<${AREAS[$group]}>"
		printf '%s\n' "${AREAS[$group]}"
		for ((index = group; index < total; index++)); do
			[ "${AREAS[$index]}" = "${AREAS[$group]}" ] || continue
			case "${STATUSES[$index]}" in
			ok) label="[ok]  " ;;
			gap) label="[gap] " ;;
			*) label="[warn]" ;;
			esac
			printf '  %s %-18s %s\n' "$label" "${CHECKS[$index]}" "${DETAILS[$index]}"
		done
	done
	printf '\n%d ok, %d gaps, %d warnings\n' "$OK_COUNT" "$GAP_COUNT" "$WARN_COUNT"
}

main() {
	audit_universal
	audit_python
	audit_node
	audit_go
	audit_rust
	audit_cross_cutting
	audit_recipes

	OK_COUNT=0
	GAP_COUNT=0
	WARN_COUNT=0
	local status
	for status in ${STATUSES[@]+"${STATUSES[@]}"}; do
		case "$status" in
		ok) OK_COUNT=$((OK_COUNT + 1)) ;;
		gap) GAP_COUNT=$((GAP_COUNT + 1)) ;;
		*) WARN_COUNT=$((WARN_COUNT + 1)) ;;
		esac
	done

	if [ "$JSON" -eq 1 ]; then report_json; else report_text; fi

	if [ "$GAP_COUNT" -gt 0 ]; then return 1; fi
	if [ "$STRICT" -eq 1 ] && [ "$WARN_COUNT" -gt 0 ]; then return 1; fi
	return 0
}

main
