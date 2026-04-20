from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

TOOLS = ("codex", "claude", "opencode")
ALL_TOOL = "all"
TOOL_CHOICES = (*TOOLS, ALL_TOOL)

PERMISSION_ACTIONS = (
    "read",
    "search",
    "edit",
    "write",
    "delete",
    "bash",
    "network",
    "webfetch",
    "mcp",
)
PERMISSION_VALUES = ("allow", "ask", "deny")

IssueLevel = Literal["error", "warning"]


@dataclass(frozen=True)
class ValidationIssue:
    level: IssueLevel
    message: str
    file: Path | None = None

    @property
    def is_error(self) -> bool:
        return self.level == "error"


@dataclass(frozen=True)
class Agent:
    id: str
    description: str
    body: str
    source_path: Path
    targets: dict[str, bool] = field(default_factory=dict)
    model: dict[str, str] = field(default_factory=dict)
    reasoning: dict[str, str] = field(default_factory=dict)
    permissions: dict[str, str] = field(default_factory=dict)
    overrides: dict[str, dict[str, Any]] = field(default_factory=dict)
    prompt_overrides: dict[str, dict[str, str]] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    def enabled_for(self, tool: str) -> bool:
        return bool(self.targets.get(tool, True))


@dataclass(frozen=True)
class RenderedFile:
    tool: str
    agent_id: str
    filename: str
    content: str


@dataclass(frozen=True)
class InstallResult:
    rendered: RenderedFile
    target_path: Path
    action: str
    message: str

