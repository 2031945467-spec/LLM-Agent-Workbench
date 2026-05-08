from src.config.settings import load_app_config
from src.llm.client import LLMClient
from src.memory.sqlite_memory import SQLiteChatMemory
from src.memory.summary_memory import (
    SummaryMemory,
    build_system_prompt,
    compress_memory_if_needed,
)

def print_config() -> None:
    config = load_app_config()

    print("\n========== 当前配置 ==========")
    for key, value in config.safe_dict().items():
        print(f"{key}: {value}")

def chat()->None:
    config=load_app_config()
    client=LLMClient(config=config)
    memory = SQLiteChatMemory(
        db_path="data/day18_project_chat.db",
        session_id="day18",
    )
    summary_memory = SummaryMemory(
        file_path="data/day18_project_summary.txt",
    )
    
    print("========== Day18: 项目模块化聊天 ==========")
    print("输入 q 退出")
    print("输入 clear 清空记忆")
    print("输入 history 查看短期记忆")
    print("输入 summary 查看长期摘要")
    print("输入 count 查看短期消息数量")
    print("-------------------------------------------")
    
    try:
        while True:
            user_input = input("\n你：").strip()

            if user_input.lower() == "q":
                print("已退出聊天。")
                break

            if user_input.lower() == "clear":
                memory.clear()
                summary_memory.clear()
                print("短期记忆和长期摘要已清空。")
                continue

            if user_input.lower() == "history":
                memory.show()
                continue

            if user_input.lower() == "summary":
                summary_memory.show()
                continue

            if user_input.lower() == "count":
                print(f"当前短期消息数量：{memory.count()}")
                continue

            if not user_input:
                print("请输入内容。")
                continue

            system_prompt = build_system_prompt(summary_memory)
            recent_history = memory.get_recent_messages(max_messages=6)

            answer = client.chat(
                user_message=user_input,
                system_prompt=system_prompt,
                history=recent_history,
            )

            print(f"AI:{answer}")

            memory.add_message("user", user_input)
            memory.add_message("assistant", answer)

            compress_memory_if_needed(
                memory=memory,
                summary_memory=summary_memory,
                client=client,
                trigger_count=14,
                keep_recent=6,
            )

    finally:
        memory.close()


def main() -> None:
    print_config()
    chat()


if __name__ == "__main__":
    main()