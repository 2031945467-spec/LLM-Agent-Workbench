import re
from typing import Optional
from src.tools.calculator import ToolResult
from src.tools.registry import ToolRegistry
from dataclasses import dataclass

@dataclass
class ToolRoute:
    should_use_tool:bool
    tool_name:Optional[str]=None
    tool_input:str=""
    reason:str=""
    
class ToolRouter:
    def __init__(self,registry:ToolRegistry)->None:
        self.registry=registry
        
    def route(self,user_input:str)->ToolRoute:
        text=user_input.strip()
        if not text:
            return ToolRoute(
                should_use_tool=False,
                reason="用户输入为空"
            )
            
        calculator_route=self._route_calculator(text)
        if calculator_route.should_use_tool:
            return calculator_route
        
        file_route = self._route_file_reader(text)
        if file_route.should_use_tool:
            return file_route

        todo_route = self._route_todo(text)
        if todo_route.should_use_tool:
            return todo_route
        
        return ToolRoute(
            should_use_tool=False,
            reason="没有匹配到合适工具",
        )
        
    def run(self,user_input:str)->tuple[ToolRoute,ToolResult]:
        route=self.route(user_input)
        if not route.should_use_tool or not route.tool_name:
            return route,ToolResult(
                success=False,
                error=route.reason
            )
        result=self.registry.run_tool(
            name=route.tool_name,
            tool_input=route.tool_input
        )
        return route,result
    
    def _route_calculator(self,text:str)->ToolRoute:
        calculate_keywords = [
            "计算",
            "算一下",
            "帮我算",
            "等于多少",
            "结果是多少",
        ]
        has_keyword=any(keyword in text for keyword in calculate_keywords)
        math_expression = self._extract_math_expression(text)
        
        if has_keyword and math_expression:
            return ToolRoute(
                should_use_tool=True,
                tool_name="calculator",
                tool_input=math_expression,
                reason="检测到计算意图。",
            )

        return ToolRoute(
            should_use_tool=False,
            reason="不是计算任务。",
        )
        
    def _extract_math_expression(self, text: str) -> str:
        candidates = re.findall(r"[-+*/%().\d\s]+", text)
        candidates=[
            item.strip()
            for item in candidates
            if item.strip()
        ]
        if not candidates:
            return ""
        
        valid_candidates = []
        
        for candidate in candidates:
            has_digit=any(char.isdigit() for char in candidate)
            has_operator=any(op in candidate for op in ["+", "-", "*", "/", "%"])
            
            if has_digit and has_operator:
                valid_candidates.append(candidate)
                
        if not valid_candidates:
            return ""
        
        return max(valid_candidates,key=len)
    
    def _route_file_reader(self, text: str) -> ToolRoute:
        file_keywords = [
            "读取",
            "打开",
            "查看文件",
            "读一下",
            "文件内容",
            "总结文件",
        ]
        has_keyword = any(keyword in text for keyword in file_keywords)

        file_path = self._extract_file_path(text)

        if has_keyword and file_path:
            return ToolRoute(
                should_use_tool=True,
                tool_name="file_reader",
                tool_input=file_path,
                reason="检测到文件读取意图。",
            )

        return ToolRoute(
            should_use_tool=False,
            reason="不是文件读取任务。",
        )
        
    def _extract_file_path(self, text: str) -> str:
        pattern = r"[\w./\\-]+\.(?:md|txt|json|py|csv)"
        match = re.search(pattern, text)

        if not match:
            return ""

        return match.group(0)
    
    def _route_todo(self, text: str) -> ToolRoute:
        lower_text=text.lower()
        if text.startswith("添加任务"):
            content = text.replace("添加任务", "", 1).strip()
            return ToolRoute(
                should_use_tool=True,
                tool_name="todo",
                tool_input=f"add {content}",
                reason="检测到添加任务意图。",
            )

        if text.startswith("新增任务"):
            content = text.replace("新增任务", "", 1).strip()
            return ToolRoute(
                should_use_tool=True,
                tool_name="todo",
                tool_input=f"add {content}",
                reason="检测到新增任务意图。",
            )

        if "查看任务" in text or "任务列表" in text or "列出任务" in text:
            return ToolRoute(
                should_use_tool=True,
                tool_name="todo",
                tool_input="list",
                reason="检测到查看任务列表意图。",
            )

        if "未完成任务" in text or "待办任务" in text:
            return ToolRoute(
                should_use_tool=True,
                tool_name="todo",
                tool_input="pending",
                reason="检测到查看未完成任务意图。",
            )

        done_match = re.search(r"(完成任务|标记完成)\s*(\d+)", text)
        if done_match:
            task_id = done_match.group(2)
            return ToolRoute(
                should_use_tool=True,
                tool_name="todo",
                tool_input=f"done {task_id}",
                reason="检测到完成任务意图。",
            )

        delete_match = re.search(r"(删除任务|移除任务)\s*(\d+)", text)
        if delete_match:
            task_id = delete_match.group(2)
            return ToolRoute(
                should_use_tool=True,
                tool_name="todo",
                tool_input=f"delete {task_id}",
                reason="检测到删除任务意图。",
            )

        if "清空任务" in text or lower_text == "clear todos":
            return ToolRoute(
                should_use_tool=True,
                tool_name="todo",
                tool_input="clear",
                reason="检测到清空任务意图。",
            )

        return ToolRoute(
            should_use_tool=False,
            reason="不是 Todo 任务。",
        )
