import json
from dataclasses import dataclass
from typing import Any

from src.llm.client import LLMClient
from src.memory.sqlite_memory import SQLiteChatMemory
from src.memory.summary_memory import (
    SummaryMemory,
    build_system_prompt,
    compress_memory_if_needed,
)
from src.tools.router import ToolRouter

@dataclass
class AgentResponse:
    answer: str
    used_tool: bool
    tool_name: str | None = None
    tool_input: str = ""
    route_reason: str = ""
    tool_success: bool = False
    tool_result: Any = None
    
class BasicAgent:
    def __init__(
        self,
        client: LLMClient,
        memory: SQLiteChatMemory,
        summary_memory: SummaryMemory,
        router: ToolRouter,
        max_history: int = 6,
    ) -> None:
        self.client = client
        self.memory = memory
        self.summary_memory = summary_memory
        self.router = router
        self.max_history = max_history
        
    def run(self, user_input: str) -> AgentResponse:
        user_input=user_input.strip()
        
        if not user_input:
            return AgentResponse(
                answer="请输入内容。",
                used_tool=False,
            )

        route, tool_result = self.router.run(user_input)

        if route.should_use_tool:
            response = self._answer_with_tool(
                user_input=user_input,
                route=route,
                tool_result=tool_result,
            )
        else:
            response = self._answer_without_tool(user_input=user_input)

        self._save_conversation(
            user_input=user_input,
            answer=response.answer,
        )

        self._compress_memory_if_needed()

        return response
    
    def _answer_without_tool(self, user_input: str) -> AgentResponse:
        
        system_prompt = build_system_prompt(self.summary_memory)
        recent_history = self.memory.get_recent_messages(max_messages=self.max_history)

        answer = self.client.chat(
            user_message=user_input,
            system_prompt=system_prompt,
            history=recent_history,
        )

        return AgentResponse(
            answer=answer,
            used_tool=False,
            route_reason="没有匹配到工具，直接调用 LLM。",
        )
        
    def _answer_with_tool(
        self,
        user_input: str,
        route,
        tool_result,
    ) -> AgentResponse:
        """
        使用工具后，再让大模型组织最终回答。
        """

        if not tool_result.success:
            answer = f"工具调用失败：{tool_result.error}"

            return AgentResponse(
                answer=answer,
                used_tool=True,
                tool_name=route.tool_name,
                tool_input=route.tool_input,
                route_reason=route.reason,
                tool_success=False,
                tool_result=tool_result.error,
            )

        tool_result_text = self._format_tool_result(tool_result.result)

        system_prompt = build_system_prompt(self.summary_memory)
        recent_history = self.memory.get_recent_messages(max_messages=self.max_history)

        agent_prompt = f"""
用户原始问题：
{user_input}

你已经调用了一个工具，工具信息如下：

工具名：
{route.tool_name}

工具输入：
{route.tool_input}

工具返回结果：
{tool_result_text}

请基于工具结果，给用户一个自然、清晰、简洁的回答。
不要编造工具结果中没有的信息。
"""

        answer = self.client.chat(
            user_message=agent_prompt,
            system_prompt=system_prompt,
            history=recent_history,
        )

        return AgentResponse(
            answer=answer,
            used_tool=True,
            tool_name=route.tool_name,
            tool_input=route.tool_input,
            route_reason=route.reason,
            tool_success=True,
            tool_result=tool_result.result,
        )
        
    
    def _save_conversation(self, user_input: str, answer: str) -> None:
        """
        保存本轮对话。
        """

        self.memory.add_message("user", user_input)
        self.memory.add_message("assistant", answer)

    def _compress_memory_if_needed(self) -> None:
        """
        如果短期历史太长，就压缩成长期摘要。
        """

        compress_memory_if_needed(
            memory=self.memory,
            summary_memory=self.summary_memory,
            client=self.client,
            trigger_count=14,
            keep_recent=6,
        )

    @staticmethod
    def _format_tool_result(result: Any) -> str:
        """
        把工具结果转成适合放进 prompt 的文本。
        """

        try:
            return json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        except TypeError:
            return str(result)