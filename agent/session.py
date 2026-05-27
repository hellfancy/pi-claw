from __future__ import annotations
from typing import Any
from agent.session_store import JsonlSessionStore

DEFAULT_SYSTEM_PROMPT = (
    "你是一个会调用工具的 coding agent。"
    "本地文件/代码相关问题优先使用 read/grep/find/ls。"
    "需要修改文件时使用 write/edit。"
    "需要运行命令时使用 bash。"
)

class AgentSession:
    def __init__(
        self,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        tools: list[dict[str, Any]] | None = None,
        messages: list[dict[str, Any]] | None = None,
        store: JsonlSessionStore | None = None
    ) -> None:
        self.system_prompt = system_prompt
        self.messages: list[dict[str, Any]] = list(messages or [])
        self.tools = tools or []
        self.store = store

    def add_user_message(self, content: str) -> dict[str, Any]:
        messages = {
            "role": "user",
            "content": content
        }
        return self._append_message(messages)

    def add_assistant_message(self, message: dict[str, Any]) -> dict[str, Any]:
        return self._append_message(message)

    def add_tool_message(self, message: dict[str, Any]) -> dict[str, Any]:
        return self._append_message(message)

    def _append_message(self, message: dict[str, Any]) -> dict[str, Any]:
        self.messages.append(message)
        if self.store:
            self.store.append_message(message)
        return message