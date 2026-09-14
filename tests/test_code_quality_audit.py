"""Tests for the code-quality audit script."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT = REPO_ROOT / "code-quality" / "scripts" / "audit.sh"

PREK = """
[[repos]]
repo = "builtin"
hooks = [{ id = "trailing-whitespace" }, { id = "check-yaml" }]

[[repos]]
repo = "https://github.com/astral-sh/ruff-pre-commit"
rev = "v0.16.7"
hooks = [{ id = "ruff-check" }, { id = "ruff-format" }]

[[repos]]
repo = "https://github.com/gitleaks/gitleaks"
rev = "v8.30.1"
hooks = [{ id = "gitleaks" }]
"""

JUSTFILE = """
ci: lint typecheck test

lint:
    uv run ruff check .

typecheck:
    uv run ty check src

test:
    uv run pytest
"""

PIPELINE = """
stages: [quality]

quality:hooks:
  stage: quality
  script:
    - uvx prek run --all-files
"""

PYPROJECT = """
[project]
name = "example"

[tool.ruff]
target-version = "py314"

[tool.pytest.ini_options]
testpaths = ["tests"]
"""

TY = """
[analysis]
respect-type-ignore-comments = false
"""


def run_audit(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(AUDIT), *args, str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


def write(root: Path, relative: str, content: str = "") -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


class AuditScriptTests(unittest.TestCase):
    def test_script_is_executable_and_shellcheck_clean_syntax(self) -> None:
        self.assertTrue(AUDIT.is_file())
        syntax = subprocess.run(
            ["bash", "-n", str(AUDIT)], capture_output=True, text=True, check=False
        )
        self.assertEqual(syntax.returncode, 0, syntax.stderr)

    def test_empty_repository_reports_baseline_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_audit(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            for expected in ("hook runner", "task runner", "ci recipe", "pipeline"):
                self.assertIn(expected, result.stdout)

    def test_complete_python_baseline_has_no_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "prek.toml", PREK)
            write(root, "justfile", JUSTFILE)
            write(root, ".gitlab-ci.yml", PIPELINE)
            write(root, "pyproject.toml", PYPROJECT)
            write(root, "ty.toml", TY)
            write(root, "uv.lock")
            write(root, ".editorconfig")
            write(root, "src/app.py", "print('hi')\n")
            write(root, "tests/test_app.py", "def test_ok():\n    assert True\n")

            result = run_audit(root)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("0 gaps", result.stdout)

    def test_missing_type_checker_is_a_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "prek.toml", PREK)
            write(root, "justfile", JUSTFILE)
            write(root, ".gitlab-ci.yml", PIPELINE)
            write(root, "pyproject.toml", PYPROJECT)
            write(root, "uv.lock")
            write(root, "src/app.py", "print('hi')\n")

            result = run_audit(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("type checker", result.stdout)

    def test_oversized_inline_tool_config_is_a_gap(self) -> None:
        rules = "\n".join(f'# keep rule {index}\n"RULE{index}",' for index in range(20))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "prek.toml", PREK)
            write(root, "justfile", JUSTFILE)
            write(root, ".gitlab-ci.yml", PIPELINE)
            write(root, "ty.toml", TY)
            write(root, "uv.lock")
            write(root, "src/app.py", "print('hi')\n")
            write(
                root,
                "pyproject.toml",
                f'[project]\nname = "example"\n\n[tool.ruff]\ntarget-version = "py314"\n\n'
                f"[tool.ruff.lint]\nselect = [\n{rules}\n]\n",
            )

            result = run_audit(root, "--json")
            payload = json.loads(result.stdout)
            sizes = [
                finding
                for finding in payload["findings"]
                if finding["check"] == "config size"
            ]
            self.assertEqual(len(sizes), 1, payload["findings"])
            self.assertEqual(sizes[0]["status"], "gap")
            self.assertIn("ruff.toml", sizes[0]["detail"])

    def test_oversized_package_json_scripts_is_a_gap(self) -> None:
        scripts = ",\n".join(
            f'    "task{index}": "echo {index}"' for index in range(45)
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root,
                "package.json",
                '{\n  "name": "example",\n  "scripts": {\n' + scripts + "\n  }\n}\n",
            )
            write(root, "src/index.ts", "export const answer = 42;\n")

            result = run_audit(root, "--json")
            payload = json.loads(result.stdout)
            details = [
                finding["detail"]
                for finding in payload["findings"]
                if finding["check"] == "config size"
            ]
            self.assertTrue(
                any("just recipes" in detail for detail in details), details
            )

    def test_small_inline_tool_config_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "pyproject.toml", PYPROJECT)
            write(root, "src/app.py", "print('hi')\n")

            result = run_audit(root, "--json")
            payload = json.loads(result.stdout)
            checks = {finding["check"] for finding in payload["findings"]}
            self.assertNotIn("config size", checks)

    def test_json_output_reports_stacks_and_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "package.json", '{\n  "name": "example"\n}\n')
            write(root, "src/index.ts", "export const answer = 42;\n")

            result = run_audit(root, "--json")
            payload = json.loads(result.stdout)
            self.assertIn("typescript", payload["stacks"])
            self.assertGreater(payload["summary"]["gap"], 0)
            statuses = {finding["status"] for finding in payload["findings"]}
            self.assertTrue(statuses <= {"ok", "gap", "warn"})
            checks = {finding["check"] for finding in payload["findings"]}
            self.assertIn("linter", checks)
            self.assertIn("tsconfig", checks)

    def test_strict_mode_fails_on_warnings_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "prek.toml", PREK)
            write(root, "justfile", JUSTFILE)
            write(root, ".gitlab-ci.yml", PIPELINE)
            write(root, "pyproject.toml", PYPROJECT)
            write(root, "ty.toml", TY)
            write(root, "uv.lock")
            write(root, ".editorconfig")
            write(root, "src/app.py", "print('hi')\n")
            write(root, "tests/test_app.py", "def test_ok():\n    assert True\n")
            write(root, "README.md", "# example\n")

            self.assertEqual(run_audit(root).returncode, 0)
            self.assertEqual(run_audit(root, "--strict").returncode, 1)

    def test_usage_error_on_missing_directory(self) -> None:
        result = run_audit(Path("/nonexistent-path-for-audit-test"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a directory", result.stderr)


if __name__ == "__main__":
    unittest.main()
