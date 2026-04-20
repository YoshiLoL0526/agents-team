from __future__ import annotations

from typing import Any

from agents_team.installers.common import (
    GENERATED_MARKER,
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

    def root_output_name(self) -> str:
        return "AGENTS.md"

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

        data = merge_dicts(data, agent.overrides.get(self.tool))
        return render_toml(data)

    def render_root(self, root_agent: Agent, agents: list[Agent]) -> str:
        body = apply_prompt_override(
            root_agent.body,
            root_agent.prompt_overrides.get(self.tool),
        )
        subagents = [
            agent
            for agent in sorted(agents, key=lambda item: item.id)
            if agent.enabled_for(self.tool)
        ]
        subagent_lines = "\n".join(
            f"- `{agent.id}`: {agent.description}" for agent in subagents
        )

        return (
            f"<!-- {GENERATED_MARKER} -->\n"
            "# Codex Root Orchestrator\n\n"
            "You are the default orchestrator for this Codex environment.\n\n"
            f"{body.strip()}\n\n"
            "## Delegation Policy\n\n"
            "For each user request, decide whether to handle the work directly or "
            "delegate part of it to a subagent. Use subagents when the task benefits "
            "from parallel work, specialized review, independent research, or clear "
            "implementation ownership. Handle trivial edits, simple questions, and "
            "blocking next steps directly.\n\n"
            "Treat these standing root instructions as the user's default request "
            "for orchestration. When the delegation criteria are met, spawn the "
            "appropriate subagents without asking for another explicit confirmation "
            "unless the task itself is risky, destructive, or ambiguous.\n\n"
            "When delegating, keep each subtask concrete, self-contained, and useful "
            "to the user's goal. Assign clear ownership, avoid duplicate work between "
            "agents, and integrate completed results into one final response.\n\n"
            "## Available Subagents\n\n"
            f"{subagent_lines}\n\n"
            "Use these exact agent ids when spawning custom subagents. Prefer "
            "`explorer` for read-only codebase mapping, `builder` for scoped "
            "implementation, `reviewer` for correctness and regression review, and "
            "`researcher` for current external information or documentation checks.\n"
        )

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
