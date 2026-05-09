#!/usr/bin/env python3
"""
Assertions for validating .gitlab-ci.yml files.

Usage:
    python3 assertions.py <file.yml>

Exits 0 if all checks pass (warnings are OK).
Exits 1 if any check fails.
"""

import sys
import yaml
import re


def check_valid_yaml(data, raw, path):
    """Check 1: File parses as valid YAML."""
    if data is None:
        print(f"[FAIL] Valid YAML — file is empty or null: {path}")
        return False
    print(f"[PASS] Valid YAML")
    return True


def check_stages(data):
    """Check 2: Top-level 'stages' key exists and is a non-empty list."""
    stages = data.get("stages")
    if stages is None:
        print("[FAIL] Has stages — 'stages' key not found at top level")
        return False
    if not isinstance(stages, list):
        print(f"[FAIL] Has stages — 'stages' is not a list (got {type(stages).__name__})")
        return False
    if len(stages) == 0:
        print("[FAIL] Has stages — 'stages' list is empty")
        return False
    print(f"[PASS] Has stages")
    return True


def _is_job(key, value):
    """Determine if a top-level key looks like a job definition."""
    if key.startswith("."):
        return False  # Anchors/extensions
    if not isinstance(value, dict):
        return False
    # Must have 'script' or 'extends' or be a template override (just 'stage')
    if "script" in value:
        return True
    if "extends" in value:
        return True
    # Allow jobs that only specify 'stage' (template overrides like secret_detection)
    if "stage" in value:
        return True
    return False


def check_jobs(data):
    """Check 3: At least one top-level key is a job with script/extends/stage."""
    for key, value in data.items():
        if _is_job(key, value):
            print(f"[PASS] Has at least one job with script")
            return True
    print("[FAIL] Has at least one job with script — no job definitions found")
    return False


def check_deprecated_keywords(raw):
    """Check 4: No lines matching 'only:' or 'except:' at line start (with optional whitespace)."""
    lines = raw.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r"^(only|except):", stripped):
            print(f"[FAIL] No deprecated keywords — found '{stripped}' at line {i}")
            return False
    print(f"[PASS] No deprecated keywords (only/except)")
    return True


DEPRECATED_GLOBAL_KEYS = {"image", "cache", "before_script", "after_script"}


def check_global_deprecated(data):
    """Check 5: No deprecated keys at top level (should be under 'default:')."""
    for key in DEPRECATED_GLOBAL_KEYS:
        if key in data:
            print(f"[FAIL] No global deprecated keys — found top-level '{key}:' (should be under 'default:')")
            return False
    print(f"[PASS] No global deprecated keys")
    return True


def check_artifacts_expire_in(data):
    """Check 6: Every job with 'artifacts' also has 'artifacts.expire_in'."""
    ok = True
    for key, value in data.items():
        if not _is_job(key, value):
            continue
        artifacts = value.get("artifacts")
        if artifacts is None:
            continue
        if not isinstance(artifacts, dict):
            continue
        if "expire_in" not in artifacts:
            print(f"[FAIL] Artifacts have expire_in — job '{key}' has artifacts but no expire_in")
            ok = False
    if ok:
        print(f"[PASS] All artifacts have expire_in")
    return ok


def check_cache_key_files(data):
    """Check 7: For jobs with cache, check cache.key.files exists (warn if not)."""
    all_ok = True
    for key, value in data.items():
        if not _is_job(key, value):
            continue
        cache = value.get("cache")
        if cache is None:
            continue
        if not isinstance(cache, dict):
            continue
        cache_key = cache.get("key")
        if cache_key is None:
            print(f"[WARN] Cache key.files not used in: {key} (no key defined)")
            all_ok = False
            continue
        if isinstance(cache_key, dict):
            if "files" not in cache_key:
                print(f"[WARN] Cache key.files not used in: {key} (consider lockfile-based invalidation)")
                all_ok = False
        elif isinstance(cache_key, str):
            # Simple string key — not using key.files
            print(f"[WARN] Cache key.files not used in: {key} (consider lockfile-based invalidation)")
            all_ok = False
    if all_ok:
        print(f"[PASS] Cache key.files used where applicable")
    return True  # Warnings don't fail


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 assertions.py <file.yml>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    try:
        with open(path, "r") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"[FAIL] File not found: {path}")
        sys.exit(1)
    except IOError as e:
        print(f"[FAIL] Could not read file: {e}")
        sys.exit(1)

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        print(f"[FAIL] Valid YAML — parse error: {e}")
        sys.exit(1)

    results = [
        check_valid_yaml(data, raw, path),
        check_stages(data),
        check_jobs(data),
        check_deprecated_keywords(raw),
        check_global_deprecated(data),
        check_artifacts_expire_in(data),
    ]

    # Check 7 is warn-only, always passes
    check_cache_key_files(data)

    if all(results):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
