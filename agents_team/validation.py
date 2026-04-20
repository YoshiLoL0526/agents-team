from __future__ import annotations

from collections import Counter
from pathlib import Path

from agents_team.parser import load_agents, validate_agent
from agents_team.permissions import validate_permissions
from agents_team.rendering import render_agents
from agents_team.schema import Agent, TOOL_CHOICES, TOOLS, ValidationIssue


def load_and_validate(root: Path) -> tuple[list[Agent], list[ValidationIssue]]:
    agents, issues = load_agents(root)

    for agent in agents:
        issues.extend(validate_agent(agent))
        issues.extend(validate_permissions(agent))

    issues.extend(_validate_duplicate_ids(agents))
    issues.extend(_validate_rendering(agents))
    return agents, issues


def has_errors(issues: list[ValidationIssue]) -> bool:
    return any(issue.is_error for issue in issues)


def ensure_tool(tool: str) -> None:
    if tool not in TOOL_CHOICES:
        choices = ", ".join(TOOL_CHOICES)
        raise ValueError(f"Unknown tool: {tool}. Expected one of: {choices}")


def _validate_duplicate_ids(agents: list[Agent]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    counts = Counter(agent.id for agent in agents if agent.id)
    duplicates = {agent_id for agent_id, count in counts.items() if count > 1}

    for agent in agents:
        if agent.id in duplicates:
            issues.append(
                ValidationIssue("error", f"Duplicate agent id: {agent.id}.", agent.source_path)
            )

    return issues


def _validate_rendering(agents: list[Agent]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for tool in TOOLS:
        try:
            render_agents(agents, tool)
        except Exception as exc:  # noqa: BLE001 - validation reports adapter failures.
            issues.append(
                ValidationIssue("error", f"Failed to render {tool}: {exc}", None)
            )
    return issues

