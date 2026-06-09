"""
Day30: Agent Stage Smoke Test

目标：
1. 测试当前 Agent 阶段核心能力是否能跑通
2. 测试普通问答
3. 测试工具调用
4. 测试多步任务
5. 为 README 和面试展示做准备

运行方式：
    python -m examples.day30_agent_smoke_test
"""

from src.agent.multistep_agent import MultiStepAgent
from src.config.settings import load_app_config
from src.llm.client import LLMClient
from src.memory.sqlite_memory import SQLiteChatMemory
from src.memory.summary_memory import SummaryMemory
from src.tools.registry import create_default_registry
from src.tools.router import ToolRouter


def create_agent() -> MultiStepAgent:
    config = load_app_config()
    client = LLMClient(config)

    memory = SQLiteChatMemory(
        db_path="data/day30_agent_smoke_test.db",
        session_id="day30",
    )

    summary_memory = SummaryMemory(
        file_path="data/day30_agent_summary.txt",
    )

    registry = create_default_registry()
    router = ToolRouter(registry)

    return MultiStepAgent(
        client=client,
        memory=memory,
        summary_memory=summary_memory,
        registry=registry,
        router=router,
        max_history=6,
    )


def print_case_title(index: int, title: str) -> None:
    print("\n" + "=" * 70)
    print(f"Case {index}: {title}")
    print("=" * 70)


def print_steps(response) -> None:
    print("\n--- Steps ---")

    for index, step in enumerate(response.steps, start=1):
        print(f"\nStep {index}")
        print(f"type: {step.step_type}")
        print(f"name: {step.name}")
        print(f"input: {step.step_input}")
        print(f"success: {step.success}")

        if step.error:
            print(f"error: {step.error}")
        else:
            observation = str(step.observation)
            print(f"observation preview: {observation[:500]}")


def run_smoke_tests() -> None:
    agent = create_agent()

    test_cases = [
        {
            "title": "Calculator Tool",
            "input": "帮我算一下 123 * 456",
        },
        {
            "title": "Todo Tool",
            "input": "添加任务 Day30 整理 Agent 阶段总结",
        },
        {
            "title": "File Summary Multi-Step",
            "input": "帮我读取 README.md 并总结主要内容",
        },
        {
            "title": "Direct LLM Answer",
            "input": "什么是 Agent？用简单的话解释。",
        },
    ]

    try:
        agent.memory.clear()
        agent.summary_memory.clear()

        for index, case in enumerate(test_cases, start=1):
            print_case_title(index, case["title"])

            user_input = case["input"]
            print("User:", user_input)

            response = agent.run(user_input)

            print("\nAgent Answer:")
            print(response.answer)

            print(f"\nused_tools: {response.used_tools}")
            print_steps(response)

        print("\n" + "=" * 70)
        print("Day30 Agent Smoke Test 完成")
        print("=" * 70)

    finally:
        agent.memory.close()


def main() -> None:
    run_smoke_tests()


if __name__ == "__main__":
    main()