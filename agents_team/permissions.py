from __future__ import annotations

from agents_team.schema import (
    PERMISSION_ACTIONS,
    PERMISSION_VALUES,
    Agent,
    ValidationIssue,
)


def validate_permissions(agent: Agent) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for action, value in agent.permissions.items():
        if action not in PERMISSION_ACTIONS:
            issues.append(
                ValidationIssue(
                    "error",
                    f"Unknown permission action: {action}.",
                    agent.source_path,
                )
            )
        if value not in PERMISSION_VALUES:
            issues.append(
                ValidationIssue(
                    "error",
                    f"Invalid permission value for {action}: {value}.",
                    agent.source_path,
                )
            )

    if agent.permissions.get("delete") == "allow" and agent.permissions.get("edit") == "deny":
        issues.append(
            ValidationIssue(
                "warning",
                "delete: allow conflicts with edit: deny.",
                agent.source_path,
            )
        )

    return issues


def permission(agent: Agent, action: str, default: str = "deny") -> str:
    return agent.permissions.get(action, default)

