import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from src.llm.client import LLMClient
from src.tools.registry import ToolRegistry

@dataclass
class PlanStep:
    step_id: int
    step_type: str
    name: str
    step_input: str
    depends_on: list[int] = field(default_factory=list)
    
@dataclass
class Plan:
    user_input: str
    steps: list[PlanStep] = field(default_factory=list)
    raw_plan: str = ""
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_input": self.user_input,
            "success": self.success,
            "error": self.error,
            "steps": [asdict(step) for step in self.steps],
            "raw_plan": self.raw_plan,
        }
        
class Planner:
    def __init__(
        self,
        client: LLMClient,
        registry: ToolRegistry,
    ) -> None:
        self.client = client
        self.registry = registry
        
    def create_plan(self, user_input: str) -> Plan:
        """
        根据用户输入创建执行计划。
        """

        user_input = user_input.strip()

        if not user_input:
            return Plan(
                user_input=user_input,
                success=False,
                error="用户输入为空。",
            )

        prompt = self._build_planning_prompt(user_input)

        raw_plan = self.client.chat(
            user_message=prompt,
            system_prompt="你是一个任务规划器。你只输出 JSON，不要输出解释。",
            history=[],
        )

        try:
            steps = self._parse_steps(raw_plan)

            if not steps:
                return self._fallback_direct_llm_plan(
                    user_input=user_input,
                    raw_plan=raw_plan,
                    error="Planner 没有生成有效步骤。",
                )

            return Plan(
                user_input=user_input,
                steps=steps,
                raw_plan=raw_plan,
                success=True,
            )

        except Exception as e:
            return self._fallback_direct_llm_plan(
                user_input=user_input,
                raw_plan=raw_plan,
                error=str(e),
            )

    def _build_planning_prompt(self, user_input: str) -> str:
        """
        构造 Planner Prompt。
        """

        tools_text = self._format_tools()

        return f"""
你需要把用户请求拆解成执行计划。

当前可用工具：

{tools_text}

工具说明：

1. 如果用户需要计算，使用 calculator。
2. 如果用户需要读取项目文件，使用 file_reader。
3. 如果用户需要添加、查看、完成、删除任务，使用 todo。
4. 如果某一步需要理解、总结、改写、分析文本，使用 llm 步骤。
5. 不要执行任务，只生成计划。
6. 不要使用不存在的工具。

用户请求：

{user_input}

请严格输出 JSON，格式如下：

{{
  "steps": [
    {{
      "step_id": 1,
      "step_type": "tool",
      "name": "工具名",
      "step_input": "传给工具的输入",
      "depends_on": []
    }},
    {{
      "step_id": 2,
      "step_type": "llm",
      "name": "任务名",
      "step_input": "这一步要让大模型做什么，可以引用 step_1 的结果",
      "depends_on": [1]
    }}
  ]
}}

注意：

- step_type 只能是 "tool" 或 "llm"
- tool 步骤的 name 必须是已有工具名
- llm 步骤的 name 可以是 summarize、analyze、rewrite、direct_answer 等
- depends_on 表示依赖前面哪些步骤
- 如果用户只是普通问答，只生成一个 llm 步骤
- 只输出 JSON，不要输出 Markdown，不要输出解释
"""

    def _format_tools(self) -> str:
        """
        把工具列表格式化给 Planner 看。
        """

        tool_infos = self.registry.list_tools()

        if not tool_infos:
            return "当前没有可用工具。"

        lines = []

        for tool in tool_infos:
            name = tool.get("name", "")
            description = tool.get("description", "")
            lines.append(f"- {name}: {description}")

        return "\n".join(lines)

    def _parse_steps(self, raw_plan: str) -> list[PlanStep]:
        """
        从 LLM 输出中解析 PlanStep。
        """

        json_text = self._extract_json(raw_plan)
        data = json.loads(json_text)

        raw_steps = data.get("steps", [])

        steps: list[PlanStep] = []

        for item in raw_steps:
            step = PlanStep(
                step_id=int(item["step_id"]),
                step_type=str(item["step_type"]),
                name=str(item["name"]),
                step_input=str(item["step_input"]),
                depends_on=[
                    int(step_id)
                    for step_id in item.get("depends_on", [])
                ],
            )

            self._validate_step(step)
            steps.append(step)

        return steps

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        提取 JSON。

        兼容两种情况：
        1. LLM 直接输出 JSON
        2. LLM 输出 ```json ... ```
        """

        text = text.strip()

        fence_match = re.search(
            r"```(?:json)?\s*(.*?)```",
            text,
            re.DOTALL,
        )

        if fence_match:
            return fence_match.group(1).strip()

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("没有找到有效 JSON。")

        return text[start : end + 1]

    def _validate_step(self, step: PlanStep) -> None:
        """
        校验单个步骤是否合法。
        """

        if step.step_type not in {"tool", "llm"}:
            raise ValueError(f"不支持的 step_type: {step.step_type}")

        if step.step_id <= 0:
            raise ValueError("step_id 必须大于 0。")

        if not step.name:
            raise ValueError("步骤 name 不能为空。")

        if step.step_type == "tool":
            tool = self.registry.get_tool(step.name)

            if tool is None:
                raise ValueError(f"工具不存在: {step.name}")

    @staticmethod
    def _fallback_direct_llm_plan(
        user_input: str,
        raw_plan: str,
        error: str,
    ) -> Plan:
        """
        当 Planner 输出坏 JSON 时，退化成普通 LLM 回答计划。
        """

        return Plan(
            user_input=user_input,
            steps=[
                PlanStep(
                    step_id=1,
                    step_type="llm",
                    name="direct_answer",
                    step_input=user_input,
                    depends_on=[],
                )
            ],
            raw_plan=raw_plan,
            success=False,
            error=error,
        )