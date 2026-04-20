from __future__ import annotations

import os
from pathlib import Path

from agents_team.schema import TOOLS


def default_repo_root() -> Path:
    return Path.cwd()


def install_dir(tool: str, project: Path | None = None) -> Path:
    if tool not in TOOLS:
        raise ValueError(f"Unknown tool: {tool}")

    if project is not None:
        root = project.expanduser().resolve()
        project_dirs = {
            "codex": root / ".codex" / "agents",
            "claude": root / ".claude" / "agents",
            "opencode": root / ".opencode" / "agents",
        }
        return project_dirs[tool]

    home = Path.home()
    global_dirs = {
        "codex": codex_home() / "agents",
        "claude": home / ".claude" / "agents",
        "opencode": home / ".config" / "opencode" / "agents",
    }
    return global_dirs[tool]


def codex_home() -> Path:
    configured_home = os.environ.get("CODEX_HOME")
    if configured_home:
        return Path(configured_home).expanduser().resolve()
    return Path.home() / ".codex"


def root_install_dir(tool: str, project: Path | None = None) -> Path:
    if tool not in {"codex", "claude"}:
        raise ValueError(f"Root agent installation is not supported for {tool}")

    if project is not None:
        return project.expanduser().resolve()

    if tool == "claude":
        return Path.home() / ".claude"

    return codex_home()
