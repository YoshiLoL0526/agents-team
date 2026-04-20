from __future__ import annotations

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
        "codex": home / ".codex" / "agents",
        "claude": home / ".claude" / "agents",
        "opencode": home / ".config" / "opencode" / "agents",
    }
    return global_dirs[tool]

