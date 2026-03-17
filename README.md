# Skills

A collection of skills for AI coding agents like [OpenCode](https://github.com/opencode-ai/opencode) and Claude Code.

## Available Skills

| Skill | Description |
|-------|-------------|
| [glab](glab/SKILL.md) | GitLab CLI (`glab`) — merge requests, issues, CI/CD pipelines, releases, API access, and full project management from the terminal. |

## Installation

### Requirements

- [OpenCode](https://github.com/opencode-ai/opencode) or any agent that supports the skills format (Claude Code, etc.)
- [glab](https://docs.gitlab.com/cli/) installed and authenticated (`glab auth login`)

### Install via Skills CLI

```bash
npx skills add cesasol/skills@glab
```

### Manual Installation

Clone the repo and symlink or copy the skill directory into your agent's skills folder:

```bash
# Global (all projects)
git clone https://gitlab.com/cesasol/skills.git
cp -r skills/glab ~/.agents/skills/glab

# Project-level
cp -r skills/glab .opencode/skills/glab
```

### Verify

Once installed, the agent should list `glab` in its available skills. You can test by asking:

> "Check the pipeline status for the current branch using glab."

## Developer

Built by [@cesasol](https://cesasol.dev/).

## License

MIT
