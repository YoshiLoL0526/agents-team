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
    supported_frontmatter_fields = {"name", "description", "model", "tools"}

    def output_name(self, agent: Agent) -> str:
        return f"{agent.id}.md"

    def root_output_name(self) -> str:
        return "CLAUDE.md"

    def render(self, agent: Agent) -> str:
        body = apply_prompt_override(agent.body, agent.prompt_overrides.get(self.tool))
        data: dict[str, Any] = {
            "name": agent.id,
            "description": agent.description,
        }

        model = agent.model.get(self.tool)
        if model:
            data["model"] = model

        data = merge_dicts(data, self._permissions(agent))
        data = merge_dicts(data, self._supported_overrides(agent))

        tools = data.get("tools")
        if tools:
            data["tools"] = _tools_csv(tools)
        else:
            data.pop("tools", None)

        return (
            "---\n"
            f"# {GENERATED_MARKER}\n"
            f"{yaml_frontmatter(data)}\n"
            "---\n\n"
            f"{body.strip()}\n"
        )

    def render_root(self, root_agent: Agent, agents: list[Agent]) -> str:
        body = apply_prompt_override(
            root_agent.body,
            root_agent.prompt_overrides.get(self.tool),
        )
        subagents = [
            agent
            for agent in sorted(agents, key=lambda item: item.id)
            if agent.enabled_for(self.tool) and agent.id != root_agent.id
        ]
        subagent_lines = "\n".join(
            f"- `{agent.id}`: {agent.description}" for agent in subagents
        )
        model = root_agent.model.get(self.tool)
        model_preference = (
            f"Model preference: use `{model}` for this root planner session "
            "when the target tool supports selecting the main model.\n\n"
            if model
            else ""
        )
        return (
            f"<!-- {GENERATED_MARKER} -->\n"
            f"# Claude Code Root Planner\n\n"
            "You are the default planner for this Claude Code environment.\n\n"
            f"{model_preference}"
            f"{body.strip()}\n\n"
            "## Delegation Policy\n\n"
            "Treat this file as the main-agent instruction source. The files in "
            "`.claude/agents/` are specialized subagents, not alternate primary "
            "agents.\n\n"
            "For each user request, decide whether to handle the work directly or "
            "delegate part of it with Claude Code's Task tool. Use subagents when "
            "the task benefits from a specialist, separate context, focused review, "
            "or independent research. Handle trivial edits, simple questions, and "
            "blocking next steps directly.\n\n"
            "When delegating, use the exact subagent name, give a concrete and "
            "self-contained task, and integrate the result into one final response. "
            "Do not delegate the same work to multiple subagents unless independent "
            "perspectives are explicitly useful.\n\n"
            "## Available Subagents\n\n"
            f"{subagent_lines}\n"
        )

    def _supported_overrides(self, agent: Agent) -> dict[str, Any]:
        overrides = agent.overrides.get(self.tool)
        if not overrides:
            return {}
        return {
            key: value
            for key, value in overrides.items()
            if key in self.supported_frontmatter_fields
        }

    def _permissions(self, agent: Agent) -> dict[str, Any]:
        tools: list[str] = []

        if permission(agent, "read") == "allow":
            tools.append("Read")
        if permission(agent, "search") == "allow":
            tools.extend(["Glob", "Grep"])

        if permission(agent, "edit") == "allow":
            tools.extend(["Edit", "MultiEdit"])

        if permission(agent, "write") == "allow":
            tools.append("Write")

        if permission(agent, "bash") == "allow":
            tools.append("Bash")

        if permission(agent, "webfetch") == "allow":
            tools.extend(["WebFetch", "WebSearch"])

        result: dict[str, Any] = {}
        if tools:
            result["tools"] = _unique(tools)
        return result


def _tools_csv(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ", ".join(str(item) for item in _unique([str(item) for item in value]))
    return str(value)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result
