from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_skills import discover_skill_dirs, validate, validate_skill_dir


VALID_BODY = """# Example Skill

Use this procedure when needed.

## Example
Input and output example.

## Failure handling
Handle edge cases explicitly.
"""


def write_skill(root: Path, name: str, frontmatter: str, body: str = VALID_BODY) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")
    return skill_dir


class ValidateSkillsTest(unittest.TestCase):
    def test_accepts_minimal_valid_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = write_skill(
                root,
                "valid-skill",
                "name: valid-skill\ndescription: Use this skill when validating examples.\n",
            )

            result = validate_skill_dir(skill_dir)

            self.assertEqual([], result.errors)

    def test_accepts_folded_description_optional_fields_and_conventional_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = write_skill(
                root,
                "rich-skill",
                """name: rich-skill
description: >
  Use this skill when the user needs a richer example with folded YAML.
license: MIT
compatibility: Requires Python 3.11 or newer.
allowed-tools: Bash(git:*) Read
metadata:
  owner: skills-team
  version: "1.0"
""",
            )
            (skill_dir / "scripts").mkdir()
            (skill_dir / "references").mkdir()
            (skill_dir / "assets").mkdir()

            result = validate_skill_dir(skill_dir)

            self.assertEqual([], result.errors)

    def test_discovers_only_top_level_skill_directories_with_skill_md(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = write_skill(root, "first", "name: first\ndescription: Use this skill when testing discovery.\n")
            write_skill(root / ".hidden", "ignored", "name: ignored\ndescription: Use this skill when hidden.\n")
            (root / "not-a-skill").mkdir()

            self.assertEqual([first], discover_skill_dirs(root))

    def test_reports_missing_skill_md(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "missing"
            skill_dir.mkdir()

            result = validate_skill_dir(skill_dir)

            self.assertIn("missing required SKILL.md", result.errors[0].message)

    def test_reports_missing_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "no-frontmatter"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Missing\n", encoding="utf-8")

            result = validate_skill_dir(skill_dir)

            self.assertIn("missing YAML frontmatter", result.errors[0].message)

    def test_reports_invalid_yaml_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = write_skill(
                root,
                "invalid-yaml",
                "name: invalid-yaml\n  description: Use this skill when indentation is invalid.\n",
            )

            result = validate_skill_dir(skill_dir)

            self.assertTrue(any("unexpected indented line" in error.message for error in result.errors))

    def test_reports_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = write_skill(Path(temp_dir), "missing-fields", "license: MIT\n")

            result = validate_skill_dir(skill_dir)

            messages = "\n".join(error.message for error in result.errors)
            self.assertIn("'name' is required", messages)
            self.assertIn("'description' is required", messages)

    def test_reports_invalid_name_forms(self) -> None:
        invalid_names = ["Upper", "-leading", "trailing-", "double--hyphen", "bad_name"]
        for invalid_name in invalid_names:
            with self.subTest(invalid_name=invalid_name), tempfile.TemporaryDirectory() as temp_dir:
                skill_dir = write_skill(
                    Path(temp_dir),
                    "skill-dir",
                    f"name: {invalid_name}\ndescription: Use this skill when testing invalid names.\n",
                )

                result = validate_skill_dir(skill_dir)

                self.assertTrue(any("single hyphens" in error.message for error in result.errors))

    def test_reports_name_too_long(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            long_name = "a" * 65
            skill_dir = write_skill(
                Path(temp_dir),
                "long-name",
                f"name: {long_name}\ndescription: Use this skill when testing name length.\n",
            )

            result = validate_skill_dir(skill_dir)

            self.assertTrue(any("1-64" in error.message for error in result.errors))

    def test_reports_name_directory_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = write_skill(
                Path(temp_dir),
                "directory-name",
                "name: different-name\ndescription: Use this skill when testing mismatches.\n",
            )

            result = validate_skill_dir(skill_dir)

            self.assertTrue(any("must match directory name" in error.message for error in result.errors))

    def test_reports_empty_too_long_and_non_triggering_descriptions(self) -> None:
        cases = [
            ("empty-description", ""),
            ("long-description", "Use this skill when " + ("x" * 1024)),
            ("non-triggering-description", "Generate examples without saying when to use it."),
        ]
        for directory, description in cases:
            with self.subTest(directory=directory), tempfile.TemporaryDirectory() as temp_dir:
                skill_dir = write_skill(
                    Path(temp_dir),
                    directory,
                    f"name: {directory}\ndescription: {description}\n",
                )

                result = validate_skill_dir(skill_dir)

                self.assertTrue(result.errors)

    def test_reports_empty_markdown_body(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = write_skill(
                Path(temp_dir),
                "empty-body",
                "name: empty-body\ndescription: Use this skill when testing empty bodies.\n",
                "",
            )

            result = validate_skill_dir(skill_dir)

            self.assertTrue(any("Markdown content" in error.message for error in result.errors))

    def test_accepts_long_string_optional_fields_without_non_spec_length_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = write_skill(
                Path(temp_dir),
                "long-options",
                "name: long-options\n"
                "description: Use this skill when testing long optional strings.\n"
                f"license: {'L' * 300}\n"
                f"allowed-tools: {'Bash(git:*) ' * 100}\n",
            )

            result = validate_skill_dir(skill_dir)

            self.assertEqual([], result.errors)

    def test_reports_invalid_optional_field_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = write_skill(
                Path(temp_dir),
                "bad-options",
                """name: bad-options
description: Use this skill when testing bad optional fields.
compatibility: """
                + ("x" * 501)
                + """
metadata:
  nested:
allowed-tools:
""",
            )

            result = validate_skill_dir(skill_dir)

            messages = "\n".join(error.message for error in result.errors)
            self.assertIn("nested value", messages)

    def test_accepts_extra_files_and_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = write_skill(
                Path(temp_dir),
                "extra-files",
                "name: extra-files\ndescription: Use this skill when testing extra files.\n",
            )
            (skill_dir / "custom").mkdir()
            (skill_dir / "custom" / "data.txt").write_text("ok", encoding="utf-8")

            result = validate_skill_dir(skill_dir)

            self.assertEqual([], result.errors)

    def test_validates_relative_markdown_links_stay_inside_skill_root_and_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = write_skill(
                Path(temp_dir),
                "links",
                "name: links\ndescription: Use this skill when validating relative links.\n",
                """# Links

[Missing](references/missing.md)
[Outside](../outside.md)
[External](https://example.com)

## Example
Example output.

## Failure handling
Edge cases.
""",
            )

            result = validate_skill_dir(skill_dir)
            messages = "\n".join(error.message for error in result.errors)
            self.assertIn("target does not exist", messages)
            self.assertIn("must not leave", messages)

    def test_repository_skills_pass_hard_spec_validation(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        result = validate(repo_root)

        self.assertEqual([], result.errors)


if __name__ == "__main__":
    unittest.main()
