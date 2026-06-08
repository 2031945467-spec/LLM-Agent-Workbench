"""
Day29: Multi-Step Agent Demo

运行方式：
    python -m examples.day29_multistep_agent_demo
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
        db_path="data/day29_multistep_agent.db",
        session_id="day29",
    )

    summary_memory = SummaryMemory(
        file_path="data/day29_multistep_agent_summary.txt",
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


def print_steps(response) -> None:
    print("\n========== Multi-Step Trace ==========")

    for index, step in enumerate(response.steps, start=1):
        print(f"\nStep {index}")
        print(f"Type: {step.step_type}")
        print(f"Name: {step.name}")
        print(f"Input: {step.step_input}")
        print(f"Success: {step.success}")

        if step.error:
            print(f"Error: {step.error}")
        else:
            observation = str(step.observation)
            print(f"Observation: {observation[:800]}")


def interactive_agent() -> None:
    agent = create_agent()

    show_trace = True

    print("========== Day29: Multi-Step Agent ==========")
    print("输入 q 退出")
    print("输入 history 查看短期记忆")
    print("输入 summary 查看长期摘要")
    print("输入 clear 清空记忆")
    print("输入 tools 查看工具")
    print("输入 trace on / trace off 开关 Trace")
    print("---------------------------------------------")
    print("示例：")
    print("帮我读取 README.md 并总结主要内容")
    print("请打开 docs/learning_log.md 并概括一下")
    print("帮我算一下 123 * 456")
    print("添加任务 明天复习 RAG")
    print("什么是 Multi-Step Agent？")
    print("---------------------------------------------")

    try:
        while True:
            user_input = input("\n你：").strip()

            if user_input.lower() == "q":
                print("已退出 Multi-Step Agent。")
                break

            if user_input.lower() == "history":
                agent.memory.show()
                continue

            if user_input.lower() == "summary":
                agent.summary_memory.show()
                continue

            if user_input.lower() == "clear":
                agent.memory.clear()
                agent.summary_memory.clear()
                print("记忆已清空。")
                continue

            if user_input.lower() == "tools":
                for tool_info in agent.registry.list_tools():
                    print(f"- {tool_info['name']}: {tool_info['description']}")
                continue

            if user_input.lower() == "trace on":
                show_trace = True
                print("已开启 Trace 显示。")
                continue

            if user_input.lower() == "trace off":
                show_trace = False
                print("已关闭 Trace 显示。")
                continue

            response = agent.run(user_input)

            print("\nAgent：")
            print(response.answer)

            print(f"\n是否使用工具：{response.used_tools}")

            if show_trace:
                print_steps(response)

    finally:
        agent.memory.close()


def main() -> None:
    interactive_agent()


if __name__ == "__main__":
    main()