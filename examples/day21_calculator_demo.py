from src.tools.calculator import CalculatorTool

def interactive_calculator()->None:
    tool=CalculatorTool()
    
    print("========== Day21: Calculator Tool ==========")
    print("输入数学表达式进行计算")
    print("输入 q 退出")
    print("--------------------------------------------")
    print("示例：")
    print("1 + 2 * 3")
    print("(10 + 5) / 3")
    print("2 ** 10")
    print("--------------------------------------------")
    
    while True:
        expression=input("\n表达式:").strip()
        
        if expression.lower()=="q":
            print("已退出计算器。")
            break
        
        result=tool.run(expression)
        
        if result.success:
            print(f"结果：{result.result}")
        else:
            print(f"错误：{result.error}")
            
def main() -> None:
    interactive_calculator()


if __name__ == "__main__":
    main()