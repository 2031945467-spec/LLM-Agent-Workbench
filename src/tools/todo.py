import json
from datetime import datetime
from typing import Any
from pathlib import Path
from src.tools.calculator import ToolResult

class TodoTool:
    name = "todo"
    description = "用于管理任务列表，支持添加、查看、完成、删除和清空任务。"
    
    def __init__(self,file_path:str="data/todos.json")->None:
        self.file_path=Path(file_path)
        self.file_path.parent.mkdir(parents=True,exist_ok=True)
        self.tasks: list[dict[str,Any]]=[]
        self.load()
        
    def load(self)->None:
        if not self.file_path.exists():
            self.tasks=[]
            return
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                data=json.load(f)
                
            if isinstance(data,list):
                self.tasks=data
            else:
                self.tasks=[]
        except json.JSONDecodeError:
            self.tasks=[]
            
    def save(self)->None:
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump(
                self.tasks,
                f,
                ensure_ascii=False,
                indent=2,
            )
            
    def _next_id(self)->int:
        if not self.tasks:
            return 1
        return max(task["id"] for task in self.tasks)+1
    
    def add_task(self,content:str)->ToolResult:
        content=content.strip()
        if not content:
            return ToolResult(
                success=False,
                error="任务内容不能为空。",
            )
            
        task={
            "id":self._next_id(),
            "content":content,
            "done":False,
            "created_at":datetime.now().isoformat(timespec="seconds"),
            "completed_at":None,
        }
        
        self.tasks.append(task)
        self.save()
        
        return ToolResult(
            success=True,
            result=task,
        )
        
    def list_tasks(self,include_done:bool=True)->ToolResult:
        if include_done:
            tasks=self.tasks
        else:
            tasks=[task for task in self.tasks if not task["done"]]
            
        return ToolResult(
            success=True,
            result=tasks,
        )
        
    def complete_task(self,task_id:int)->ToolResult:
        for task in self.tasks:
            if task["id"] == task_id:
                if task["done"]:
                    return ToolResult(
                        success=False,
                        error=f"任务 {task_id} 已经完成。",
                    )

                task["done"] = True
                task["completed_at"] = datetime.now().isoformat(timespec="seconds")
                self.save()

                return ToolResult(
                    success=True,
                    result=task,
                )

        return ToolResult(
            success=False,
            error=f"未找到任务 ID: {task_id}",
        )

    def delete_task(self,task_id:int)->ToolResult:
        for index,task in enumerate(self.tasks):
            if task["id"]==task_id:
                removed=self.tasks.pop(index)
                self.save()
                
                return ToolResult(
                    success=True,
                    result=removed
                )
                
        return ToolResult(
            success=False,
            error=f"未找到任务 ID: {task_id}",
        )
        
    def clear_tasks(self)->ToolResult:
        count=len(self.tasks)
        self.tasks = []
        self.save()

        return ToolResult(
            success=True,
            result={
                "cleared_count": count,
            }
        )
        
    def run(self,command:str)->ToolResult:
        command=command.strip()
        if not command:
            return ToolResult(
                success=False,
                error="命令不能为空。",
            )
            
        parts=command.split(maxsplit=1)
        action=parts[0].lower()
        argument=parts[1] if len(parts) > 1 else ""
        
        try:
            if action == "add":
                return self.add_task(argument)

            if action == "list":
                return self.list_tasks(include_done=True)

            if action == "pending":
                return self.list_tasks(include_done=False)

            if action == "done":
                task_id = int(argument)
                return self.complete_task(task_id)

            if action == "delete":
                task_id = int(argument)
                return self.delete_task(task_id)

            if action == "clear":
                return self.clear_tasks()

            return ToolResult(
                success=False,
                error=f"不支持的命令: {action}",
            )

        except ValueError:
            return ToolResult(
                success=False,
                error="任务 ID 必须是整数。",
            )
            
    def info(self)->str:
        return f"{self.name}: {self.description}"
    
def format_tasks(tasks: list[dict[str, Any]]) -> str:
    """
    把任务列表格式化成适合打印的文本。
    """

    if not tasks:
        return "当前没有任务。"

    lines = []

    for task in tasks:
        status = "✅" if task["done"] else "⬜"
        lines.append(f"{status} {task['id']}. {task['content']}")

    return "\n".join(lines)


def demo() -> None:
    tool = TodoTool(file_path="data/demo_todos.json")

    commands = [
        "clear",
        "add 学习 Day23 TodoTool",
        "add 复习 FastAPI 请求响应模型",
        "list",
        "done 1",
        "pending",
        "delete 2",
        "list",
    ]

    for command in commands:
        print(f"\n命令: {command}")

        result = tool.run(command)

        if not result.success:
            print(f"执行失败: {result.error}")
            continue

        if isinstance(result.result, list):
            print(format_tasks(result.result))
        else:
            print(result.result)


if __name__ == "__main__":
    demo()