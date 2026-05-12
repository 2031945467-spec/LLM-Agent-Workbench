import ast
import operator
from dataclasses import dataclass
from typing import Any

@dataclass
class ToolResult:
    success:bool
    result:Any=None
    error:str|None=None
    
class SafeMathEvaluator(ast.NodeVisitor):
    ALLOWED_BIN_OPS={
        ast.Add:operator.add,
        ast.Sub:operator.sub,
        ast.Mult:operator.mul,
        ast.Div:operator.truediv,
        ast.FloorDiv:operator.floordiv,
        ast.Mod:operator.mod,
        ast.Pow:operator.pow
    }
    ALLOWED_UNARY_OPS={
        ast.UAdd:operator.pos,
        ast.USub:operator.neg
    }
    
    def visit_Expression(self, node:ast.Expression)->float:
        return self.visit(node.body)
    
    def visit_Constant(self, node:ast.Constant)->float:
        if isinstance(node.value,(int,float)):
            return node.value
        raise ValueError(f"不支持的常量类型: {type(node.value)}")
    
    def visit_BinOp(self, node:ast.BinOp)->float:
        op_type=type(node.op)
        
        if op_type not in self.ALLOWED_BIN_OPS:
            raise ValueError(f"不支持的运算符: {op_type.__name__}")
        left=self.visit(node.left)
        right=self.visit(node.right)
        
        return self.ALLOWED_BIN_OPS[op_type](left,right)
    
    def visit_UnaryOp(self, node:ast.UnaryOp)->float:
        op_type=type(node.op)
        
        if op_type not in self.ALLOWED_UNARY_OPS:
            raise ValueError(f"不支持的一元运算符: {op_type.__name__}")
        
        value=self.visit(node.operand)
        return self.ALLOWED_UNARY_OPS[op_type](value)
    
    def generic_visit(self, node:ast.AST)->float:
        raise ValueError(f"不允许的表达式: {type(node).__name__}")
    
class CalculatorTool:
    name="calculator"
    description = "用于计算数学表达式，支持 +、-、*、/、//、%、** 和括号。"
    
    def __init__(self)->None:
        self.evaluator=SafeMathEvaluator()
        
    def run(self,expression:str)->ToolResult:
        expression=expression.strip()
        if not expression:
            return ToolResult(
                success=False,
                error="表达式不能为空。"
            )
        try:
            tree=ast.parse(expression,mode="eval")
            result=self.evaluator.visit(tree)
            
            return ToolResult(
                success=True,
                result=result
            )
        except ZeroDivisionError:
            return ToolResult(
                success=False,
                error="除数不能为 0。"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
            
def demo()->None:
    
    tool=CalculatorTool()
    expressions = [
        "1 + 2 * 3",
        "(10 + 5) / 3",
        "2 ** 10",
        "10 // 3",
        "10 % 3",
        "-5 + 2",
        "1 / 0",
        "__import__('os').system('dir')",
    ]
    for expression in expressions:
        result=tool.run(expression)
        print(f"\n表达式: {expression}")

        if result.success:
            print(f"计算结果: {result.result}")
        else:
            print(f"执行失败: {result.error}")
            
if __name__ == "__main__":
    demo()
    