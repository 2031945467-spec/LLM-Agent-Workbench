"""
Multi-Step Agent

作用：
1. 支持简单多步任务执行
2. 当前重点支持：读取文件 -> 总结文件内容
3. 为后续 Planner / Executor 做准备
"""

import json
import re
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
from src.tools.registry import ToolRegistry
from src.tools.router import ToolRouter


@dataclass
class MultiStep:
    """
    多步任务中的单个步骤。

    step_type:
        tool 表示调用工具
        llm 表示调用大模型处理结果

    name:
        工具名或 LLM 步骤名

    step_input:
        传给工具或 LLM 的输入

    observation:
        这一步执行后的结果
    """

    step_type: str
    name: str
    step_input: str
    success: bool = False
    observation: Any = None
    error: str | None = None


@dataclass
class MultiStepResponse:
    """
    MultiStepAgent 最终返回结果。
    """

    answer: str
    steps: list[MultiStep] = field(default_factory=list)
    used_tools: bool = False


class MultiStepAgent:
    """
    多步 Agent。

    当前支持两种模式：

    1. 多步任务：
       用户：帮我读取 README.md 并总结主要内容
       步骤：
           Step 1: file_reader 读取文件
           Step 2: LLM 总结文件内容

    2. 普通任务：
       交给 ToolRouter 做单步工具调用或直接 LLM 回答
    """

    def __init__(
        self,
        client: LLMClient,
        memory: SQLiteChatMemory,
        summary_memory: SummaryMemory,
        registry: ToolRegistry,
        router: ToolRouter,
        max_history: int = 6,
    ) -> None:
        self.client = client
        self.memory = memory
        self.summary_memory = summary_memory
        self.registry = registry
        self.router = router
        self.max_history = max_history

    def run(self, user_input: str) -> MultiStepResponse:
        user_input = user_input.strip()

        if not user_input:
            return MultiStepResponse(
                answer="请输入内容。",
                used_tools=False,
            )

        if self._is_file_summary_task(user_input):
            response = self._run_file_summary_task(user_input)
        else:
            response = self._run_single_step_task(user_input)

        self._save_conversation(user_input, response.answer)
        self._compress_memory_if_needed()

        return response

    def _is_file_summary_task(self, text: str) -> bool:
        """
        判断是否是“读取文件并总结”的多步任务。
        """

        has_file = bool(self._extract_file_path(text))

        summary_keywords = [
            "总结",
            "概括",
            "提炼",
            "主要内容",
            "讲一下文件",
            "分析文件",
        ]

        has_summary_intent = any(keyword in text for keyword in summary_keywords)

        return has_file and has_summary_intent

    def _run_file_summary_task(self, user_input: str) -> MultiStepResponse:
        """
        执行多步任务：读取文件 -> 总结文件。
        """

        steps: list[MultiStep] = []

        file_path = self._extract_file_path(user_input)

        if not file_path:
            return MultiStepResponse(
                answer="我没有找到要读取的文件路径。",
                used_tools=False,
            )

        # Step 1：调用 file_reader
        read_step = MultiStep(
            step_type="tool",
            name="file_reader",
            step_input=file_path,
        )

        tool_result = self.registry.run_tool(
            name="file_reader",
            tool_input=file_path,
        )

        read_step.success = tool_result.success

        if not tool_result.success:
            read_step.error = tool_result.error
            steps.append(read_step)

            return MultiStepResponse(
                answer=f"读取文件失败：{tool_result.error}",
                steps=steps,
                used_tools=True,
            )

        read_step.observation = tool_result.result
        steps.append(read_step)

        # Step 2：调用 LLM 总结文件内容
        summary_step = MultiStep(
            step_type="llm",
            name="summarize_file",
            step_input="根据读取到的文件内容进行总结。",
        )

        answer = self._summarize_file_content(
            user_input=user_input,
            file_data=tool_result.result,
        )

        summary_step.success = True
        summary_step.observation = answer
        steps.append(summary_step)

        return MultiStepResponse(
            answer=answer,
            steps=steps,
            used_tools=True,
        )

    def _run_single_step_task(self, user_input: str) -> MultiStepResponse:
        """
        普通单步任务：

        1. Router 判断是否需要工具
        2. 如果需要工具，调用工具后让 LLM 整理回答
        3. 如果不需要工具，直接 LLM 回答
        """

        steps: list[MultiStep] = []

        route, tool_result = self.router.run(user_input)

        if not route.should_use_tool or not route.tool_name:
            answer = self._ask_llm(user_input)

            return MultiStepResponse(
                answer=answer,
                steps=[
                    MultiStep(
                        step_type="llm",
                        name="direct_answer",
                        step_input=user_input,
                        success=True,
                        observation=answer,
                    )
                ],
                used_tools=False,
            )

        tool_step = MultiStep(
            step_type="tool",
            name=route.tool_name,
            step_input=route.tool_input,
            success=tool_result.success,
            observation=tool_result.result if tool_result.success else None,
            error=tool_result.error if not tool_result.success else None,
        )
        steps.append(tool_step)

        if not tool_result.success:
            return MultiStepResponse(
                answer=f"工具调用失败：{tool_result.error}",
                steps=steps,
                used_tools=True,
            )

        answer = self._answer_with_tool_result(
            user_input=user_input,
            tool_name=route.tool_name,
            tool_input=route.tool_input,
            tool_result=tool_result,
        )

        llm_step = MultiStep(
            step_type="llm",
            name="final_answer",
            step_input="基于工具结果生成最终回答。",
            success=True,
            observation=answer,
        )
        steps.append(llm_step)

        return MultiStepResponse(
            answer=answer,
            steps=steps,
            used_tools=True,
        )

    def _summarize_file_content(
        self,
        user_input: str,
        file_data: Any,
    ) -> str:
        """
        根据文件内容生成总结。
        """

        path = file_data.get("path", "")
        content = file_data.get("content", "")
        size = file_data.get("size", 0)

        # 简单限制，避免一次性塞太长内容
        content_preview = content[:4000]

        prompt = f"""
用户请求：
{user_input}

已读取文件：
{path}

文件大小：
{size} bytes

文件内容如下：
{content_preview}

请总结这个文件的主要内容。

要求：
1. 用中文回答
2. 先概括文件用途
3. 再列出核心内容
4. 如果文件是项目 README，请重点说明项目功能、运行方式和当前进度
5. 不要编造文件中没有的信息
"""

        return self._ask_llm(prompt)

    def _answer_with_tool_result(
        self,
        user_input: str,
        tool_name: str,
        tool_input: str,
        tool_result: ToolResult,
    ) -> str:
        """
        基于工具结果生成自然语言回答。
        """

        tool_result_text = self._format_data(tool_result.result)

        prompt = f"""
用户原始问题：
{user_input}

工具名：
{tool_name}

工具输入：
{tool_input}

工具返回结果：
{tool_result_text}

请基于工具结果，给用户一个自然、清晰、简洁的回答。
不要编造工具结果中没有的信息。
"""

        return self._ask_llm(prompt)

    def _ask_llm(self, user_message: str) -> str:
        """
        调用 LLM。
        """

        system_prompt = build_system_prompt(self.summary_memory)
        recent_history = self.memory.get_recent_messages(max_messages=self.max_history)

        return self.client.chat(
            user_message=user_message,
            system_prompt=system_prompt,
            history=recent_history,
        )

    def _save_conversation(self, user_input: str, answer: str) -> None:
        self.memory.add_message("user", user_input)
        self.memory.add_message("assistant", answer)

    def _compress_memory_if_needed(self) -> None:
        compress_memory_if_needed(
            memory=self.memory,
            summary_memory=self.summary_memory,
            client=self.client,
            trigger_count=14,
            keep_recent=6,
        )

    @staticmethod
    def _extract_file_path(text: str) -> str:
        """
        从用户输入中提取文件路径。
        """

        pattern = r"[\w./\\-]+\.(?:md|txt|json|py|csv)"
        match = re.search(pattern, text)

        if not match:
            return ""

        return match.group(0)

    @staticmethod
    def _format_data(data: Any) -> str:
        try:
            return json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        except TypeError:
            return str(data)