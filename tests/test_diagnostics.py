from pathlib import Path

from agents_team.diagnostics import build_doctor_report


def test_doctor_reports_valid_repository() -> None:
    report = build_doctor_report(Path("."), "codex")

    assert not report.has_errors
    assert any(
        check.status == "OK" and check.label == "agent validation"
        for check in report.checks
    )
    assert len(report.install_results) == 5


def test_doctor_detects_project_install_conflicts(tmp_path: Path) -> None:
    target_dir = tmp_path / ".claude" / "agents"
    target_dir.mkdir(parents=True)
    (target_dir / "raidel-auditor.md").write_text("manual agent", encoding="utf-8")

    report = build_doctor_report(Path("."), "claude", tmp_path)

    assert not report.has_errors
    assert any(
        check.status == "WARN" and check.label == "install conflicts"
        for check in report.checks
    )
    assert any(result.action == "skipped" for result in report.install_results)
