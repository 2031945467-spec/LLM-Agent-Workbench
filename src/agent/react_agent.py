import json
from dataclasses import dataclass, field
from typing import Any

from src.llm.client import LLMClient
from src.memory.sqlite_memory import SQLiteChatMemory
from src.memory.summary_memory import (
    SummaryMemory,
    build_system_prompt,
    compress_memory_if_needed,
)
from src.tools.calculator import ToolResult
from src.tools.router import ToolRouter

@dataclass
class ReActStep:
    thought: str
    action: str | None = None
    action_input: str = ""
    observation: str = ""
    
@dataclass
class ReActResponse:
    answer: str
    used_tool: bool
    steps: list[ReActStep] = field(default_factory=list)
    tool_success: bool = False
    tool_result: Any = None
    
class ReActAgent:
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
        
    def run(self, user_input: str) -> ReActResponse:
        """
        ReAct Agent 统一入口。
        """

        user_input = user_input.strip()

        if not user_input:
            return ReActResponse(
                answer="请输入内容。",
                used_tool=False,
            )

        steps: list[ReActStep] = []

        route = self.router.route(user_input)

        if not route.should_use_tool or not route.tool_name:
            step = ReActStep(
                thought="没有匹配到合适工具，直接使用大模型回答。",
                action=None,
                action_input="",
                observation="未调用工具。",
            )
            steps.append(step)

            answer = self._answer_without_tool(user_input)

            self._save_conversation(user_input, answer)
            self._compress_memory_if_needed()

            return ReActResponse(
                answer=answer,
                used_tool=False,
                steps=steps,
            )

        thought = f"用户问题需要调用工具。路由原因：{route.reason}"
        action = route.tool_name
        action_input = route.tool_input

        tool_result = self.router.registry.run_tool(
            name=route.tool_name,
            tool_input=route.tool_input,
        )

        observation = self._format_observation(tool_result)

        step = ReActStep(
            thought=thought,
            action=action,
            action_input=action_input,
            observation=observation,
        )
        steps.append(step)

        if not tool_result.success:
            answer = f"工具调用失败：{tool_result.error}"

            self._save_conversation(user_input, answer)
            self._compress_memory_if_needed()

            return ReActResponse(
                answer=answer,
                used_tool=True,
                steps=steps,
                tool_success=False,
                tool_result=tool_result.error,
            )

        answer = self._answer_with_observation(
            user_input=user_input,
            step=step,
            tool_result=tool_result,
        )

        self._save_conversation(user_input, answer)
        self._compress_memory_if_needed()

        return ReActResponse(
            answer=answer,
            used_tool=True,
            steps=steps,
            tool_success=True,
            tool_result=tool_result.result,
        )

    def _answer_without_tool(self, user_input: str) -> str:
        """
        不使用工具，直接调用 LLM。
        """

        system_prompt = build_system_prompt(self.summary_memory)
        recent_history = self.memory.get_recent_messages(max_messages=self.max_history)

        return self.client.chat(
            user_message=user_input,
            system_prompt=system_prompt,
            history=recent_history,
        )

    def _answer_with_observation(
        self,
        user_input: str,
        step: ReActStep,
        tool_result: ToolResult,
    ) -> str:
        """
        基于工具观察结果，让 LLM 生成最终回答。
        """

        system_prompt = build_system_prompt(self.summary_memory)
        recent_history = self.memory.get_recent_messages(max_messages=self.max_history)

        prompt = f"""
你是一个 ReAct Agent。

用户原始问题：
{user_input}

本轮 ReAct 过程如下：

Thought:
{step.thought}

Action:
{step.action}

Action Input:
{step.action_input}

Observation:
{step.observation}

请你基于 Observation 给用户一个自然、清晰、简洁的最终回答。

要求：
1. 不要编造 Observation 里没有的信息
2. 如果是计算结果，直接给出结果并简单说明
3. 如果是文件内容，基于读取到的内容回答
4. 如果是 Todo 操作，说明任务操作结果
"""

        return self.client.chat(
            user_message=prompt,
            system_prompt=system_prompt,
            history=recent_history,
        )

    def _save_conversation(self, user_input: str, answer: str) -> None:
        """
        保存对话。
        """

        self.memory.add_message("user", user_input)
        self.memory.add_message("assistant", answer)

    def _compress_memory_if_needed(self) -> None:
        """
        压缩长期记忆。
        """

        compress_memory_if_needed(
            memory=self.memory,
            summary_memory=self.summary_memory,
            client=self.client,
            trigger_count=14,
            keep_recent=6,
        )

    @staticmethod
    def _format_observation(tool_result: ToolResult) -> str:
        """
        把工具结果格式化为 Observation 文本。
        """

        if not tool_result.success:
            return f"工具执行失败：{tool_result.error}"

        try:
            return json.dumps(
                tool_result.result,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        except TypeError:
            return str(tool_result.result)