import sqlite3
from pathlib import Path
from typing import List
from day13_llm_client import LLMClient,load_config,Message

class SQLiteChatMemory():
    def __init__(
        self,
        db_path:str="data/chat_memory.db",
        session_id:str="default",
    ):
        self.db_path=Path(db_path)
        self.session_id=session_id
        
        self.db_path.parent.mkdir(parents=True,exist_ok=True)
        self.conn=sqlite3.connect(self.db_path)
        self.conn.row_factory=sqlite3.Row
        self._init_table()
        
    def _init_table(self)->None:
        sql = """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.conn.execute(sql)
        self.conn.commit()
        
    def add_message(self,role,content)->None:
        sql = """
        INSERT INTO messages (session_id, role, content)
        VALUES (?, ?, ?);
        """
        self.conn.execute(sql,(self.session_id,role,content))
        self.conn.commit()
        
    def get_messages(self)->List[Message]:
        sql = """
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC;
        """
        
        rows=self.conn.execute(sql,(self.session_id,)).fetchall()
        messages:List[Message]=[]
        for row in rows:
            messages.append({
                "role":row["role"],
                "content":row["content"],
            })
        return messages
    
    def get_recent_messages(self,max_messages:int=10)->List[Message]:
        sql = """
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?;
        """
        rows=self.conn.execute(sql,(self.session_id,max_messages)).fetchall()
        rows=list(rows)
        rows.reverse()
        messages=[]
        for row in rows:
            messages.append({
                "role":row["role"],
                "content":row["content"],
            })
        return messages
    
    def count(self)->int:
        sql = """
        SELECT COUNT(*) AS total
        FROM messages
        WHERE session_id = ?;
        """
        row=self.conn.execute(sql,(self.session_id,)).fetchone()
        return row["total"]
    
    def clear(self)->None:
        sql = """
        DELETE FROM messages
        WHERE session_id = ?;
        """
        self.conn.execute(sql,(self.session_id,))
        self.conn.commit()
        
    def show(self)->None:
        sql = """
        SELECT id, role, content, created_at
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC;
        """
        rows=self.conn.execute(sql,(self.session_id,)).fetchall()
        if not rows:
            print("当前没有历史记忆。")
            return

        print("\n========== 当前 SQLite 历史记忆 ==========")
        for index,row in enumerate(rows,start=1):
            role=row["role"]
            content=row["content"]
            created_at=row["created_at"]
            print(f"{index}. [{role}] {content}")
            print(f"   time: {created_at}")
        
    def close(self)->None:
        self.conn.close()
        
def demo_memory_only()->None:
    memory=SQLiteChatMemory(
        db_path="data/chat_memory.db",
        session_id="demo",
    )
    memory.clear()
    memory.add_message("user", "我正在学习大模型 Agent。")
    memory.add_message("assistant", "很好,Memory 是 Agent 的核心模块之一。")
    memory.add_message("user", "SQLite 记忆和 JSON 记忆有什么区别？")   
    memory.show()
    print("\n当前消息数量:", memory.count())
    recent_messages = memory.get_recent_messages(max_messages=2)
    print("\n========== 最近 2 条消息 ==========")
    for message in recent_messages:
        print(message)

    memory.close()
    
def chat_with_sqlite_memory()->None:
    config=load_config()
    client=LLMClient(config)
    memory = SQLiteChatMemory(
        db_path="data/chat_memory.db",
        session_id="default",
    )
    print("========== Day16: SQLite 对话记忆 ==========")
    print("输入 q 退出")
    print("输入 clear 清空记忆")
    print("输入 history 查看历史记忆")
    print("输入 count 查看消息数量")
    print("--------------------------------------------")
    
    try:
        while True:
            user_input=input("\nYOU:").strip()
            if user_input.lower() == "q":
                print("已退出聊天。")
                break

            if user_input.lower() == "clear":
                memory.clear()
                print("历史记忆已清空。")
                continue

            if user_input.lower() == "history":
                memory.show()
                continue

            if user_input.lower() == "count":
                print(f"当前共有 {memory.count()} 条历史消息。")
                continue

            if not user_input:
                print("请输入内容。")
                continue
            
            history=memory.get_recent_messages(10)
            answer=client.chat(
                user_message=user_input,
                system_prompt="你是一个有数据库记忆能力的 AI 学习助手，回答要清晰、具体。",
                history=history,
            )
            print(f"AI:{answer}")

            memory.add_message("user", user_input)
            memory.add_message("assistant", answer)
    finally:
        memory.close()
        
def main() -> None:
    # Demo 1：只演示数据库记忆读写
    demo_memory_only()

    # Demo 2：进入带 SQLite 记忆的聊天
    chat_with_sqlite_memory()


if __name__ == "__main__":
    main()
        