from __future__ import annotations

import os
import argparse
from pathlib import Path

from agent import AgentRuntime, AgentSession, JsonlSessionStore, build_system_prompt, load_settings
from agent.session import DEFAULT_SYSTEM_PROMPT
from tools import get_tools


def render_header(session_name: str) -> None:
    print("=" * 60)
    print("pi-claw TUI")
    print(f"Session: {session_name}")
    print("=" * 60)
    print("输入 quit / exit / q 退出\n")


def render_event(event) -> None:
    if event.type == "agent_start":
        print("\n" + "━" * 60)
        return

    if event.type == "skill_invoked":
        print(f"✨ Skill: {event.data['input']}")
        return

    if event.type == "compaction_start":
        print(
            f"  [Compaction] start: "
            f"{event.data['messages_to_summarize']} old messages, "
            f"keep {event.data['messages_to_keep']}"
        )
        return

    if event.type == "compaction_end":
        if event.data.get("ok"):
            print(
                f"  [Compaction] done: "
                f"{event.data['messages_before']} -> {event.data['messages_after']} messages"
            )
        else:
            print(f"  [Compaction] skipped: {event.data['error']}")
        return

    if event.type == "message_end":
        message = event.data["message"]
        role = message.get("role")

        if role == "user":
            content = message.get("content") or ""
            print("👤 User")
            print(indent(content))
            print()
            return

        if role == "assistant":
            content = message.get("content") or ""
            if content:
                print("🤖 Assistant")
                print(indent(content))
                print()
            return

        return

    if event.type == "turn_start":
        turn = event.data["turn"]
        print(f"↻ Turn {turn}")
        return

    if event.type == "tool_call_start":
        name = event.data["name"]
        arguments = event.data["arguments"]
        print(f"  🔧 Tool: {name}")
        print(f"     args: {arguments}")
        return

    if event.type == "tool_call_end":
        name = event.data["name"]
        content = event.data["content"]
        is_error = event.data["is_error"]
        status = "error" if is_error else "done"
        preview = preview_text(content)
        print(f"     {status}: {preview}")
        print()
        return

    if event.type == "turn_end":
        print()
        return

    if event.type == "agent_end":
        print("━" * 60 + "\n")
        return

    if event.type == "error":
        print(f"❌ Error: {event.data['message']}")
        return


def indent(text: str, prefix: str = "  ") -> str:
    return "\n".join(prefix + line for line in text.splitlines())


def preview_text(text: str, limit: int = 300) -> str:
    text = text.strip().replace("\n", "\\n")
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="pi-claw Agent")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="恢复已有会话",
    )
    parser.add_argument(
        "--session",
        default=None,
        help="会话名称，默认读取 settings.default_session",
    )
    return parser.parse_args()


def create_runtime(args: argparse.Namespace) -> AgentRuntime:
    cwd = Path.cwd()
    settings = load_settings(cwd)
    session_name = args.session or settings.default_session
    session_path = cwd / settings.sessions_dir / f"{session_name}.jsonl"
    store = JsonlSessionStore(session_path)

    if args.resume:
        messages = store.load_messages()
    else:
        store.clear()
        messages = []

    system_prompt = build_system_prompt(cwd, DEFAULT_SYSTEM_PROMPT)

    session = AgentSession(
        system_prompt=system_prompt,
        tools=[tool.to_llm_format() for tool in get_tools()],
        messages=messages,
        store=store,
    )

    runtime = AgentRuntime(
        session=session,
        skills_dir=settings.skills_dir,
        enable_skills=settings.enable_skills,
        model=settings.model,
        api_key_env=settings.api_key_env,
        base_url_env=settings.base_url_env,
        compact_enabled=settings.compact_enabled,
        compact_max_messages=settings.compact_max_messages,
        compact_keep_recent_messages=settings.compact_keep_recent_messages,
    )

    return runtime, session_name


def main() -> None:
    args = parse_args()

    settings = load_settings(Path.cwd())
    if not os.environ.get(settings.api_key_env) or not os.environ.get(settings.base_url_env):
        print(f"请先设置 {settings.api_key_env} 和 {settings.base_url_env}")
        return

    runtime, session_name = create_runtime(args)

    render_header(session_name)

    while True:
        user_input = input("👤 You: ").strip()

        if user_input.lower() in {"quit", "exit", "q"}:
            print("\n再见！")
            break

        if not user_input:
            continue

        for event in runtime.run_turn(user_input):
            render_event(event)


if __name__ == "__main__":
    main()