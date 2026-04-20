from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from agents_team.installer import install_agents
from agents_team.paths import install_dir
from agents_team.rendering import render_agents, selected_tools
from agents_team.schema import InstallResult, ValidationIssue
from agents_team.validation import ensure_tool, has_errors, load_and_validate

CLI_COMMANDS = {
    "codex": "codex",
    "claude": "claude",
    "opencode": "opencode",
}


@dataclass(frozen=True)
class DoctorCheck:
    status: str
    label: str
    detail: str


@dataclass(frozen=True)
class DoctorReport:
    checks: list[DoctorCheck]
    validation_issues: list[ValidationIssue]
    install_results: list[InstallResult]

    @property
    def has_errors(self) -> bool:
        if has_errors(self.validation_issues):
            return True
        return any(check.status == "ERROR" for check in self.checks)


def build_doctor_report(
    root: Path,
    tool: str = "all",
    project: Path | None = None,
    root_agent: str | None = None,
) -> DoctorReport:
    ensure_tool(tool)
    checks: list[DoctorCheck] = []
    install_results: list[InstallResult] = []

    checks.append(_python_check())

    agents_dir = root / "agents"
    if agents_dir.exists() and agents_dir.is_dir():
        checks.append(DoctorCheck("OK", "agents directory", str(agents_dir)))
    else:
        checks.append(DoctorCheck("ERROR", "agents directory", f"missing: {agents_dir}"))

    agents, issues = load_and_validate(root)
    if has_errors(issues):
        checks.append(DoctorCheck("ERROR", "agent validation", "validation errors found"))
    else:
        checks.append(DoctorCheck("OK", "agent validation", f"{len(agents)} agent(s) valid"))

    if agents:
        for selected_tool in selected_tools(tool):
            rendered = render_agents(agents, selected_tool)
            checks.append(
                DoctorCheck(
                    "OK",
                    f"{selected_tool} render",
                    f"{len(rendered)} file(s) renderable",
                )
            )

    for selected_tool in selected_tools(tool):
        target_dir = install_dir(selected_tool, project)
        if target_dir.exists():
            detail = str(target_dir)
        else:
            detail = f"will be created when installing: {target_dir}"
        checks.append(DoctorCheck("OK", f"{selected_tool} target", detail))

        command = CLI_COMMANDS[selected_tool]
        command_path = shutil.which(command)
        if command_path:
            checks.append(DoctorCheck("OK", f"{selected_tool} CLI", command_path))
        else:
            checks.append(
                DoctorCheck(
                    "WARN",
                    f"{selected_tool} CLI",
                    f"`{command}` was not found on PATH",
                )
            )

    if agents and not has_errors(issues):
        install_results = install_agents(
            agents,
            tool,
            project=project,
            dry_run=True,
            root_agent=root_agent,
        )
        skipped = [result for result in install_results if result.action == "skipped"]
        if skipped:
            checks.append(
                DoctorCheck(
                    "WARN",
                    "install conflicts",
                    f"{len(skipped)} existing file(s) would be skipped without --force",
                )
            )
        else:
            checks.append(
                DoctorCheck("OK", "install conflicts", "no blocking conflicts detected")
            )

    return DoctorReport(checks, issues, install_results)


def _python_check() -> DoctorCheck:
    version = sys.version_info
    detail = f"{version.major}.{version.minor}.{version.micro}"
    if version >= (3, 13):
        return DoctorCheck("OK", "python", detail)
    return DoctorCheck("ERROR", "python", f"{detail}; Python 3.13+ required")
