from pathlib import Path

from agents_team.parser import load_agents
from agents_team.validation import load_and_validate


def test_loads_repository_agents() -> None:
    agents, issues = load_agents(Path("."))

    assert not issues
    assert {agent.id for agent in agents} == {
        "orchestrator",
        "explorer",
        "builder",
        "reviewer",
        "researcher",
    }


def test_repository_agents_are_valid() -> None:
    agents, issues = load_and_validate(Path("."))

    assert [issue for issue in issues if issue.level == "error"] == []
    assert len(agents) == 5

