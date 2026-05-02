import json
from pathlib import Path
from typing import List,Dict,Optional
from day13_llm_client import LLMClient,load_config,Message

class JsonChatMemory:
    def __init__(self,file_path:str="data/chat_history.json"):
        self.file_path=Path(file_path)
        self.file_path.parent.mkdir(parents=True,exist_ok=True)
        self.messages:List[Message]=[]
        self.load()
    def load(self)->None:
        if not self.file_path.exists():
            self.messages=[]
            return
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                data=json.load(f)
            if isinstance(data,list):
                self.messages=data
            else:
                self.messages=[]
        except json.JSONDecodeError:
            print("警告:JSON 文件格式错误,已重置为空记忆。")
            self.messages=[]
    def save(self)->None:
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump(
                self.messages,
                f,
                ensure_ascii=False,
                indent=2
            )
    def add_message(self,role:str,content:str)->None:
        message:Message={
            "role":role,
            "content":content
        }
        self.messages.append(message)
        self.save()
    def get_messages(self)->List[Message]:
        return self.messages
    def get_recent_messages(self,max_messages:int=10)->List[Message]:
        return self.messages[-max_messages:]
    def clear(self)->None:
        self.messages=[]
        self.save()
    def show(self)->None:
        if not self.messages:
            print("当前没有历史记忆。")
            return
        print("\n========== 当前历史记忆 ==========")
        for index,message in enumerate(self.messages,start=1):
            role=message.get("role","unknow")
            content=message.get("content","")
            print(f"{index}. [{role}] {content}")
def chat_with_json_memory()->None:
    config=load_config()
    client=LLMClient(config)
    memory=JsonChatMemory()
    
    print("========== Day15: JSON 对话记忆 ==========")
    print("输入 q 退出")
    print("输入 clear 清空记忆")
    print("输入 history 查看历史记忆")
    print("------------------------------------------")
    while True:
        user_input=input("\n你:").strip()
        if user_input.lower()=="q":
            print("已退出聊天。")
            break
        if user_input.lower()=="clear":
            memory.clear()
            print("历史记忆已清空。")
            continue
        if user_input.lower()=="history":
            memory.show()
            continue
        if not user_input:
            print("请输入内容。")
            continue
        history=memory.get_recent_messages(max_messages=10)
        
        answer=client.chat(
            user_message=user_input,
            system_prompt="你是一个有记忆能力的 AI 学习助手，回答要清晰、具体。",
            history=history
        )
        print(f"AI:{answer}")
        memory.add_message("user",user_input)
        memory.add_message("assistant",answer)
        
def demo_memory_only()->None:
    memory=JsonChatMemory(file_path="data/demo_memory.json")
    memory.clear()
    memory.add_message("user", "我正在学习大模型 Agent。")
    memory.add_message("assistant", "很好，你现在可以先理解 LLMClient、Memory 和 Tools。")
    memory.add_message("user", "Memory 是做什么的？")
    memory.show()
    recent_messages = memory.get_recent_messages(max_messages=2)

    print("\n========== 最近 2 条消息 ==========")
    for message in recent_messages:
        print(message)
        
def main() -> None:
    # Demo 1：只演示 JSON 读写，不调用模型
    demo_memory_only()

    # Demo 2：真正进入带记忆的聊天
    chat_with_json_memory()


if __name__ == "__main__":
    main()
    