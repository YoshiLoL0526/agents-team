# Agents Team

Agents Team keeps one canonical team of AI agents in this repository and
installs that team into multiple AI agent tools.

Initial targets:

- Codex
- Claude Code
- OpenCode

The source format is Markdown with YAML frontmatter. Codex receives generated
TOML files, while Claude Code and OpenCode receive generated Markdown files.

## Status

This project is in its first implementation phase. The current MVP supports:

- Canonical agents in `agents/`.
- Validation of required metadata and permissions.
- Rendering native files for Codex, Claude Code, and OpenCode.
- Global installation by default.
- Project-local installation with `--project`.
- Safe overwrites using a generated-file marker.
- `--dry-run`, `--backup`, and `--force`.

## Install For Development

```bash
pip install -e ".[dev]"
```

Or with `uv`:

```bash
uv sync --extra dev
```

## Commands

List canonical agents:

```bash
agents-team list
```

Validate agents:

```bash
agents-team validate
```

Run an environment and installation diagnostic:

```bash
agents-team doctor
agents-team doctor all --project .
agents-team doctor codex
```

Render one agent:

```bash
agents-team render codex raidel-auditor
agents-team render claude raidel-auditor
agents-team render opencode raidel-researcher
```

Render all agents into a directory:

```bash
agents-team render all --out generated/
```

Install globally:

```bash
agents-team install all
agents-team install codex
agents-team install codex --root-agent raidel-planner
agents-team install claude
agents-team install claude --root-agent raidel-planner
agents-team install opencode
```

Install into a project:

```bash
agents-team install all --project .
```

Preview installation without writing files:

```bash
agents-team install all --dry-run
```

Update installed agents from the current repository:

```bash
agents-team update all
agents-team update codex --root-agent raidel-planner
agents-team update claude --root-agent raidel-planner
```

## Default Install Locations

Global:

```text
Codex:       ~/.codex/agents/
Codex root:  ~/.codex/AGENTS.md
Claude Code: ~/.claude/agents/
Claude root: ~/.claude/CLAUDE.md
OpenCode:    ~/.config/opencode/agents/
```

Project:

```text
Codex:       <project>/.codex/agents/
Codex root:  <project>/AGENTS.md
Claude Code: <project>/.claude/agents/
Claude root: <project>/CLAUDE.md
OpenCode:    <project>/.opencode/agents/
```

## Canonical Agent Example

```markdown
---
id: raidel-auditor
description: Reviews code for correctness, security, regressions, maintainability risks, and missing tests.

targets:
  codex: true
  claude: true
  opencode: true

model:
  codex: gpt-5.3-codex
  claude: sonnet
  opencode: openai/gpt-5.3-codex

permissions:
  read: allow
  search: allow
  edit: deny
  write: deny
  delete: deny
  bash: ask
  network: deny
  webfetch: deny
  mcp: ask
---

You are a raidel-auditor agent.
```

See [docs](docs/README.md) for the design notes, format reference, adapter
rules, permission model, and CLI behavior.

## Tests

```bash
pytest
```
