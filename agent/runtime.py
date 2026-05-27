from __future__ import annotations

from typing import Iterator

from core.llm import call_llm
from tools import get_tools, ToolExecutor

from agent.events import AgentEvent
from agent.session import AgentSession

from pathlib import Path
from agent.skills import expand_skill_invocation, load_skills

class AgentRuntime:
    def __init__(
        self,
        session: AgentSession | None = None,
        skills_dir: str = ".openclaw/skills",
        enable_skills: bool = True,
        model: str = "gpt-5.5",
        api_key_env: str = "OPENAI_API_KEY",
        base_url_env: str = "OPENAI_BASE_URL",
    ) -> None:
        self.model = model
        self.api_key_env = api_key_env
        self.base_url_env = base_url_env
        self.tool_executor = ToolExecutor()
        self.session = session or AgentSession(
            tools=[tool.to_llm_format() for tool in get_tools()]
        )
        self.skills = load_skills(Path.cwd(), skills_dir) if enable_skills else {}

    def run_turn(self, user_input: str) -> Iterator[AgentEvent]:
        yield AgentEvent("agent_start", {})

        expanded_input = expand_skill_invocation(user_input, self.skills)

        if expanded_input != user_input:
            yield AgentEvent("skill_invoked", {
                "input": user_input,
                "expanded": expanded_input,
            })
        
        user_message = self.session.add_user_message(expanded_input)

        yield AgentEvent("message_start", {
            "role": "user",
        })
        yield AgentEvent("message_end", {
            "message": user_message,
        })

        turn = 1

        while True:
            yield AgentEvent("turn_start", {
                "turn": turn,
            })

            try:
                assistant_message = call_llm(
                    messages=self.session.messages,
                    tools=self.session.tools,
                    system_prompt=self.session.system_prompt,
                    model=self.model,
                    api_key_env=self.api_key_env,
                    base_url_env=self.base_url_env,
                )
            except Exception as exc:
                yield AgentEvent("error", {
                    "message": str(exc),
                })
                yield AgentEvent("agent_end", {})
                return

            saved_assistant_message = self.session.add_assistant_message(assistant_message)

            yield AgentEvent("message_start", {
                "role": "assistant",
            })
            yield AgentEvent("message_end", {
                "message": saved_assistant_message,
            })

            tool_calls = self.tool_executor.parse_tool_calls(assistant_message)

            if not tool_calls:
                yield AgentEvent("turn_end", {
                    "turn": turn,
                    "has_tool_calls": False,
                })
                yield AgentEvent("agent_end", {})
                return

            for tool_call in tool_calls:
                yield AgentEvent("tool_call_start", {
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                })

                result = self.tool_executor.execute(tool_call)
                tool_message = self.session.add_tool_message(result.to_message())

                yield AgentEvent("tool_call_end", {
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "content": result.content,
                    "is_error": result.is_error,
                    "message": tool_message,
                })

                yield AgentEvent("message_start", {
                    "role": "tool",
                })
                yield AgentEvent("message_end", {
                    "message": tool_message,
                })

            yield AgentEvent("turn_end", {
                "turn": turn,
                "has_tool_calls": True,
            })

            turn += 1