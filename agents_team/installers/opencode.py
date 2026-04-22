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


class OpenCodeAdapter:
    tool = "opencode"

    def output_name(self, agent: Agent) -> str:
        return f"{agent.id}.md"

    def render(self, agent: Agent) -> str:
        body = apply_prompt_override(agent.body, agent.prompt_overrides.get(self.tool))
        data: dict[str, Any] = {
            "description": agent.description,
            "mode": "subagent",
        }

        model = agent.model.get(self.tool)
        if model:
            data["model"] = model

        data = merge_dicts(data, self._permissions(agent))
        data = merge_dicts(data, agent.overrides.get(self.tool))

        return (
            "---\n"
            f"{yaml_frontmatter(data)}\n"
            "---\n\n"
            f"<!-- {GENERATED_MARKER} -->\n\n"
            f"{body.strip()}\n"
        )

    def _permissions(self, agent: Agent) -> dict[str, Any]:
        mapped: dict[str, str] = {}

        for source, target in (
            ("edit", "edit"),
            ("bash", "bash"),
            ("webfetch", "webfetch"),
        ):
            value = permission(agent, source, "ask")
            if value:
                mapped[target] = value

        return {"permission": mapped} if mapped else {}
