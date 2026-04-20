from pathlib import Path

from agents_team.installer import install_agents, install_rendered_file
from agents_team.installers.common import GENERATED_MARKER
from agents_team.parser import load_agents
from agents_team.paths import codex_home, install_dir, root_install_dir
from agents_team.schema import RenderedFile


def test_project_install_paths(tmp_path: Path) -> None:
    assert install_dir("codex", tmp_path) == tmp_path / ".codex" / "agents"
    assert install_dir("claude", tmp_path) == tmp_path / ".claude" / "agents"
    assert install_dir("opencode", tmp_path) == tmp_path / ".opencode" / "agents"
    assert root_install_dir("codex", tmp_path) == tmp_path
    assert root_install_dir("claude", tmp_path) == tmp_path


def test_global_codex_paths_respect_codex_home(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))

    assert codex_home() == tmp_path
    assert install_dir("codex") == tmp_path / "agents"
    assert root_install_dir("codex") == tmp_path


def test_install_skips_non_generated_file_without_force(tmp_path: Path) -> None:
    rendered = RenderedFile("claude", "reviewer", "reviewer.md", "new content")
    target = tmp_path / "reviewer.md"
    target.write_text("manual content", encoding="utf-8")

    result = install_rendered_file(rendered, tmp_path)

    assert result.action == "skipped"
    assert target.read_text(encoding="utf-8") == "manual content"


def test_install_updates_generated_file(tmp_path: Path) -> None:
    rendered = RenderedFile("claude", "reviewer", "reviewer.md", "new content")
    target = tmp_path / "reviewer.md"
    target.write_text(f"<!-- {GENERATED_MARKER} -->\nold", encoding="utf-8")

    result = install_rendered_file(rendered, tmp_path)

    assert result.action == "updated"
    assert target.read_text(encoding="utf-8") == "new content"


def test_install_updates_empty_existing_file_without_force(tmp_path: Path) -> None:
    rendered = RenderedFile("codex", "orchestrator", "AGENTS.md", "generated content")
    target = tmp_path / "AGENTS.md"
    target.write_text("", encoding="utf-8")

    result = install_rendered_file(rendered, tmp_path)

    assert result.action == "updated"
    assert target.read_text(encoding="utf-8") == "generated content"


def test_install_codex_root_agent_to_project(tmp_path: Path) -> None:
    agents, issues = load_agents(Path("."))
    assert issues == []

    results = install_agents(agents, "codex", project=tmp_path, root_agent="orchestrator")

    root_result = next(result for result in results if result.rendered.filename == "AGENTS.md")
    assert root_result.action == "created"
    assert root_result.target_path == tmp_path / "AGENTS.md"
    assert "Codex Root Orchestrator" in root_result.target_path.read_text(encoding="utf-8")


def test_install_codex_root_agent_skips_manual_project_agents_md(tmp_path: Path) -> None:
    agents, issues = load_agents(Path("."))
    assert issues == []
    target = tmp_path / "AGENTS.md"
    target.write_text("manual instructions", encoding="utf-8")

    results = install_agents(agents, "codex", project=tmp_path, root_agent="orchestrator")

    root_result = next(result for result in results if result.rendered.filename == "AGENTS.md")
    assert root_result.action == "skipped"
    assert target.read_text(encoding="utf-8") == "manual instructions"


def test_install_invalid_codex_root_agent_writes_nothing(tmp_path: Path) -> None:
    agents, issues = load_agents(Path("."))
    assert issues == []

    try:
        install_agents(agents, "codex", project=tmp_path, root_agent="missing")
    except ValueError as exc:
        assert "Agent not found" in str(exc)
    else:
        raise AssertionError("expected invalid root agent to fail")

    assert not (tmp_path / ".codex").exists()
    assert not (tmp_path / "AGENTS.md").exists()


def test_install_codex_root_agent_skips_when_subagent_conflicts(tmp_path: Path) -> None:
    agents, issues = load_agents(Path("."))
    assert issues == []
    subagent = tmp_path / ".codex" / "agents" / "builder.toml"
    subagent.parent.mkdir(parents=True)
    subagent.write_text("manual builder", encoding="utf-8")

    results = install_agents(agents, "codex", project=tmp_path, root_agent="orchestrator")

    builder_result = next(result for result in results if result.rendered.agent_id == "builder")
    root_result = next(result for result in results if result.rendered.filename == "AGENTS.md")
    assert builder_result.action == "skipped"
    assert root_result.action == "skipped"
    assert "subagent conflicts" in root_result.message
    assert not (tmp_path / "AGENTS.md").exists()


def test_install_claude_root_agent_to_project(tmp_path: Path) -> None:
    agents, issues = load_agents(Path("."))
    assert issues == []

    results = install_agents(agents, "claude", project=tmp_path, root_agent="orchestrator")

    root_result = next(result for result in results if result.rendered.filename == "CLAUDE.md")
    assert root_result.action == "created"
    assert root_result.target_path == tmp_path / "CLAUDE.md"
    assert "Claude Code Root Orchestrator" in root_result.target_path.read_text(encoding="utf-8")
    assert not (tmp_path / ".claude" / "agents" / "orchestrator.md").exists()
    assert (tmp_path / ".claude" / "agents" / "builder.md").exists()


def test_install_all_root_agent_includes_codex_and_claude_roots(tmp_path: Path) -> None:
    agents, issues = load_agents(Path("."))
    assert issues == []

    results = install_agents(agents, "all", project=tmp_path, root_agent="orchestrator")

    filenames = {result.rendered.tool: result.rendered.filename for result in results if result.rendered.filename in {"AGENTS.md", "CLAUDE.md"}}
    assert filenames == {"codex": "AGENTS.md", "claude": "CLAUDE.md"}
