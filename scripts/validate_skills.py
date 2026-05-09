#!/usr/bin/env python3
"""Validate Agent Skills packages against https://agentskills.io/specification.md.

The repository intentionally keeps skills as static directories, so this validator is
self-contained and dependency-free. It enforces the normative parts of the public
specification and reports best-practice guidance as warnings.
"""

from __future__ import annotations

import argparse
import dataclasses
import re
import sys
from pathlib import Path
from typing import Iterable, Sequence


NAME_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SKILL_BODY_RECOMMENDED_MAX_LINES = 500


@dataclasses.dataclass(frozen=True)
class Finding:
    path: Path
    message: str

    def format(self) -> str:
        return f"{self.path}: {self.message}"


@dataclasses.dataclass
class ValidationResult:
    errors: list[Finding]
    warnings: list[Finding]

    @property
    def ok(self) -> bool:
        return not self.errors


class FrontmatterError(ValueError):
    """Raised when a SKILL.md frontmatter block cannot be parsed."""


def discover_skill_dirs(root: Path) -> list[Path]:
    """Return top-level skill directories, matching the repository packaging jobs."""
    return sorted(
        child
        for child in root.iterdir()
        if child.is_dir() and not child.name.startswith(".") and (child / "SKILL.md").is_file()
    )


def parse_frontmatter(text: str, source: Path) -> tuple[dict[str, object], str]:
    """Parse the restricted YAML frontmatter used by Agent Skills.

    The spec requires YAML frontmatter, but this repository only needs the simple
    mapping forms used by SKILL.md files: scalar values, folded block scalars, and
    one-level mappings for `metadata`. The parser rejects lists/nesting that would
    make spec validation ambiguous without a YAML dependency.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("missing YAML frontmatter opening delimiter")

    closing_index = next((index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
    if closing_index is None:
        raise FrontmatterError("missing YAML frontmatter closing delimiter")

    frontmatter_lines = lines[1:closing_index]
    body = "\n".join(lines[closing_index + 1 :]).lstrip("\n")
    data: dict[str, object] = {}
    index = 0

    while index < len(frontmatter_lines):
        raw_line = frontmatter_lines[index]
        index += 1

        if not raw_line.strip():
            continue
        if raw_line.startswith((" ", "\t")):
            raise FrontmatterError(f"unexpected indented line: {raw_line!r}")
        if ":" not in raw_line:
            raise FrontmatterError(f"expected key/value pair: {raw_line!r}")

        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            raise FrontmatterError("frontmatter key cannot be empty")
        if key in data:
            raise FrontmatterError(f"duplicate frontmatter key: {key}")

        if raw_value in {">", "|-", "|"} or raw_value.startswith(">"):
            folded_lines: list[str] = []
            while index < len(frontmatter_lines):
                continuation = frontmatter_lines[index]
                if continuation and not continuation.startswith((" ", "\t")):
                    break
                folded_lines.append(continuation.strip())
                index += 1
            data[key] = " ".join(part for part in folded_lines if part).strip()
            continue

        if raw_value == "":
            nested: dict[str, str] = {}
            while index < len(frontmatter_lines):
                continuation = frontmatter_lines[index]
                if not continuation.strip():
                    index += 1
                    continue
                if not continuation.startswith((" ", "\t")):
                    break
                nested_key, nested_value = _parse_nested_mapping_line(continuation, source)
                if nested_key in nested:
                    raise FrontmatterError(f"duplicate metadata key: {nested_key}")
                nested[nested_key] = nested_value
                index += 1
            data[key] = nested
            continue

        data[key] = _unquote(raw_value)

    return data, body


def _parse_nested_mapping_line(line: str, source: Path) -> tuple[str, str]:
    stripped = line.strip()
    if ":" not in stripped:
        raise FrontmatterError(f"expected nested key/value pair in {source}: {stripped!r}")
    key, raw_value = stripped.split(":", 1)
    key = key.strip()
    raw_value = raw_value.strip()
    if not key:
        raise FrontmatterError("nested frontmatter key cannot be empty")
    if raw_value == "":
        raise FrontmatterError(f"nested value for {key!r} must be a string")
    return key, _unquote(raw_value)


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def validate_skill_dir(skill_dir: Path) -> ValidationResult:
    skill_file = skill_dir / "SKILL.md"
    errors: list[Finding] = []
    warnings: list[Finding] = []

    if not skill_file.is_file():
        return ValidationResult([Finding(skill_dir, "missing required SKILL.md")], warnings)

    try:
        text = skill_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return ValidationResult([Finding(skill_file, f"must be UTF-8 text: {exc}")], warnings)

    try:
        frontmatter, body = parse_frontmatter(text, skill_file)
    except FrontmatterError as exc:
        return ValidationResult([Finding(skill_file, str(exc))], warnings)

    _validate_required_frontmatter(skill_dir, skill_file, frontmatter, errors)
    _validate_optional_frontmatter(skill_file, frontmatter, errors)
    _validate_markdown_body(skill_file, body, errors, warnings)
    _validate_markdown_links(skill_dir, skill_file, body, errors)
    _validate_conventional_directories(skill_dir, warnings)
    return ValidationResult(errors, warnings)


def _validate_required_frontmatter(
    skill_dir: Path,
    skill_file: Path,
    frontmatter: dict[str, object],
    errors: list[Finding],
) -> None:
    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not isinstance(name, str):
        errors.append(Finding(skill_file, "frontmatter field 'name' is required and must be a string"))
    else:
        if not (1 <= len(name) <= 64):
            errors.append(Finding(skill_file, "frontmatter field 'name' must be 1-64 characters"))
        if not NAME_PATTERN.fullmatch(name) or "--" in name:
            errors.append(
                Finding(
                    skill_file,
                    "frontmatter field 'name' must use lowercase ASCII letters, numbers, and single hyphens; "
                    "it cannot start/end with a hyphen",
                )
            )
        if name != skill_dir.name:
            errors.append(Finding(skill_file, f"frontmatter field 'name' must match directory name '{skill_dir.name}'"))

    if not isinstance(description, str):
        errors.append(Finding(skill_file, "frontmatter field 'description' is required and must be a string"))
    else:
        normalized = description.strip()
        if not (1 <= len(normalized) <= 1024):
            errors.append(Finding(skill_file, "frontmatter field 'description' must be 1-1024 characters"))
        if "use this skill" not in normalized.lower() and "use when" not in normalized.lower():
            errors.append(Finding(skill_file, "description must describe when to use the skill"))


def _validate_optional_frontmatter(skill_file: Path, frontmatter: dict[str, object], errors: list[Finding]) -> None:
    license_value = frontmatter.get("license")
    if license_value is not None and not _is_non_empty_string(license_value):
        errors.append(Finding(skill_file, "optional field 'license' must be a non-empty string when present"))

    compatibility = frontmatter.get("compatibility")
    if compatibility is not None and not _is_bounded_string(compatibility, minimum=1, maximum=500):
        errors.append(Finding(skill_file, "optional field 'compatibility' must be a 1-500 character string"))

    metadata = frontmatter.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in metadata.items()):
            errors.append(Finding(skill_file, "optional field 'metadata' must be a string-to-string mapping"))

    allowed_tools = frontmatter.get("allowed-tools")
    if allowed_tools is not None and not _is_non_empty_string(allowed_tools):
        errors.append(Finding(skill_file, "optional field 'allowed-tools' must be a non-empty space-separated string"))


def _is_bounded_string(value: object, *, minimum: int, maximum: int) -> bool:
    return isinstance(value, str) and minimum <= len(value.strip()) <= maximum


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_markdown_body(skill_file: Path, body: str, errors: list[Finding], warnings: list[Finding]) -> None:
    if not body.strip():
        errors.append(Finding(skill_file, "SKILL.md must contain Markdown content after frontmatter"))
        return
    if len(body.splitlines()) > SKILL_BODY_RECOMMENDED_MAX_LINES:
        warnings.append(Finding(skill_file, "body should stay under 500 lines; move long material to references/ or assets/"))
    lowered = body.lower()
    if "example" not in lowered:
        warnings.append(Finding(skill_file, "body should include input/output or usage examples where practical"))
    if "edge" not in lowered and "mistake" not in lowered and "fail" not in lowered:
        warnings.append(Finding(skill_file, "body should mention common edge cases, mistakes, or failure handling"))


def _validate_markdown_links(skill_dir: Path, skill_file: Path, body: str, errors: list[Finding]) -> None:
    for raw_target in MARKDOWN_LINK_PATTERN.findall(body):
        target = raw_target.split("#", 1)[0].strip()
        if not target or _is_external_or_absolute_target(target):
            continue
        if target.startswith("../"):
            errors.append(Finding(skill_file, f"relative link must not leave the skill root: {raw_target}"))
            continue
        if not (skill_dir / target).exists():
            errors.append(Finding(skill_file, f"relative link target does not exist: {raw_target}"))


def _is_external_or_absolute_target(target: str) -> bool:
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)) or target.startswith("/")


def _validate_conventional_directories(skill_dir: Path, warnings: list[Finding]) -> None:
    for directory_name in ("scripts", "references", "assets"):
        directory = skill_dir / directory_name
        if directory.exists() and not directory.is_dir():
            warnings.append(Finding(directory, f"'{directory_name}' is conventionally a directory"))

    root_scripts = [path for path in skill_dir.iterdir() if path.is_file() and path.suffix in {".sh", ".py", ".js"}]
    if root_scripts and not (skill_dir / "scripts").exists():
        warnings.append(Finding(skill_dir, "scripts are conventionally kept in scripts/ for progressive disclosure"))


def validate(root: Path, skill_dirs: Sequence[Path] | None = None) -> ValidationResult:
    selected_skill_dirs = list(skill_dirs) if skill_dirs is not None else discover_skill_dirs(root)
    errors: list[Finding] = []
    warnings: list[Finding] = []

    if not selected_skill_dirs:
        errors.append(Finding(root, "no skill directories found"))
        return ValidationResult(errors, warnings)

    for skill_dir in selected_skill_dirs:
        result = validate_skill_dir(skill_dir)
        errors.extend(result.errors)
        warnings.extend(result.warnings)

    return ValidationResult(errors, warnings)


def _print_findings(label: str, findings: Iterable[Finding]) -> None:
    findings = list(findings)
    if not findings:
        return
    print(f"{label}:", file=sys.stderr)
    for finding in findings:
        print(f"  - {finding.format()}", file=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills packages against the public specification.")
    parser.add_argument("root", nargs="?", default=".", type=Path, help="repository root or a single skill directory")
    parser.add_argument("--strict", action="store_true", help="treat best-practice warnings as failures")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    skill_dirs = [root] if (root / "SKILL.md").is_file() else None
    result = validate(root, skill_dirs)

    _print_findings("Errors", result.errors)
    _print_findings("Warnings", result.warnings)

    if result.errors or (args.strict and result.warnings):
        return 1

    skill_count = len(skill_dirs) if skill_dirs is not None else len(discover_skill_dirs(root))
    print(f"Validated {skill_count} skill(s) successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
