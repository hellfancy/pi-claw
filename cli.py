from __future__ import annotations

import os
import argparse
from pathlib import Path

from agent import AgentRuntime, AgentSession, JsonlSessionStore, build_system_prompt, load_settings
from agent.session import DEFAULT_SYSTEM_PROMPT
from tools import get_tools

def render_event(event) -> None:
    if event.type == "message_end":
        message = event.data["message"]
        role = message.get("role")

        if role == "assistant":
            content = message.get("content") or ""
            if content:
                print(f"\n🤖 Assistant: {content}\n")

        return
    
    if event.type == "skill_invoked":
        print(f"  [Skill] {event.data['input']}")
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


def create_runtime(args: argparse.Namespace) -> tuple[AgentRuntime, str]:
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
    )
    return runtime, session_name


def main() -> None:
    args = parse_args()

    settings = load_settings(Path.cwd())
    if not os.environ.get(settings.api_key_env) or not os.environ.get(settings.base_url_env):
        print(f"请先设置 {settings.api_key_env} 和 {settings.base_url_env}")
        return

    runtime, session_name = create_runtime(args)

    print("=" * 60)
    print("pi-claw Agent")
    print("=" * 60)
    print(f"Session: {session_name}")
    print("输入 quit / exit / q 退出\n")

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