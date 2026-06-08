"""
Day27: ReAct Agent Demo

运行方式：
    python -m examples.day27_react_agent_demo
"""

from src.agent.react_agent import ReActAgent
from src.config.settings import load_app_config
from src.llm.client import LLMClient
from src.memory.sqlite_memory import SQLiteChatMemory
from src.memory.summary_memory import SummaryMemory
from src.tools.registry import create_default_registry
from src.tools.router import ToolRouter


def create_agent() -> ReActAgent:
    config = load_app_config()
    client = LLMClient(config)

    memory = SQLiteChatMemory(
        db_path="data/day27_react_agent.db",
        session_id="day27",
    )

    summary_memory = SummaryMemory(
        file_path="data/day27_react_agent_summary.txt",
    )

    registry = create_default_registry()
    router = ToolRouter(registry)

    return ReActAgent(
        client=client,
        memory=memory,
        summary_memory=summary_memory,
        router=router,
        max_history=6,
    )


def print_steps(agent_response) -> None:
    """
    打印 ReAct 执行过程。
    """

    print("\n========== ReAct Trace ==========")

    for index, step in enumerate(agent_response.steps, start=1):
        print(f"\nStep {index}")
        print(f"Thought: {step.thought}")
        print(f"Action: {step.action}")
        print(f"Action Input: {step.action_input}")
        print(f"Observation: {step.observation}")


def interactive_agent() -> None:
    agent = create_agent()

    print("========== Day27: ReAct Agent ==========")
    print("输入 q 退出")
    print("输入 history 查看短期记忆")
    print("输入 summary 查看长期摘要")
    print("输入 clear 清空记忆")
    print("输入 tools 查看工具")
    print("----------------------------------------")
    print("示例：")
    print("帮我算一下 123 * 456")
    print("读取 README.md")
    print("添加任务 明天复习 Transformer")
    print("查看任务列表")
    print("完成任务 1")
    print("什么是 ReAct Agent？")
    print("----------------------------------------")

    try:
        while True:
            user_input = input("\n你：").strip()

            if user_input.lower() == "q":
                print("已退出 ReAct Agent。")
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
                for tool_info in agent.router.registry.list_tools():
                    print(f"- {tool_info['name']}: {tool_info['description']}")
                continue

            response = agent.run(user_input)

            print("\nAgent：")
            print(response.answer)

            print_steps(response)

    finally:
        agent.memory.close()


def main() -> None:
    interactive_agent()


if __name__ == "__main__":
    main()