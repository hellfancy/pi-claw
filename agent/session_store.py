from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonlSessionStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load_messages(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        messages: list[dict[str, Any]] = []

        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                messages.append(json.loads(line))

        return messages

    def append_message(self, message: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(message, ensure_ascii=False))
            f.write("\n")

    def overwrite_messages(self, messages: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("w", encoding="utf-8") as f:
            for message in messages:
                f.write(json.dumps(message, ensure_ascii=False))
                f.write("\n")

    def clear(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")