"""
Day31: Planner Demo

目标：
1. 输入用户请求
2. Planner 生成执行计划
3. 只展示计划，不执行

运行方式：
    python -m examples.day31_planner_demo
"""

import json

from src.agent.planner import Planner
from src.config.settings import load_app_config
from src.llm.client import LLMClient
from src.tools.registry import create_default_registry


def create_planner() -> Planner:
    config = load_app_config()
    client = LLMClient(config)
    registry = create_default_registry()

    return Planner(
        client=client,
        registry=registry,
    )


def print_plan(plan) -> None:
    print("\n========== Planner Result ==========")

    print(f"success: {plan.success}")

    if plan.error:
        print(f"error: {plan.error}")

    print("\n--- Steps ---")

    for step in plan.steps:
        print(f"\nStep {step.step_id}")
        print(f"type: {step.step_type}")
        print(f"name: {step.name}")
        print(f"input: {step.step_input}")
        print(f"depends_on: {step.depends_on}")

    print("\n--- Raw Plan ---")
    print(plan.raw_plan)

    print("\n--- Plan Dict ---")
    print(
        json.dumps(
            plan.to_dict(),
            ensure_ascii=False,
            indent=2,
        )
    )


def run_examples() -> None:
    planner = create_planner()

    examples = [
        "帮我算一下 123 * 456",
        "读取 README.md 并总结主要内容",
        "读取 docs/learning_log.md，提取后续要做的任务",
        "添加任务 明天复习 Planner 和 Executor",
        "什么是 RAG？用简单的话解释",
    ]

    for index, user_input in enumerate(examples, start=1):
        print("\n" + "=" * 70)
        print(f"Example {index}")
        print("=" * 70)
        print("User:", user_input)

        plan = planner.create_plan(user_input)

        print_plan(plan)


def interactive_demo() -> None:
    planner = create_planner()

    print("========== Day31: Planner Demo ==========")
    print("输入 q 退出")
    print("-----------------------------------------")
    print("示例：")
    print("读取 README.md 并总结主要内容")
    print("读取 docs/learning_log.md，提取后续要做的任务")
    print("帮我算一下 123 * 456，然后把结果添加成任务")
    print("什么是 Agent？")
    print("-----------------------------------------")

    while True:
        user_input = input("\n你：").strip()

        if user_input.lower() == "q":
            print("已退出 Planner Demo。")
            break

        if not user_input:
            print("请输入内容。")
            continue

        plan = planner.create_plan(user_input)

        print_plan(plan)


def main() -> None:
    run_examples()

    print("\n是否进入交互模式？")
    choice = input("输入 y 进入，其他任意键退出：").strip().lower()

    if choice == "y":
        interactive_demo()


if __name__ == "__main__":
    main()