"""
Day32: Executor Demo

目标：
1. Planner 生成计划
2. Executor 执行计划
3. 打印每一步执行结果

运行方式：
    python -m examples.day32_executor_demo
"""

import json

from src.agent.executor import Executor
from src.agent.planner import Planner
from src.config.settings import load_app_config
from src.llm.client import LLMClient
from src.tools.registry import create_default_registry


def create_planner_and_executor():
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

    return planner, executor


def print_plan(plan) -> None:
    print("\n========== Plan ==========")

    for step in plan.steps:
        print(f"\nStep {step.step_id}")
        print(f"type: {step.step_type}")
        print(f"name: {step.name}")
        print(f"input: {step.step_input}")
        print(f"depends_on: {step.depends_on}")

    if plan.error:
        print("\nPlanner error:", plan.error)


def print_execution_result(result) -> None:
    print("\n========== Execution Result ==========")
    print("success:", result.success)

    if result.error:
        print("error:", result.error)

    print("\n--- Step Results ---")

    for step_result in result.step_results:
        print(f"\nStep {step_result.step_id}")
        print(f"type: {step_result.step_type}")
        print(f"name: {step_result.name}")
        print(f"input: {step_result.step_input}")
        print(f"success: {step_result.success}")

        if step_result.error:
            print(f"error: {step_result.error}")
        else:
            output = str(step_result.output)
            print(f"output preview: {output[:800]}")

    print("\n--- Final Answer ---")
    print(result.final_answer)

    print("\n--- Result Dict ---")
    print(
        json.dumps(
            result.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


def run_examples() -> None:
    planner, executor = create_planner_and_executor()

    examples = [
        "帮我算一下 123 * 456",
        "读取 README.md 并总结主要内容",
        "什么是 Executor？用简单的话解释",
    ]

    for index, user_input in enumerate(examples, start=1):
        print("\n" + "=" * 70)
        print(f"Example {index}")
        print("=" * 70)

        print("User:", user_input)

        plan = planner.create_plan(user_input)
        print_plan(plan)

        result = executor.execute(plan)
        print_execution_result(result)


def interactive_demo() -> None:
    planner, executor = create_planner_and_executor()

    print("========== Day32: Executor Demo ==========")
    print("输入 q 退出")
    print("------------------------------------------")
    print("示例：")
    print("帮我算一下 123 * 456")
    print("读取 README.md 并总结主要内容")
    print("读取 docs/learning_log.md，提取后续要做的任务")
    print("什么是 Planner 和 Executor？")
    print("------------------------------------------")

    while True:
        user_input = input("\n你：").strip()

        if user_input.lower() == "q":
            print("已退出 Executor Demo。")
            break

        if not user_input:
            print("请输入内容。")
            continue

        plan = planner.create_plan(user_input)
        print_plan(plan)

        result = executor.execute(plan)
        print_execution_result(result)


def main() -> None:
    run_examples()

    print("\n是否进入交互模式？")
    choice = input("输入 y 进入，其他任意键退出：").strip().lower()

    if choice == "y":
        interactive_demo()


if __name__ == "__main__":
    main()