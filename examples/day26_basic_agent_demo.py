"""
Day26: Basic Agent Demo

运行方式：
    python -m examples.day26_basic_agent_demo
"""

from src.agent.basic_agent import BasicAgent
from src.config.settings import load_app_config
from src.llm.client import LLMClient
from src.memory.sqlite_memory import SQLiteChatMemory
from src.memory.summary_memory import SummaryMemory
from src.tools.registry import create_default_registry
from src.tools.router import ToolRouter


def create_agent() -> BasicAgent:
    config = load_app_config()
    client = LLMClient(config)

    memory = SQLiteChatMemory(
        db_path="data/day26_basic_agent.db",
        session_id="day26",
    )

    summary_memory = SummaryMemory(
        file_path="data/day26_basic_agent_summary.txt",
    )

    registry = create_default_registry()
    router = ToolRouter(registry)

    agent = BasicAgent(
        client=client,
        memory=memory,
        summary_memory=summary_memory,
        router=router,
        max_history=6,
    )

    return agent


def interactive_agent() -> None:
    agent = create_agent()

    print("========== Day26: Basic Agent ==========")
    print("输入 q 退出")
    print("输入 history 查看短期记忆")
    print("输入 summary 查看长期摘要")
    print("输入 clear 清空记忆")
    print("----------------------------------------")
    print("示例：")
    print("帮我算一下 123 * 456")
    print("读取 README.md")
    print("添加任务 明天复习 Transformer")
    print("查看任务列表")
    print("完成任务 1")
    print("什么是 Agent？")
    print("----------------------------------------")

    try:
        while True:
            user_input = input("\n你：").strip()

            if user_input.lower() == "q":
                print("已退出 Basic Agent。")
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

            response = agent.run(user_input)

            print("\nAgent：", response.answer)

            print("\n--- 调试信息 ---")
            print("used_tool:", response.used_tool)
            print("tool_name:", response.tool_name)
            print("tool_input:", response.tool_input)
            print("route_reason:", response.route_reason)
            print("tool_success:", response.tool_success)

    finally:
        agent.memory.close()


def main() -> None:
    interactive_agent()


if __name__ == "__main__":
    main()