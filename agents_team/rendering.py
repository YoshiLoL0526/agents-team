from __future__ import annotations

from agents_team.installers.claude import ClaudeAdapter
from agents_team.installers.codex import CodexAdapter
from agents_team.installers.opencode import OpenCodeAdapter
from agents_team.schema import Agent, RenderedFile, TOOLS

ADAPTERS = {
    "codex": CodexAdapter(),
    "claude": ClaudeAdapter(),
    "opencode": OpenCodeAdapter(),
}


def selected_tools(tool: str) -> tuple[str, ...]:
    if tool == "all":
        return TOOLS
    if tool not in TOOLS:
        raise ValueError(f"Unknown tool: {tool}")
    return (tool,)


def render_agent(agent: Agent, tool: str) -> RenderedFile:
    adapter = ADAPTERS[tool]
    return RenderedFile(
        tool=tool,
        agent_id=agent.id,
        filename=adapter.output_name(agent),
        content=adapter.render(agent),
    )


def render_agents(
    agents: list[Agent],
    tool: str,
    agent_id: str | None = None,
) -> list[RenderedFile]:
    rendered: list[RenderedFile] = []
    for selected_tool in selected_tools(tool):
        for agent in agents:
            if agent_id and agent.id != agent_id:
                continue
            if not agent.enabled_for(selected_tool):
                continue
            rendered.append(render_agent(agent, selected_tool))
    return rendered

