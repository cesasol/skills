set shell := ["bash", "-uc"]

# Show available recipes
default:
    just --list

# Run the full CI verification suite
ci: lint hooks test package-check

# Run all linters
lint: lint-md

# Lint Markdown with rumdl
lint-md:
    uvx rumdl check .

# Validate all Agent Skills packages
validate-skills:
    python3 scripts/validate_skills.py . --strict

# Run Python unit tests
test:
    python3 -m unittest discover -s tests -v

# Package every skill as a .skill archive
package:
    rm -rf dist
    mkdir -p dist
    for skill in $(find . -maxdepth 1 -mindepth 1 -type d ! -name '.*' -exec test -f '{}/SKILL.md' \; -print | sed 's|^./||' | sort); do \
      echo "Packaging: ${skill}"; \
      (cd "${skill}" && zip -qr "../dist/${skill}.skill" . -x '.*'); \
    done

# Verify every skill can be packaged as a .skill archive
package-check: package
    rm -rf dist

# Run configured prek hooks across the repository
hooks:
    uvx prek run --all-files

# Format the justfile when supported by the installed just version
fmt-just:
    just --fmt
