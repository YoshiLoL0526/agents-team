# Repository Guidelines

## Project Structure & Module Organization

`agents_team/` contains the Python package and CLI implementation. Core modules include parsing, validation, rendering, permissions, installer orchestration, and target-specific installers in `agents_team/installers/`. `agents/` stores the canonical Markdown agent definitions with YAML frontmatter. `tests/` contains pytest coverage for CLI behavior, parsing, diagnostics, permissions, paths, and rendering. `docs/` holds design notes and reference material for formats, adapters, permissions, and CLI behavior.

## Build, Test, and Development Commands

Use Python 3.13 or newer. Set up development dependencies with:

```bash
uv sync --extra dev
```

Alternative editable install:

```bash
pip install -e ".[dev]"
```

Run the full test suite:

```bash
pytest
```

Useful local CLI checks:

```bash
agents-team list
agents-team validate
agents-team doctor codex --project .
agents-team render all --out generated/
```

`list` shows canonical agents, `validate` checks metadata and permissions, `doctor` previews environment/install state, and `render` generates target-native files.

## Coding Style & Naming Conventions

Write idiomatic Python with 4-space indentation and type annotations for public functions and non-obvious data structures. Keep modules focused around one responsibility, following the current names such as `parser.py`, `rendering.py`, and `permissions.py`. Use `snake_case` for modules, functions, variables, and test files. Agent definition files in `agents/` use lowercase ids such as `builder.md` and `reviewer.md`.

## Testing Guidelines

Tests use `pytest` and Typer's `CliRunner` for CLI assertions. Place new tests in `tests/` with filenames matching `test_*.py`. Name tests after observable behavior, for example `test_render_with_out_prints_rendered_files_table`. Prefer temporary directories through pytest fixtures such as `tmp_path` when testing file output or installation previews.

## Commit & Pull Request Guidelines

Recent history uses Conventional Commits, for example `feat(codex): support root agent install` and `fix(claude): install orchestrator as root instructions`. Keep commit subjects imperative and scoped when useful: `feat(cli): ...`, `fix(opencode): ...`, `test(rendering): ...`.

Pull requests should include a short description, the commands run for verification, and any affected targets: Codex, Claude Code, or OpenCode. Link related issues when available. Include screenshots or terminal output only when CLI formatting or rendered output changes.

## Security & Configuration Tips

Do not hand-edit generated installed files. Update canonical files in `agents/`, then render or install through `agents-team`. Use `--dry-run` before installation changes and `--backup` when overwriting existing generated files.
