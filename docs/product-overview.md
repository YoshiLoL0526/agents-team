# Product Overview

Agents Team keeps a reusable team of AI agents in one repository and installs
that team into different AI agent tools with one command.

The first supported tools are:

- Codex
- Claude Code
- OpenCode

## Initial Agent Team

The MVP includes five canonical agents:

- `raidel-planner`: coordinates work and integrates results.
- `raidel-scout`: inspects codebases and explains existing behavior.
- `raidel-coder`: implements scoped changes and tests.
- `raidel-auditor`: reviews code for bugs, risks, and missing tests.
- `raidel-researcher`: performs internet research and verifies current information.

## Goals

- Maintain one canonical source of truth for agent behavior.
- Install the same team globally into supported tools.
- Support project-local installation through an explicit flag.
- Update installed agents after changes are made in this repository.
- Preserve tool-specific capabilities through adapter overrides.
- Keep agents behaviorally consistent across tools as much as each tool allows.

## Non-Goals For MVP

- Perfect feature parity across all target tools.
- Automatic conversion of every tool-specific setting into a shared abstraction.
- Remote package distribution and self-updating from GitHub.
- Merge conflict resolution for manually edited installed agents.
- UI or desktop app behavior.

These can be added later once the source format and adapters are stable.

## Core Workflow

The expected user flow is:

```bash
agents-team list
agents-team validate
agents-team doctor
agents-team render codex
agents-team install all
agents-team update all
```

By default, installation is global. A project-specific installation is requested
with an explicit project flag:

```bash
agents-team install all --project .
agents-team install codex --project C:\path\to\project
```

## Source Of Truth

The repository owns the canonical agent definitions. Supported tools receive
generated native files:

- Codex receives TOML files.
- Claude Code receives Markdown files with YAML frontmatter.
- OpenCode receives Markdown files with YAML frontmatter.

## Update Semantics

The default update behavior is repository-driven:

- Installed files are generated from canonical source files.
- Generated outputs are overwritten on update when they contain the Agents Team
  generated-file marker.
- Files that do not contain the generated-file marker are skipped unless
  `--force` is passed.
- Backups are created only when `--backup` is passed.
- A manifest should eventually record installed files and source hashes.

For the MVP, `update` uses the same implementation as `install`.
