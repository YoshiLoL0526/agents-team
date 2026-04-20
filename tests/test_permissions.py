from pathlib import Path

from agents_team.parser import parse_agent_file
from agents_team.permissions import validate_permissions


def test_rejects_unknown_permission_action(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text(
        """---
id: bad
description: Bad agent
permissions:
  teleport: allow
---

Prompt.
""",
        encoding="utf-8",
    )

    agent = parse_agent_file(path)
    issues = validate_permissions(agent)

    assert any("Unknown permission action" in issue.message for issue in issues)


def test_rejects_invalid_permission_value(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text(
        """---
id: bad
description: Bad agent
permissions:
  read: maybe
---

Prompt.
""",
        encoding="utf-8",
    )

    agent = parse_agent_file(path)
    issues = validate_permissions(agent)

    assert any("Invalid permission value" in issue.message for issue in issues)

