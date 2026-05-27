"""Chatbot with Tool Support - 支持工具调用的对话机器人"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.runtime import AgentRuntime

SYSTEM_PROMPT = (
    # 系统提示词用于约束模型：遇到实时信息或事实核验类问题时优先调用搜索工具。
    "你是一个会调用工具的助手。"
    "当问题涉及最新信息、模型版本、产品发布时间或事实核验时，优先先调用 search 工具，再基于搜索结果回答。"
    "若问题是本地文件/代码相关，优先使用 read/grep/find/ls 等本地工具。"
)

def render_event(event) -> None:
    if event.type == "message_end":
        message = event.data["message"]
        role = message.get("role")

        if role == "assistant":
            content = message.get("content") or ""
            if content:
                print(f"\n🤖 Assistant: {content}\n")

        return

    if event.type == "tool_call_start":
        name = event.data["name"]
        arguments = event.data["arguments"]
        print(f"  [Tool] start: {name}({arguments})")
        return

    if event.type == "tool_call_end":
        name = event.data["name"]
        content = event.data["content"]
        is_error = event.data["is_error"]
        status = "error" if is_error else "done"
        preview = content[:200].replace("\n", "\\n")
        print(f"  [Tool] {status}: {name} -> {preview}")
        return

    if event.type == "error":
        print(f"\n❌ Error: {event.data['message']}\n")
        return

def run_chat() -> None:
    """运行对话循环"""
    print("=" * 60)
    print("🤖 Chatbot with Tools")
    print("=" * 60)
    print("可用工具: read, write, edit, bash, grep, find, ls, search")
    print("输入 'quit' 或 'exit' 退出\n")

    runtime = AgentRuntime()

    if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("OPENAI_BASE_URL"):
        print("请先设置 OPENAI_API_KEY 和 OPENAI_BASE_URL")
        return

    while True:
        user_input = input("👤 You: ").strip()

        if user_input.lower() in {"quit", "exit", "q"}:
            print("\n再见！")
            break

        if not user_input:
            continue

        for event in runtime.run_turn(user_input):
            render_event(event)


def main() -> None:
    if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("OPENAI_BASE_URL"):
        print("⚠️  提示：请先设置环境变量 OPENAI_API_KEY 和 OPENAI_BASE_URL")
        return

    run_chat()


if __name__ == "__main__":
    main()
