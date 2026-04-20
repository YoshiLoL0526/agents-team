# Tool Adapters

Adapters convert canonical agent files into each tool's native format.

The initial targets are Codex, Claude Code, and OpenCode.

## Codex

Official documentation: <https://developers.openai.com/codex/subagents>

### Native Format

Codex subagents use TOML files.

Global location:

```text
~/.codex/agents/
```

Project location:

```text
<project>/.codex/agents/
```

### Generated File

```text
~/.codex/agents/reviewer.toml
```

### Field Mapping

| Canonical Field | Codex Field |
| --- | --- |
| `id` | `name` |
| `description` | `description` |
| Markdown body | `developer_instructions` |
| `model.codex` | `model` |
| `reasoning.codex` | `model_reasoning_effort` |
| `permissions` | best-effort sandbox and native permission settings |
| `overrides.codex` | merged into TOML output |

### Example Output

```toml
name = "reviewer"
description = "Reviews code for correctness, security, regressions, and missing tests."
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
You are a reviewer agent.

Review code like an owner.
"""
```

## Claude Code

Official documentation: <https://code.claude.com/docs/en/sub-agents>

### Native Format

Claude Code subagents use Markdown files with YAML frontmatter.

Global location:

```text
~/.claude/agents/
```

Project location:

```text
<project>/.claude/agents/
```

### Generated File

```text
~/.claude/agents/reviewer.md
```

### Field Mapping

| Canonical Field | Claude Code Field |
| --- | --- |
| `id` | `name` |
| `description` | `description` |
| Markdown body | Markdown body |
| `model.claude` | `model` |
| `reasoning.claude` | `effort`, if supported by current Claude Code schema |
| `permissions` | tools, disallowed tools, or permission mode |
| `overrides.claude` | merged into YAML frontmatter |

### Example Output

```markdown
---
name: reviewer
description: Reviews code for correctness, security, regressions, and missing tests.
model: sonnet
tools:
  - Read
  - Glob
  - Grep
disallowedTools:
  - Edit
  - Write
  - Bash
---

You are a reviewer agent.

Review code like an owner.
```

## OpenCode

Official documentation: <https://opencode.ai/docs/agents/>

### Native Format

OpenCode agents use Markdown files with YAML frontmatter.

Global location:

```text
~/.config/opencode/agents/
```

Project location:

```text
<project>/.opencode/agents/
```

### Generated File

```text
~/.config/opencode/agents/reviewer.md
```

OpenCode derives the agent name from the filename.

### Field Mapping

| Canonical Field | OpenCode Field |
| --- | --- |
| `id` | output filename |
| `description` | `description` |
| Markdown body | Markdown body |
| `model.opencode` | `model` |
| `reasoning.opencode` | best-effort native equivalent, if supported |
| `permissions` | `permission` mapping |
| `overrides.opencode` | merged into YAML frontmatter |

### Example Output

```markdown
---
description: Reviews code for correctness, security, regressions, and missing tests.
mode: subagent
model: anthropic/claude-sonnet-4-20250514
permission:
  edit: deny
  bash: ask
  webfetch: ask
---

You are a reviewer agent.

Review code like an owner.
```

## Adapter Merge Order

Adapters should build generated output in this order:

1. Required native fields derived from canonical fields.
2. Optional normalized fields such as model, reasoning, and permissions.
3. Native settings from `overrides.<tool>`.
4. Prompt body with any future prompt override additions.

Tool-specific overrides win over normalized fields.

## Unsupported Fields

If a canonical field cannot be represented exactly in a target tool, validation
should warn instead of failing unless the mismatch could create unsafe behavior.

Examples:

- A denied permission that cannot be enforced should produce a warning.
- A model name that is unknown to the target may produce a warning.
- A reasoning value unsupported by the target may be omitted with a warning.

