# Permissions Model

Agents Team uses a portable permission model based on actions and decisions.

The model is intentionally explicit from the beginning because each target tool
has different native permission controls.

## Permission Values

Every permission action uses one of:

```yaml
allow
ask
deny
```

Meaning:

- `allow`: the agent may perform the action without additional confirmation.
- `ask`: the tool should request approval when possible.
- `deny`: the agent should not be allowed to perform the action.

## Canonical Actions

```yaml
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
```

### `read`

Read existing files and project context.

### `search`

Search file contents, filenames, symbols, or project metadata.

### `edit`

Modify existing files.

### `write`

Create new files.

### `delete`

Remove files or directories.

### `bash`

Run shell commands.

### `network`

Access the network from tool execution or shell commands.

### `webfetch`

Fetch web content through native web tools, if the target has them.

### `mcp`

Use MCP servers or external tool connectors.

## Adapter Strategy

Permissions should be translated conservatively.

If a denied permission cannot be enforced by a target tool, validation should
warn. If enforcing a permission requires reducing the agent's capability more
than requested, the adapter should prefer safety and mention the limitation in
validation output.

## Codex Mapping

Codex permissions map primarily through sandbox settings and native subagent
configuration.

Suggested starting rules:

| Canonical Permissions | Codex Result |
| --- | --- |
| `edit: deny`, `write: deny`, `delete: deny` | `sandbox_mode = "read-only"` |
| any of `edit/write/delete: allow` | `sandbox_mode = "workspace-write"` |
| `network: deny` | disable network where supported |
| `network: allow` | enable network where supported |

When fine-grained controls are not available, use `overrides.codex` for native
settings.

## Claude Code Mapping

Claude Code permissions can be represented through native fields such as tools,
disallowed tools, and permission mode.

Suggested starting rules:

| Canonical Permission | Claude Code Result |
| --- | --- |
| `read: allow` | allow `Read` |
| `search: allow` | allow `Glob`, `Grep` |
| `edit: deny` | disallow `Edit`, `MultiEdit` |
| `write: deny` | disallow `Write` |
| `bash: deny` | disallow `Bash` |
| `bash: ask` | do not grant unrestricted Bash |
| `webfetch: deny` | disallow web fetch tool if available |

Exact Claude Code tool names should be kept in adapter code and revised when
the official schema changes.

## OpenCode Mapping

OpenCode exposes a native `permission` object.

Suggested starting rules:

```yaml
permission:
  edit: deny
  bash: ask
  webfetch: ask
```

Map direct equivalents where they exist. Use validation warnings for canonical
permissions without a native OpenCode equivalent.

## Overrides

Native overrides should be available for all tools:

```yaml
overrides:
  codex:
    sandbox_mode: read-only
  claude:
    disallowedTools:
      - Bash
  opencode:
    permission:
      edit: deny
      bash: ask
```

Overrides win over normalized permissions. This allows exact tool behavior when
the common model is too broad.

## Validation Requirements

The validator should catch:

- Unknown permission actions.
- Invalid permission values.
- Unsafe combinations, such as `delete: allow` with `edit: deny`.
- Permissions that cannot be represented for a target.
- Overrides that conflict with the common permission model.

Conflicts should warn by default. They should fail only when the generated output
would be misleading or unsafe.

