from __future__ import annotations

from typing import Any

from agents_team.installers.common import (
    apply_prompt_override,
    merge_dicts,
    render_toml,
)
from agents_team.permissions import permission
from agents_team.schema import Agent


class CodexAdapter:
    tool = "codex"

    def output_name(self, agent: Agent) -> str:
        return f"{agent.id}.toml"

    def render(self, agent: Agent) -> str:
        body = apply_prompt_override(agent.body, agent.prompt_overrides.get(self.tool))
        data: dict[str, Any] = {
            "name": agent.id,
            "description": agent.description,
            "developer_instructions": body,
        }

        model = agent.model.get(self.tool)
        if model:
            data["model"] = model

        reasoning = agent.reasoning.get(self.tool)
        if reasoning:
            data["model_reasoning_effort"] = reasoning

        sandbox_mode = self._sandbox_mode(agent)
        if sandbox_mode:
            data["sandbox_mode"] = sandbox_mode

        if permission(agent, "network") == "allow":
            data["network_access"] = True
        elif permission(agent, "network") == "deny":
            data["network_access"] = False

        data = merge_dicts(data, agent.overrides.get(self.tool))
        return render_toml(data)

    def _sandbox_mode(self, agent: Agent) -> str | None:
        if (
            permission(agent, "edit") == "deny"
            and permission(agent, "write") == "deny"
            and permission(agent, "delete") == "deny"
        ):
            return "read-only"

        if permission(agent, "edit") in {"allow", "ask"} or permission(
            agent, "write"
        ) in {"allow", "ask"}:
            return "workspace-write"

        return None

