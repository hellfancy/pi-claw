from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.compaction import create_compaction_summary_message


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

                entry = json.loads(line)

                if entry.get("type") == "compaction":
                    messages.append(create_compaction_summary_message(entry["summary"]))
                    continue

                if entry.get("type") == "message":
                    message = entry.get("message")
                    if isinstance(message, dict):
                        messages.append(message)
                    continue

                messages.append(entry)

        return messages

    def append_message(self, message: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(message, ensure_ascii=False))
            f.write("\n")

    def append_compaction(
        self,
        *,
        summary: str,
        messages_before: int,
        messages_after: int,
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "type": "compaction",
            "summary": summary,
            "messages_before": messages_before,
            "messages_after": messages_after,
        }

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False))
            f.write("\n")


    def overwrite_messages(self, messages: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("w", encoding="utf-8") as f:
            for message in messages:
                f.write(json.dumps(message, ensure_ascii=False))
                f.write("\n")

    def overwrite_compacted(
        self,
        *,
        summary: str,
        messages: list[dict[str, Any]],
        messages_before: int,
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        compaction_entry = {
            "type": "compaction",
            "summary": summary,
            "messages_before": messages_before,
            "messages_after": len(messages) + 1,
        }

        with self.path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(compaction_entry, ensure_ascii=False))
            f.write("\n")

            for message in messages:
                f.write(json.dumps(message, ensure_ascii=False))
                f.write("\n")

    def clear(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")