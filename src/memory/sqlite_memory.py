import sqlite3
from pathlib import Path
from typing import List
from src.llm.client import Message

class SQLiteChatMemory:
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
        sql="""--sql
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.conn.execute(sql)
        self.conn.commit()
        
    def add_message(self,role:str,content:str)->None:
        sql="""--sql
        INSERT INTO messages (session_id,role,content)
        VALUES(?,?,?);
        """
        self.conn.execute(sql,(self.session_id,role,content))
        self.conn.commit()
        
    def get_messages(self)->List[Message]:
        sql="""--sql
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
        sql="""--sql
        SELECT role,content
        FROM messages
        WHERE session_id=?
        ORDER BY id DESC
        LIMIT ?;
        """
        rows=self.conn.execute(sql,(self.session_id,max_messages)).fetchall()
        rows=list(rows)
        rows.reverse()
        messages:List[Message]=[]
        for row in rows:
            messages.append({
                "role":row["role"],
                "content":row["content"],
            })
        return messages
    
    def count(self)->int:
        sql="""--sql
        SELECT COUNT(*) AS total
        FROM messages
        WHERE session_id=?;
        """
        row=self.conn.execute(sql,(self.session_id,)).fetchone()
        return int(row["total"])
    
    def clear(self)->None:
        sql="""--sql
        DELETE FROM messages
        WHERE session_id=?;
        """
        self.conn.execute(sql,(self.session_id,))
        self.conn.commit()
        
    def show(self)->None:
        sql="""--sql
        SELECT id,role,content,created_at
        FROM messages
        WHERE session_id=?
        ORDER BY id ASC;
        """
        rows=self.conn.execute(sql,(self.session_id,)).fetchall()
        if not rows:
            print("当前没有记忆")
            return
        print("\n========== 当前 SQLite 历史记忆 ==========")
        for index,row in enumerate(rows,start=1):
            print(f"{index}. [{row['role']}] {row['content']}")
            print(f"   time: {row['created_at']}")
    def close(self) -> None:
        self.conn.close()
        