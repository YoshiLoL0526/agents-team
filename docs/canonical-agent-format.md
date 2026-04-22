# Canonical Agent Format

Agents Team uses Markdown with YAML frontmatter as the canonical source format.
This keeps long prompts easy to edit while still allowing structured metadata.

Canonical agents live under:

```text
agents/
  raidel-auditor.md
  raidel-scout.md
  raidel-coder.md
```

## File Shape

```markdown
---
id: raidel-auditor
description: Reviews code for correctness, security, regressions, and missing tests.

targets:
  codex: true
  claude: true
  opencode: true

model:
  codex: gpt-5.3-codex
  claude: sonnet
  opencode: openai/gpt-5.3-codex

reasoning:
  codex: high
  claude: high
  opencode: high

permissions:
  read: allow
  search: allow
  edit: deny
  write: deny
  delete: deny
  bash: ask
  network: deny
  webfetch: ask
  mcp: ask

overrides:
  codex:
    sandbox_mode: read-only
  claude:
    tools:
      - Read
      - Glob
      - Grep
    disallowedTools:
      - Edit
      - Write
      - Bash
  opencode:
    mode: subagent
    permission:
      edit: deny
      bash: ask
      webfetch: ask
---

You are a raidel-auditor agent.

Review code like an owner. Prioritize correctness, security, behavioral
regressions, and missing test coverage.
```

## Required Fields

### `id`

Stable agent identifier. It should be lowercase, filename-safe, and unique.

Recommended pattern:

```text
^[a-z][a-z0-9-]*$
```

### `description`

Short explanation used by target tools when deciding whether to invoke the
agent.

The description should explain capability and trigger conditions, not marketing
copy.

## Recommended Fields

### `targets`

Controls which tools receive the agent.

```yaml
targets:
  codex: true
  claude: true
  opencode: true
```

If omitted, the implementation should treat all supported targets as enabled.

### `model`

Tool-specific model preference.

```yaml
model:
  codex: gpt-5.3-codex
  claude: sonnet
  opencode: openai/gpt-5.3-codex
```

Model names are intentionally not normalized because providers and tools use
different naming schemes.

### `reasoning`

Tool-specific reasoning or effort preference.

```yaml
reasoning:
  codex: high
  claude: high
  opencode: high
```

Adapters are responsible for mapping this to the closest native field.

### `permissions`

Portable permission declarations using the Agents Team permission model.

See [Permissions Model](permissions-model.md).

### `overrides`

Native tool-specific settings that should be merged into generated output.

Overrides exist because tool capabilities do not map perfectly to a universal
schema.

## Prompt Body

The Markdown body after frontmatter is the shared prompt. This prompt should
describe the agent identity, priorities, constraints, output shape, and any
collaboration rules that should remain consistent across tools.

## Tool-Specific Prompt Overrides

The default pattern is one shared prompt with optional additions.

Prompt overrides should be additive unless there is a strong reason to replace
the shared prompt.

A future schema may support:

```yaml
prompt_overrides:
  codex:
    append: |
      Codex-specific instruction.
  claude:
    append: |
      Claude-specific instruction.
  opencode:
    append: |
      OpenCode-specific instruction.
```

This is intentionally separate from `overrides` so native configuration and
prompt content do not get mixed.

## Validation Rules

The validator should check:

- Frontmatter exists and is valid YAML.
- `id` is present and filename-safe.
- `description` is present and non-empty.
- Target keys are known.
- Permission actions are known.
- Permission values are one of `allow`, `ask`, or `deny`.
- Overrides are mappings.
- The Markdown body is not empty.
