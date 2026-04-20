from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from agents_team.schema import Agent, TOOLS, ValidationIssue

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")


class AgentParseError(Exception):
    def __init__(self, issue: ValidationIssue) -> None:
        super().__init__(issue.message)
        self.issue = issue


def discover_agent_files(root: Path) -> list[Path]:
    agents_dir = root / "agents"
    if not agents_dir.exists():
        return []
    return sorted(agents_dir.glob("*.md"))


def parse_agent_file(path: Path) -> Agent:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise AgentParseError(
            ValidationIssue("error", "Missing YAML frontmatter.", path)
        )

    frontmatter_text, body = match.groups()
    try:
        raw = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError as exc:
        raise AgentParseError(
            ValidationIssue("error", f"Invalid YAML frontmatter: {exc}", path)
        ) from exc

    if not isinstance(raw, dict):
        raise AgentParseError(
            ValidationIssue("error", "Frontmatter must be a mapping.", path)
        )

    return Agent(
        id=str(raw.get("id", "")),
        description=str(raw.get("description", "")),
        body=body.strip(),
        source_path=path,
        targets=_dict_of_bool(raw.get("targets")),
        model=_dict_of_str(raw.get("model")),
        reasoning=_dict_of_str(raw.get("reasoning")),
        permissions=_dict_of_str(raw.get("permissions")),
        overrides=_dict_of_dict(raw.get("overrides")),
        prompt_overrides=_dict_of_dict(raw.get("prompt_overrides")),
        raw=raw,
    )


def load_agents(root: Path) -> tuple[list[Agent], list[ValidationIssue]]:
    agents: list[Agent] = []
    issues: list[ValidationIssue] = []

    for path in discover_agent_files(root):
        try:
            agents.append(parse_agent_file(path))
        except AgentParseError as exc:
            issues.append(exc.issue)

    return agents, issues


def validate_agent(agent: Agent) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    path = agent.source_path

    if not agent.id:
        issues.append(ValidationIssue("error", "Missing required field: id.", path))
    elif not ID_RE.match(agent.id):
        issues.append(
            ValidationIssue(
                "error",
                "Agent id must match ^[a-z][a-z0-9-]*$.",
                path,
            )
        )

    expected_name = f"{agent.id}.md" if agent.id else None
    if expected_name and path.name != expected_name:
        issues.append(
            ValidationIssue(
                "warning",
                f"Filename should match agent id: expected {expected_name}.",
                path,
            )
        )

    if not agent.description.strip():
        issues.append(
            ValidationIssue("error", "Missing required field: description.", path)
        )

    if not agent.body.strip():
        issues.append(ValidationIssue("error", "Prompt body must not be empty.", path))

    for target in agent.targets:
        if target not in TOOLS:
            issues.append(
                ValidationIssue("error", f"Unknown target: {target}.", path)
            )

    for field_name, values in (
        ("model", agent.model),
        ("reasoning", agent.reasoning),
        ("overrides", agent.overrides),
        ("prompt_overrides", agent.prompt_overrides),
    ):
        for tool in values:
            if tool not in TOOLS:
                issues.append(
                    ValidationIssue(
                        "error", f"Unknown tool in {field_name}: {tool}.", path
                    )
                )

    return issues


def _dict_of_bool(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        return {}
    return {str(key): bool(item) for key, item in value.items()}


def _dict_of_str(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items()}


def _dict_of_dict(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        return {}

    result: dict[str, dict[str, Any]] = {}
    for key, item in value.items():
        if isinstance(item, dict):
            result[str(key)] = item
        else:
            result[str(key)] = {}
    return result

