from __future__ import annotations

from pathlib import Path


CONTEXT_FILES = [
    "AGENTS.md",
    ".openclaw/system_prompt.md",
    ".openclaw/context.md",
]


def read_text_if_exists(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return None

    return content


def load_project_context(cwd: Path) -> list[tuple[str, str]]:
    contexts: list[tuple[str, str]] = []

    for relative_path in CONTEXT_FILES:
        path = cwd / relative_path
        content = read_text_if_exists(path)
        if content:
            contexts.append((relative_path, content))

    return contexts


def build_system_prompt(cwd: Path, base_prompt: str) -> str:
    contexts = load_project_context(cwd)

    if not contexts:
        return base_prompt

    parts = [base_prompt]

    for source, content in contexts:
        parts.append(
            f"\n\n# Project Context: {source}\n\n{content}"
        )

    return "".join(parts)