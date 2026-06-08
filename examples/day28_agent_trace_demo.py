"""
Day28: Agent Trace Demo

运行方式：
    python -m examples.day28_agent_trace_demo
"""

from src.agent.react_agent import ReActAgent
from src.agent.trace import AgentTraceLogger
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
        db_path="data/day28_trace_agent.db",
        session_id="day28",
    )

    summary_memory = SummaryMemory(
        file_path="data/day28_trace_agent_summary.txt",
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


def print_steps(response) -> None:
    """
    打印本轮 ReAct 过程。
    """

    print("\n========== ReAct Trace ==========")

    for index, step in enumerate(response.steps, start=1):
        print(f"\nStep {index}")
        print(f"Thought: {step.thought}")
        print(f"Action: {step.action}")
        print(f"Action Input: {step.action_input}")
        print(f"Observation: {step.observation}")


def interactive_agent() -> None:
    agent = create_agent()
    trace_logger = AgentTraceLogger(
        file_path="data/day28_agent_traces.jsonl"
    )

    show_trace = True

    print("========== Day28: Agent Trace Logger ==========")
    print("输入 q 退出")
    print("输入 history 查看短期记忆")
    print("输入 summary 查看长期摘要")
    print("输入 clear 清空记忆")
    print("输入 traces 查看最近 Trace 日志")
    print("输入 clear_traces 清空 Trace 日志")
    print("输入 trace on / trace off 开关终端 Trace 显示")
    print("输入 tools 查看工具")
    print("-----------------------------------------------")
    print("示例：")
    print("帮我算一下 123 * 456")
    print("读取 README.md")
    print("添加任务 明天复习 Transformer")
    print("查看任务列表")
    print("什么是 ReAct Agent？")
    print("-----------------------------------------------")

    try:
        while True:
            user_input = input("\n你：").strip()

            if user_input.lower() == "q":
                print("已退出 Agent Trace Demo。")
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

            if user_input.lower() == "traces":
                trace_logger.show_recent(limit=5)
                continue

            if user_input.lower() == "clear_traces":
                trace_logger.clear()
                print("Trace 日志已清空。")
                continue

            if user_input.lower() == "trace on":
                show_trace = True
                print("已开启终端 Trace 显示。")
                continue

            if user_input.lower() == "trace off":
                show_trace = False
                print("已关闭终端 Trace 显示，但日志仍会保存。")
                continue

            if user_input.lower() == "tools":
                for tool_info in agent.router.registry.list_tools():
                    print(f"- {tool_info['name']}: {tool_info['description']}")
                continue

            if not user_input:
                print("请输入内容。")
                continue

            response = agent.run(user_input)

            trace_logger.log(
                user_input=user_input,
                response=response,
            )

            print("\nAgent：")
            print(response.answer)

            print(f"\n是否使用工具：{response.used_tool}")

            if show_trace:
                print_steps(response)

    finally:
        agent.memory.close()


def main() -> None:
    interactive_agent()


if __name__ == "__main__":
    main()