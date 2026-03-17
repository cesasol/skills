# Infrastructure — Auth, Config, Tokens, Keys, Repo, Clusters

Complete reference for authentication, project/repo management, and infrastructure commands.

## Table of Contents

- [Auth](#auth)
- [Config](#config)
- [Repository / Project](#repository--project)
- [Tokens](#tokens)
- [Deploy Keys](#deploy-keys)
- [Secure Files](#secure-files)
- [SSH Keys](#ssh-keys)
- [GPG Keys](#gpg-keys)
- [Clusters](#clusters)

## Auth

```bash
# Check authentication status
glab auth status

# Login with token (non-interactive)
glab auth login --hostname gitlab.example.com --token "$GITLAB_TOKEN"

# Login to gitlab.com
glab auth login --token "$GITLAB_TOKEN"

# Logout
glab auth logout --hostname gitlab.example.com

# Configure Docker credential helper
glab auth configure-docker
```

> **Agent rule:** Never use `glab auth login` interactively. Always pass `--token`. Never log or display tokens.

## Config

### Respected settings

| Key | Description | Default |
|-----|-------------|---------|
| `host` | GitLab hostname | `https://gitlab.com` |
| `token` | Access token | From environment variables |
| `editor` | Editor command | `$EDITOR` |
| `browser` | Browser command | `$BROWSER` |
| `glab_pager` | Pager command | (none) |
| `glamour_style` | Markdown style | `dark`, `light`, `notty` |
| `check_update` | Auto-update check | `true` |
| `display_hyperlinks` | Show hyperlinks in TTY | `false` |

```bash
# Get a setting
glab config get host

# Set a setting
glab config set host https://gitlab.example.com

# Global config
glab config set host https://gitlab.example.com --global
```

> **Agent rule:** Use `glab config get` for non-sensitive settings only. Never `glab config get token`.

## Repository / Project

### View

```bash
# Current repo
glab repo view -F json

# Specific repo
glab repo view group/project -F json
```

### Search

```bash
glab repo search --search "my-project" -F json
```

### Clone

```bash
# Clone by path
glab repo clone group/project

# Clone into specific directory
glab repo clone group/project ./my-dir

# Clone all repos in a group
glab repo clone --group my-group

# With git flags
glab repo clone group/project -- --depth=1
```

### Create

```bash
# Create new project
glab repo create my-project

# In a group
glab repo create my-group/my-project

# With description and visibility
glab repo create my-project --description "My new project" --private
glab repo create my-project --internal
glab repo create my-project --public
```

### Fork

```bash
glab repo fork group/project
glab repo fork group/project --name my-fork
```

### Update

```bash
glab repo update --description "Updated description"
glab repo update --visibility private
glab repo update --default-branch main
```

### Members

```bash
# List members
glab repo members list -F json

# Add member
glab repo members add --username newuser --access-level 30

# Remove member
glab repo members remove --username olduser
```

#### Access levels

| Level | Name |
|-------|------|
| 10 | Guest |
| 20 | Reporter |
| 30 | Developer |
| 40 | Maintainer |
| 50 | Owner |

### Other

```bash
# Archive repository
glab repo archive

# Download archive
glab repo archive download --format zip

# List contributors
glab repo contributors -F json

# Delete project (dangerous!)
glab repo delete my-project --yes

# Transfer to new namespace
glab repo transfer my-project --target-namespace new-group

# Mirror
glab repo mirror --url https://github.com/org/repo.git --direction push
```

## Tokens

### Create

```bash
# Personal access token
glab token create "my-pat" --scopes api,read_user --expires-at 2025-12-31

# Project access token
glab token create "deploy-token" --type project --scopes read_registry --expires-at 2025-12-31

# Group access token
glab token create "group-token" --type group --group my-group --scopes api --access-level 30
```

### List

```bash
# Personal tokens
glab token list -F json

# Project tokens
glab token list --type project -F json

# Group tokens
glab token list --type group --group my-group -F json
```

### Revoke

```bash
glab token revoke "my-pat"
glab token revoke 12345  # by ID
```

### Rotate

```bash
glab token rotate "my-pat"
glab token rotate "my-pat" --expires-at 2026-06-01
```

## Deploy Keys

```bash
# List deploy keys
glab deploy-key list -F json

# Add a deploy key
glab deploy-key add ~/.ssh/id_ed25519.pub --title "CI Deploy Key"

# Add with write access
glab deploy-key add ~/.ssh/id_ed25519.pub --title "CI Deploy Key" --can-push

# Get deploy key details
glab deploy-key get <key-id> -F json

# Delete
glab deploy-key delete <key-id>
```

## Secure Files

Secure files are stored outside the repo for use in CI/CD pipelines (max 5 MB, max 100 files).

```bash
# List secure files
glab securefile list -F json

# Upload a secure file
glab securefile create "my-keystore" ./keystore.jks

# Download
glab securefile download <file-id>
glab securefile download <file-id> --path ./output/

# Get details
glab securefile get <file-id>

# Remove
glab securefile remove <file-id> --yes
```

## SSH Keys

```bash
# List SSH keys
glab ssh-key list -F json

# Add SSH key
glab ssh-key add ~/.ssh/id_ed25519.pub --title "My Workstation"

# Add with expiry
glab ssh-key add ~/.ssh/id_ed25519.pub --title "Temp Key" --expires-at 2025-12-31

# Get key details
glab ssh-key get <key-id> -F json

# Delete
glab ssh-key delete <key-id> --yes
```

## GPG Keys

```bash
# List GPG keys
glab gpg-key list -F json

# Add GPG key
glab gpg-key add ./my-gpg-key.pub

# Get key details
glab gpg-key get <key-id> -F json

# Delete
glab gpg-key delete <key-id>
```

## Clusters

### Agent management

```bash
# List agents
glab cluster agent list -F json

# Get agent details
glab cluster agent get <agent-id> -F json
```

### Object graph (experimental)

```bash
# Query Kubernetes objects
glab cluster graph --agent-id <id>
```
