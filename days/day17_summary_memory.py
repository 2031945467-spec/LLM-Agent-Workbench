from pathlib import Path
from typing import List
from day13_llm_client import LLMClient,load_config,Message
from day16_sqlite_memory import SQLiteChatMemory

class SummaryMemory:
    def __init__(self,file_path:str="data/chat_summary.txt"):
        self.file_path=Path(file_path)
        self.file_path.parent.mkdir(parents=True,exist_ok=True)
        self.summary:str=""
        self.load()
        
    def load(self)->None:
        if not self.file_path.exists():
            self.summary=""
            return
        self.summary=self.file_path.read_text(encoding="utf-8")
        
    def save(self)->None:
        self.file_path.write_text(self.summary,encoding="utf-8")
        
    def clear(self)->None:
        self.summary=""
        self.save()
        
    def get_summary(self)->str:
        return self.summary
    
    def updated_summary(self,client:LLMClient,old_messages:List[Message])->None:
        if not old_messages:
            return
        old_text=self._format_messages(old_messages)
        prompt = f"""
你需要更新一段长期记忆摘要。

已有摘要：
{self.summary if self.summary else "暂无"}

新增加的旧对话内容：
{old_text}

请把“已有摘要”和“新增加的旧对话内容”合并成一段新的长期记忆摘要。

要求：
1. 保留用户长期偏好、正在做的项目、学习目标、重要事实
2. 删除寒暄、重复内容、临时无意义内容
3. 用简洁中文输出
4. 不要超过 300 字
"""
        new_summary=client.chat(
            user_message=prompt,
            system_prompt="你是一个记忆总结助手，擅长把长对话压缩成简洁、准确的长期记忆。",
            history=None,
        )
        self.summary=new_summary.strip()
        self.save()
        
    @staticmethod
    def _format_messages(messages:List[Message])->str:
        lines=[]
        for message in messages:
            role=message.get("role","unkown")
            content=message.get("content","")
            lines.append(f"{role}:{content}")
        return "\n".join(lines)
    
    def show(self)->None:
        if not self.summary:
            print("当前没有长期摘要记忆。")
            return
        
        print("\n========== 当前长期摘要记忆 ==========")
        print(self.summary)
        
def build_system_prompt(summary_memory:SummaryMemory)->str:
    summary=summary_memory.get_summary()
    if not summary:
        return "你是一个有记忆能力的 AI 学习助手，回答要清晰、具体。"
    
    return f"""
你是一个有记忆能力的 AI 学习助手，回答要清晰、具体。

以下是你对用户的长期记忆摘要：
{summary}

请在回答时合理参考这些长期记忆，但不要机械重复摘要内容。
"""

def compress_memory_if_needed(
    memory:SQLiteChatMemory,
    summary_memory:SummaryMemory,
    client:LLMClient,
    trigger_count:int=16,
    keep_recent:int=4,
)->None:
    total=memory.count()
    if total<=trigger_count:
        return
    
    all_messages=memory.get_messages()
    old_messages=all_messages[:-keep_recent]
    recent_messages=all_messages[-keep_recent:]
    
    print("\n检测到历史消息较长,开始压缩旧记忆...")
    summary_memory.updated_summary(client=client,old_messages=old_messages)
    memory.clear()
    
    for message in recent_messages:
        memory.add_message(
            role=message["role"],
            content=message["content"],
        )
    print("旧记忆已压缩为长期摘要，最近消息已保留。")
    
def demo_summary_only()->None:
    config=load_config()
    client=LLMClient(config=config)
    summary_memory=SummaryMemory(file_path="data/demo_summary.txt")
    summary_memory.clear()
    old_messages: List[Message] = [
        {"role": "user", "content": "我是一名 211 人工智能专业大二学生。"},
        {"role": "assistant", "content": "你可以围绕大模型 Agent 做项目。"},
        {"role": "user", "content": "我的目标是暑假找一份大模型相关实习。"},
        {"role": "assistant", "content": "建议你学习 LLMClient、Memory、Tools、Agent、RAG。"},
    ]
    summary_memory.updated_summary(
        client=client,
        old_messages=old_messages,
    )

    summary_memory.show()
    
    
    
def chat_with_summary_memory()->None:
    config=load_config()
    client=LLMClient(config=config)
    memory=SQLiteChatMemory(
        db_path="data/day17_summary_memory.db",
        session_id="summary_demo",
    )
    summary_memory=SummaryMemory(file_path="data/day17_summary.txt")
    
    print("========== Day17: 长对话总结记忆 ==========")
    print("输入 q 退出")
    print("输入 clear 清空短期记忆和长期摘要")
    print("输入 history 查看短期历史")
    print("输入 summary 查看长期摘要")
    print("输入 count 查看短期消息数量")
    print("--------------------------------------------")
    
    try:
        while True:
            user_input = input("\n你:").strip()

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
    # Demo 1：演示长期摘要如何生成
    demo_summary_only()

    # Demo 2：进入带摘要记忆的聊天
    chat_with_summary_memory()


if __name__ == "__main__":
    main()