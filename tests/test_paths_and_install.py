from pathlib import Path

from agents_team.installer import install_rendered_file
from agents_team.installers.common import GENERATED_MARKER
from agents_team.paths import install_dir
from agents_team.schema import RenderedFile


def test_project_install_paths(tmp_path: Path) -> None:
    assert install_dir("codex", tmp_path) == tmp_path / ".codex" / "agents"
    assert install_dir("claude", tmp_path) == tmp_path / ".claude" / "agents"
    assert install_dir("opencode", tmp_path) == tmp_path / ".opencode" / "agents"


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

