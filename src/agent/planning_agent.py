"""
Planning Agent

作用：
1. 接收用户输入
2. 使用 Planner 生成执行计划
3. 使用 Executor 执行计划
4. 保存用户输入和最终回答
"""

from dataclasses import dataclass

from src.agent.executor import ExecutionResult, Executor
from src.agent.planner import Plan, Planner
from src.memory.sqlite_memory import SQLiteChatMemory


@dataclass
class PlanningAgentResponse:
    """
    PlanningAgent 的统一返回结果。
    """

    answer: str
    success: bool
    plan: Plan | None = None
    execution: ExecutionResult | None = None
    error: str | None = None


class PlanningAgent:
    """
    负责串联 Planner、Executor 和 Memory。
    """

    def __init__(
        self,
        planner: Planner,
        executor: Executor,
        memory: SQLiteChatMemory,
    ) -> None:
        self.planner = planner
        self.executor = executor
        self.memory = memory

    def run(self, user_input: str) -> PlanningAgentResponse:
        """
        执行一次完整的 Planning Agent 流程。
        """

        user_input = user_input.strip()

        if not user_input:
            return PlanningAgentResponse(
                answer="请输入内容。",
                success=False,
                error="用户输入为空。",
            )

        try:
            # 第一步：Planner 生成计划
            plan = self.planner.create_plan(user_input)

            if not plan.steps:
                return PlanningAgentResponse(
                    answer="没有生成可执行的计划。",
                    success=False,
                    plan=plan,
                    error=plan.error or "计划为空。",
                )

            # 第二步：Executor 执行计划
            execution = self.executor.execute(plan)

            answer = execution.final_answer

            # 第三步：保存对话
            self.memory.add_message(
                role="user",
                content=user_input,
            )

            self.memory.add_message(
                role="assistant",
                content=answer,
            )

            return PlanningAgentResponse(
                answer=answer,
                success=execution.success,
                plan=plan,
                execution=execution,
                error=execution.error,
            )

        except Exception as e:
            return PlanningAgentResponse(
                answer=f"Agent 执行失败：{e}",
                success=False,
                error=str(e),
            )