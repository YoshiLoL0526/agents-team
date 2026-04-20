# Agents Team Documentation

This directory captures the product decisions, source formats, adapter rules,
and implementation patterns for Agents Team.

Agents Team is a CLI-first tool for keeping one canonical team of AI agents in
this repository and installing that team into multiple agent tools. The initial
targets are Codex, Claude Code, and OpenCode.

## Documents

- [Product Overview](product-overview.md): goals, non-goals, core workflows, and
  MVP scope.
- [Canonical Agent Format](canonical-agent-format.md): the Markdown source format
  used by this repository.
- [Tool Adapters](tool-adapters.md): how canonical agents map to Codex, Claude
  Code, and OpenCode.
- [Permissions Model](permissions-model.md): portable permission vocabulary and
  adapter-specific translation rules.
- [CLI Design](cli-design.md): command surface, flags, and expected behavior.
- [Repository Patterns](repository-patterns.md): proposed project structure and
  implementation conventions.
- [Decision Log](decision-log.md): design decisions that should remain stable
  unless intentionally revisited.

