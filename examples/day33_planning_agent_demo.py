"""
Day33: PlanningAgent Demo

运行方式：
    python -m examples.day33_planning_agent_demo
"""

from src.agent.executor import Executor
from src.agent.planner import Planner
from src.agent.planning_agent import PlanningAgent
from src.config.settings import load_app_config
from src.llm.client import LLMClient
from src.memory.sqlite_memory import SQLiteChatMemory
from src.tools.registry import create_default_registry


def create_agent() -> PlanningAgent:
    """
    创建 PlanningAgent 及其依赖对象。
    """

    config = load_app_config()
    client = LLMClient(config)

    registry = create_default_registry()

    planner = Planner(
        client=client,
        registry=registry,
    )

    executor = Executor(
        client=client,
        registry=registry,
    )

    memory = SQLiteChatMemory(
        db_path="data/day33_planning_agent.db",
        session_id="day33",
    )

    return PlanningAgent(
        planner=planner,
        executor=executor,
        memory=memory,
    )


def print_plan(response) -> None:
    """
    打印 Planner 生成的计划。
    """

    if response.plan is None:
        return

    print("\n========== Plan ==========")

    if response.plan.error:
        print("Planner 提示：", response.plan.error)

    for step in response.plan.steps:
        print(f"\nStep {step.step_id}")
        print(f"type: {step.step_type}")
        print(f"name: {step.name}")
        print(f"input: {step.step_input}")
        print(f"depends_on: {step.depends_on}")


def print_execution(response) -> None:
    """
    打印 Executor 的执行结果。
    """

    if response.execution is None:
        return

    print("\n========== Execution ==========")

    for result in response.execution.step_results:
        print(f"\nStep {result.step_id}")
        print(f"name: {result.name}")
        print(f"success: {result.success}")
        print(f"input: {result.step_input}")

        if result.error:
            print(f"error: {result.error}")
        else:
            output = str(result.output)
            print(f"output: {output[:500]}")


def interactive_demo() -> None:
    agent = create_agent()
    show_trace = True

    print("========== Day33: PlanningAgent ==========")
    print("输入 q 退出")
    print("输入 history 查看对话历史")
    print("输入 clear 清空历史")
    print("输入 trace on 开启执行过程显示")
    print("输入 trace off 关闭执行过程显示")
    print("------------------------------------------")
    print("示例：")
    print("帮我算一下 123 * 456")
    print("读取 README.md 并总结主要内容")
    print("添加任务 明天学习基础 RAG")
    print("什么是 Planner 和 Executor？")
    print("------------------------------------------")

    try:
        while True:
            user_input = input("\n你：").strip()

            if user_input.lower() == "q":
                print("已退出 PlanningAgent。")
                break

            if user_input.lower() == "history":
                agent.memory.show()
                continue

            if user_input.lower() == "clear":
                agent.memory.clear()
                print("对话历史已清空。")
                continue

            if user_input.lower() == "trace on":
                show_trace = True
                print("已开启执行过程显示。")
                continue

            if user_input.lower() == "trace off":
                show_trace = False
                print("已关闭执行过程显示。")
                continue

            if not user_input:
                print("请输入内容。")
                continue

            response = agent.run(user_input)

            print("\nAgent：")
            print(response.answer)

            print(f"\n执行是否成功：{response.success}")

            if response.error:
                print(f"错误信息：{response.error}")

            if show_trace:
                print_plan(response)
                print_execution(response)

    finally:
        agent.memory.close()


def main() -> None:
    interactive_demo()


if __name__ == "__main__":
    main()