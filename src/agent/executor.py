import json
from dataclasses import asdict, dataclass, field
from typing import Any

from src.agent.planner import Plan, PlanStep
from src.llm.client import LLMClient
from src.tools.calculator import ToolResult
from src.tools.registry import ToolRegistry

@dataclass
class StepExecutionResult:
    step_id:int
    step_type:str
    name:str
    step_input:str
    success:bool
    output:Any=None
    error:str|None=None
    
@dataclass
class ExecutionResult:
    success:bool
    user_input:str
    final_answer:str
    step_results:list[StepExecutionResult]=field(default_factory=list)
    error:str|None=None
    
    def to_dict(self)->dict[str,Any]:
        return{
            "success": self.success,
            "user_input": self.user_input,
            "final_answer": self.final_answer,
            "error": self.error,
            "step_results": [
                asdict(step_result)
                for step_result in self.step_results
            ],
        }
        
class Executor:
    def __init__(
        self,
        client:LLMClient,
        registry:ToolRegistry,
    )->None:
        self.client=client
        self.registry=registry
        
    def execute(self,plan:Plan)->ExecutionResult:
        if not plan.steps:
            return ExecutionResult(
                success=False,
                user_input=plan.user_input,
                final_answer="执行失败：计划中没有步骤。",
                error="计划中没有步骤。",
            )
        
        step_outputs:dict[int,Any]={}
        step_results:list[StepExecutionResult]=[]
        
        for step in plan.steps:
            result=self._execute_step(
                step=step,
                plan=plan,
                step_outputs=step_outputs,
            )
            
            step_results.append(result)
            
            if not result.success:
                return ExecutionResult(
                    success=False,
                    user_input=plan.user_input,
                    final_answer=f"执行失败:Step {step.step_id} 出错：{result.error}",
                    step_results=step_results,
                    error=result.error,
                )
                
            step_outputs[step.step_id]=result.output
            
        final_answer=self._build_final_answer(
            plan=plan,
            step_results=step_results,
        )
        
        return ExecutionResult(
            success=True,
            user_input=plan.user_input,
            final_answer=final_answer,
            step_results=step_results,
        )
        
    def _execute_step(
        self,
        step: PlanStep,
        plan: Plan,
        step_outputs: dict[int, Any],
    ) -> StepExecutionResult:
        
        if step.step_type == "tool":
            return self._execute_tool_step(
                step=step,
                plan=plan,
                step_outputs=step_outputs,
            )

        if step.step_type == "llm":
            return self._execute_llm_step(
                step=step,
                plan=plan,
                step_outputs=step_outputs,
            )

        return StepExecutionResult(
            step_id=step.step_id,
            step_type=step.step_type,
            name=step.name,
            step_input=step.step_input,
            success=False,
            error=f"不支持的 step_type: {step.step_type}",
        )
        
    def _execute_tool_step(
        self,
        step: PlanStep,
        plan: Plan,
        step_outputs: dict[int, Any],
    ) -> StepExecutionResult:
        """
        执行工具步骤。
        """

        tool_input = self._prepare_tool_input(
            step=step,
            plan=plan,
            step_outputs=step_outputs,
        )

        tool_result = self.registry.run_tool(
            name=step.name,
            tool_input=tool_input,
        )

        if not tool_result.success:
            return StepExecutionResult(
                step_id=step.step_id,
                step_type=step.step_type,
                name=step.name,
                step_input=tool_input,
                success=False,
                error=tool_result.error,
            )

        return StepExecutionResult(
            step_id=step.step_id,
            step_type=step.step_type,
            name=step.name,
            step_input=tool_input,
            success=True,
            output=tool_result.result,
        )

    def _execute_llm_step(
        self,
        step: PlanStep,
        plan: Plan,
        step_outputs: dict[int, Any],
    ) -> StepExecutionResult:
        """
        执行 LLM 步骤。
        """

        prompt = self._build_llm_step_prompt(
            step=step,
            plan=plan,
            step_outputs=step_outputs,
        )

        try:
            output = self.client.chat(
                user_message=prompt,
                system_prompt="你是一个执行器，负责根据已有步骤结果完成当前步骤。",
                history=[],
            )

            return StepExecutionResult(
                step_id=step.step_id,
                step_type=step.step_type,
                name=step.name,
                step_input=step.step_input,
                success=True,
                output=output,
            )

        except Exception as e:
            return StepExecutionResult(
                step_id=step.step_id,
                step_type=step.step_type,
                name=step.name,
                step_input=step.step_input,
                success=False,
                error=str(e),
            )

    def _prepare_tool_input(
        self,
        step: PlanStep,
        plan: Plan,
        step_outputs: dict[int, Any],
    ) -> str:
        """
        准备工具输入。

        如果这个工具步骤不依赖前置结果，直接使用 step.step_input。

        如果依赖前置结果，则让 LLM 根据前置结果生成真正传给工具的输入。
        """

        if not step.depends_on:
            return step.step_input

        dependency_text = self._format_dependencies(
            depends_on=step.depends_on,
            step_outputs=step_outputs,
        )

        prompt = f"""
用户原始请求：
{plan.user_input}

当前要执行的工具：
{step.name}

当前步骤说明：
{step.step_input}

当前步骤依赖的前置结果：
{dependency_text}

请生成真正传给工具 {step.name} 的输入。

要求：
1. 只输出工具输入内容
2. 不要解释
3. 不要使用 Markdown
4. 如果是 todo 工具，添加任务时格式使用：add 任务内容
5. 如果是 calculator 工具，只输出数学表达式
6. 如果是 file_reader 工具，只输出文件路径
"""

        tool_input = self.client.chat(
            user_message=prompt,
            system_prompt="你负责把计划步骤转换成具体工具输入。只输出工具输入。",
            history=[],
        )

        return tool_input.strip()

    def _build_llm_step_prompt(
        self,
        step: PlanStep,
        plan: Plan,
        step_outputs: dict[int, Any],
    ) -> str:
        """
        构造 LLM 步骤的 prompt。
        """

        dependency_text = self._format_dependencies(
            depends_on=step.depends_on,
            step_outputs=step_outputs,
        )

        return f"""
用户原始请求：
{plan.user_input}

当前步骤：
Step {step.step_id}
名称：{step.name}
任务：{step.step_input}

当前步骤依赖的前置结果：
{dependency_text}

请完成当前步骤。

要求：
1. 用中文回答
2. 只完成当前步骤，不要编造前置结果里没有的信息
3. 如果是总结任务，请基于前置结果总结
4. 如果是提取任务，请尽量结构化输出
"""

    def _build_final_answer(
        self,
        plan: Plan,
        step_results: list[StepExecutionResult],
    ) -> str:
        """
        根据所有步骤结果生成最终回答。
        """

        last_result = step_results[-1]

        if last_result.output is None:
            return "计划执行完成，但最后一步没有输出。"

        if isinstance(last_result.output, str):
            return last_result.output

        return self._format_data(last_result.output)

    def _format_dependencies(
        self,
        depends_on: list[int],
        step_outputs: dict[int, Any],
    ) -> str:
        """
        格式化依赖步骤的输出。
        """

        if not depends_on:
            return "无前置依赖。"

        lines = []

        for step_id in depends_on:
            output = step_outputs.get(step_id)

            lines.append(f"Step {step_id} 输出：")
            lines.append(self._format_data(output))

        return "\n".join(lines)

    @staticmethod
    def _format_data(data: Any) -> str:
        """
        把任意数据格式化成字符串。
        """

        try:
            return json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        except TypeError:
            return str(data)