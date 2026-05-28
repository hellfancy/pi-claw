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
    compact_enabled: bool = True
    compact_max_messages: int = 20
    compact_keep_recent_messages: int = 8

def load_settings(cwd: Path) -> Settings:
    path = cwd / ".openclaw" / "settings.json"
    defaults = Settings()

    if not path.exists():
        return defaults

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        return defaults

    return Settings(
        model=_get_str(data, "model", defaults.model),
        api_key_env=_get_str(data, "api_key_env", defaults.api_key_env),
        base_url_env=_get_str(data, "base_url_env", defaults.base_url_env),
        sessions_dir=_get_str(data, "sessions_dir", defaults.sessions_dir),
        skills_dir=_get_str(data, "skills_dir", defaults.skills_dir),
        enable_skills=_get_bool(data, "enable_skills", defaults.enable_skills),
        default_session=_get_str(data, "default_session", defaults.default_session),
        compact_enabled=_get_bool(data, "compact_enabled", defaults.compact_enabled),
        compact_max_messages=_get_int(
            data,
            "compact_max_messages",
            defaults.compact_max_messages,
        ),
        compact_keep_recent_messages=_get_int(
            data,
            "compact_keep_recent_messages",
            defaults.compact_keep_recent_messages,
        ),
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

def _get_int(data: dict[str, Any], key: str, default: int) -> int:
    value = data.get(key)
    if isinstance(value, int) and value > 0:
        return value
    return default