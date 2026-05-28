from __future__ import annotations

import json
from typing import Any

from core.llm import call_llm_simple


COMPACTION_SUMMARY_PREFIX = (
    "The previous conversation was compacted into the following summary:\n"
)


def should_compact(
    messages: list[dict[str, Any]],
    *,
    enabled: bool,
    max_messages: int,
) -> bool:
    if not enabled:
        return False
    return len(messages) > max_messages


def split_for_compaction(
    messages: list[dict[str, Any]],
    *,
    keep_recent_messages: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if keep_recent_messages <= 0:
        return messages, []

    if len(messages) <= keep_recent_messages:
        return [], messages

    return messages[:-keep_recent_messages], messages[-keep_recent_messages:]


def create_compaction_summary_message(summary: str) -> dict[str, Any]:
    return {
        "role": "system",
        "content": f"{COMPACTION_SUMMARY_PREFIX}{summary.strip()}",
    }


def build_compaction_prompt(messages: list[dict[str, Any]]) -> str:
    serialized_messages = "\n".join(
        _format_message_for_summary(message)
        for message in messages
    )

    return f"""请把下面这段 coding agent 会话压缩成一份后续可继续工作的上下文摘要。

要求：
- 保留用户目标、已经做出的决策、已修改/创建的文件、关键命令结果、未完成事项。
- 删除寒暄、重复内容、无意义中间过程。
- 如果出现工具调用结果，请总结结果，不要逐字复制长输出。
- 输出中文。
- 控制在 800 字以内。

会话内容：

{serialized_messages}
"""


def compact_messages(
    messages: list[dict[str, Any]],
    *,
    model: str,
    api_key_env: str,
    base_url_env: str,
) -> str:
    prompt = build_compaction_prompt(messages)
    return call_llm_simple(
        prompt,
        model=model,
        api_key_env=api_key_env,
        base_url_env=base_url_env,
    )


def _format_message_for_summary(message: dict[str, Any]) -> str:
    role = message.get("role", "unknown")
    content = message.get("content")

    if isinstance(content, str):
        text = content
    else:
        text = json.dumps(content, ensure_ascii=False)

    tool_calls = message.get("tool_calls")
    if tool_calls:
        text += "\nTool calls:\n"
        text += json.dumps(tool_calls, ensure_ascii=False)

    return f"[{role}]\n{text}\n"