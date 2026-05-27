from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Settings:
    model: str = "gpt-5.5"
    api_key_env: str = "OPENAI_API_KEY"
    base_url_env: str = "OPENAI_BASE_URL"
    sessions_dir: str = ".openclaw/sessions"
    skills_dir: str = ".openclaw/skills"
    enable_skills: bool = True
    default_session: str = "default"


def load_settings(cwd: Path) -> Settings:
    path = cwd / ".openclaw" / "settings.json"

    if not path.exists():
        return Settings()

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        return Settings()

    return Settings(
        model=_get_str(data, "model", Settings.model),
        api_key_env=_get_str(data, "api_key_env", Settings.api_key_env),
        base_url_env=_get_str(data, "base_url_env", Settings.base_url_env),
        sessions_dir=_get_str(data, "sessions_dir", Settings.sessions_dir),
        skills_dir=_get_str(data, "skills_dir", Settings.skills_dir),
        enable_skills=_get_bool(data, "enable_skills", Settings.enable_skills),
        default_session=_get_str(data, "default_session", Settings.default_session),
    )


def _get_str(data: dict[str, Any], key: str, default: str) -> str:
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value
    return default


def _get_bool(data: dict[str, Any], key: str, default: bool) -> bool:
    value = data.get(key)
    if isinstance(value, bool):
        return value
    return default