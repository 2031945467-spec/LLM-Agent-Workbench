from typing import Any
from src.tools.calculator import ToolResult

class ToolRegistry:
    def __init__(self)->None:
        self.tools:dict[str,Any]={}
        
    def register(self,tool:Any)->None:
        
        name=getattr(tool,"name",None)
        description=getattr(tool,"description",None)
        run=getattr(tool,"run",None)
        
        if not name:
            raise ValueError("工具必须有 name 属性。")
        
        if not description:
            raise ValueError(f"工具 {name} 必须有 description 属性。")

        if not callable(run):
            raise ValueError(f"工具 {name} 必须有可调用的 run() 方法。")
        
        normalized_name=name.lower().strip()
        self.tools[normalized_name]=tool
        
    def get_tool(self,name:str)->Any|None:
        normalized_name=name.lower().strip()
        return self.tools.get(normalized_name)
    
    def has_tool(self,name:str)->bool:
        return self.get_tool(name) is not None
    
    def list_tools(self)->list[dict[str,str]]:
        result=[]
        
        for name,tool in self.tools.items():
            result.append({
                "name":name,
                "description":tool.description,
            })
            
        return result
    
    def run_tool(self,name:str,tool_input:str)->ToolResult:
        tool=self.get_tool(name)
        
        if tool is None:
            return ToolResult(
                success=False,
                error=f"未找到工具: {name}",
            )
            
        try:
            return tool.run(tool_input)
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"工具 {name} 执行失败: {e}",
            )
            
    def remove_tool(self,name:str)->ToolResult:
        normalized_name=name.lower().strip()
        
        if normalized_name not in self.tools:
            return ToolResult(
                success=False,
                error=f"未找到工具: {name}",
            )
            
        removed=self.tools.pop(normalized_name)
        return ToolResult(
            success=True,
            result={
                "name": normalized_name,
                "description": removed.description,
            },
        )
    
    def clear(self)->None:
        self.tools.clear()
        
def create_default_registry() -> ToolRegistry:
    """
    创建默认工具注册表。

    当前注册：
    - calculator
    - file_reader
    - todo
    """

    from src.tools.calculator import CalculatorTool
    from src.tools.file_reader import FileReaderTool
    from src.tools.todo import TodoTool

    registry = ToolRegistry()

    registry.register(CalculatorTool())
    registry.register(FileReaderTool(base_dir="."))
    registry.register(TodoTool(file_path="data/day24_todos.json"))

    return registry