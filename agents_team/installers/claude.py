from __future__ import annotations

from typing import Any

from agents_team.installers.common import (
    GENERATED_MARKER,
    apply_prompt_override,
    merge_dicts,
    yaml_frontmatter,
)
from agents_team.permissions import permission
from agents_team.schema import Agent


class ClaudeAdapter:
    tool = "claude"

    def output_name(self, agent: Agent) -> str:
        return f"{agent.id}.md"

    def render(self, agent: Agent) -> str:
        body = apply_prompt_override(agent.body, agent.prompt_overrides.get(self.tool))
        data: dict[str, Any] = {
            "name": agent.id,
            "description": agent.description,
        }

        model = agent.model.get(self.tool)
        if model:
            data["model"] = model

        reasoning = agent.reasoning.get(self.tool)
        if reasoning:
            data["effort"] = reasoning

        data = merge_dicts(data, self._permissions(agent))
        data = merge_dicts(data, agent.overrides.get(self.tool))

        return (
            f"<!-- {GENERATED_MARKER} -->\n"
            "---\n"
            f"{yaml_frontmatter(data)}\n"
            "---\n\n"
            f"{body.strip()}\n"
        )

    def _permissions(self, agent: Agent) -> dict[str, Any]:
        tools: list[str] = []
        disallowed: list[str] = []

        if permission(agent, "read") == "allow":
            tools.append("Read")
        if permission(agent, "search") == "allow":
            tools.extend(["Glob", "Grep"])

        if permission(agent, "edit") == "allow":
            tools.extend(["Edit", "MultiEdit"])
        elif permission(agent, "edit") == "deny":
            disallowed.extend(["Edit", "MultiEdit"])

        if permission(agent, "write") == "allow":
            tools.append("Write")
        elif permission(agent, "write") == "deny":
            disallowed.append("Write")

        if permission(agent, "bash") == "allow":
            tools.append("Bash")
        elif permission(agent, "bash") == "deny":
            disallowed.append("Bash")

        if permission(agent, "webfetch") == "allow":
            tools.extend(["WebFetch", "WebSearch"])
        elif permission(agent, "webfetch") == "deny":
            disallowed.extend(["WebFetch", "WebSearch"])

        result: dict[str, Any] = {}
        if tools:
            result["tools"] = _unique(tools)
        if disallowed:
            result["disallowedTools"] = _unique(disallowed)
        return result


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result

