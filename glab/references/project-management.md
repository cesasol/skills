# Project Management — Releases, Labels, Milestones, Variables, Snippets, Changelog

Complete reference for project organization and release management commands.

## Table of Contents

- [Releases](#releases)
- [Labels](#labels)
- [Milestones](#milestones)
- [Variables](#variables)
- [Snippets](#snippets)
- [Changelog](#changelog)

## Releases

### Create

```bash
# Create release from existing tag
glab release create v1.0.0 --title "Version 1.0.0" --notes "First stable release"

# Create with tag (creates tag if it doesn't exist)
glab release create v1.1.0 --title "v1.1.0" --notes "Bug fixes and improvements" --ref main

# With release notes from file
glab release create v1.2.0 --title "v1.2.0" --notes-file CHANGELOG.md

# Upload assets during creation
glab release create v1.0.0 ./build/app.tar.gz ./build/checksums.txt \
  --title "v1.0.0" --notes "Release with assets"

# With milestone association
glab release create v1.0.0 --title "v1.0.0" --milestone "v1.0" --notes "Milestone release"

# As pre-release
glab release create v2.0.0-beta.1 --title "v2.0.0 Beta 1" --notes "Beta release" --pre-release
```

### List

```bash
glab release list -F json
glab release list --per-page 5 -F json
```

### View

```bash
glab release view v1.0.0 -F json
```

### Download assets

```bash
# Download all assets from a release
glab release download v1.0.0

# To a specific directory
glab release download v1.0.0 --dir ./downloads/

# Specific asset by name
glab release download v1.0.0 --asset-name "app.tar.gz"
```

### Upload assets to existing release

```bash
glab release upload v1.0.0 ./build/app.tar.gz
glab release upload v1.0.0 ./build/app.tar.gz ./build/checksums.txt
```

### Delete

```bash
glab release delete v1.0.0 --yes
# Also delete associated tag
glab release delete v1.0.0 --with-tag --yes
```

## Labels

### Create

```bash
# Basic label
glab label create --name "priority::high" --color "#FF0000"

# With description
glab label create --name "type::bug" --color "#D73A4A" --description "Something isn't working"

# Group label
glab label create --name "team::backend" --color "#0075CA" --group my-group
```

### List

```bash
glab label list -F json
glab label list --per-page 100 -F json
```

### Get

```bash
glab label get <label-id> -F json
```

### Edit

```bash
glab label edit --name "priority::high" --new-name "priority::critical" --color "#B60205"
glab label edit --name "type::bug" --description "Updated description"
```

### Delete

```bash
glab label delete --name "deprecated-label"
```

## Milestones

### Create

```bash
# Project milestone
glab milestone create --title "v2.0" --description "Major release" --due-date 2025-06-01

# With start date
glab milestone create --title "Sprint 5" --start-date 2025-03-01 --due-date 2025-03-14

# Group milestone
glab milestone create --title "Q2 Goals" --group my-group
```

### List

```bash
# Project milestones
glab milestone list -F json

# Include closed
glab milestone list --state all -F json

# Group milestones
glab milestone list --group my-group -F json
```

### Get

```bash
glab milestone get --id 5 -F json
```

### Edit

```bash
glab milestone edit --id 5 --title "v2.0 (updated)" --due-date 2025-07-01

# Close a milestone
glab milestone edit --id 5 --state close
```

### Delete

```bash
glab milestone delete --id 5
```

## Variables

### Set (create)

```bash
# Project variable
glab variable set MY_VAR "my-value"

# Masked variable (hidden in logs)
glab variable set SECRET_KEY "s3cr3t" --masked

# Protected variable (only on protected branches)
glab variable set DEPLOY_KEY "key" --protected

# Scoped to environment
glab variable set DB_HOST "db.staging.example.com" --scope staging

# From file
glab variable set SSH_KEY --value @id_rsa --type file

# Group variable
glab variable set GROUP_VAR "value" --group my-group
```

### Get

```bash
glab variable get MY_VAR
glab variable get MY_VAR --scope production

# Group variable
glab variable get GROUP_VAR --group my-group
```

### List

```bash
glab variable list -F json

# Group variables
glab variable list --group my-group -F json
```

### Update

```bash
glab variable update MY_VAR "new-value"
glab variable update MY_VAR "new-value" --masked --protected
```

### Delete

```bash
glab variable delete MY_VAR
glab variable delete MY_VAR --scope staging
```

### Export

```bash
# Export all variables (dotenv format)
glab variable export

# Group variables
glab variable export --group my-group
```

## Snippets

```bash
# Create snippet from file
glab snippet create -t "My config" myconfig.yml

# Create from multiple files
glab snippet create -t "Project configs" config.yml docker-compose.yml

# Create from stdin
echo "Hello World" | glab snippet create -t "Quick note" -f "note.txt"
```

### Key flags

| Flag | Description |
|------|-------------|
| `-t, --title` | Snippet title (required) |
| `-f, --filename` | Filename when reading from stdin |
| `-d, --description` | Snippet description |
| `-v, --visibility` | `private`, `internal`, or `public` |

## Changelog

```bash
# Generate changelog
glab changelog generate

# For a specific version
glab changelog generate --version v1.2.0

# From a specific date
glab changelog generate --from 2025-01-01

# Custom config file
glab changelog generate --config-file .gitlab/changelog_config.yml
```
