from typing import Any
from src.tools.registry import create_default_registry
from src.tools.todo import format_tasks

def print_tool_result(result)->None:
    if not result.success:
        print(f"执行失败：{result.error}")
        return
    data:Any=result.result
    if isinstance(data,list):
        print(format_tasks(data))
        return
    
    if isinstance(data, dict):
        if "content" in data and "path" in data:
            print(f"文件路径：{data['path']}")
            print(f"文件大小：{data['size']} bytes")
            print("\n文件内容预览:")
            print(data["content"][:500])
            return

        print(data)
        return

    print(data)
    
def demo_registry_basic() -> None:
    registry = create_default_registry()

    print("========== 已注册工具 ==========")

    for tool_info in registry.list_tools():
        print(f"- {tool_info['name']}: {tool_info['description']}")

    print("\n========== 调用 calculator ==========")
    result = registry.run_tool("calculator", "1 + 2 * 3")
    print_tool_result(result)

    print("\n========== 调用 file_reader ==========")
    result = registry.run_tool("file_reader", "README.md")
    print_tool_result(result)

    print("\n========== 调用 todo ==========")
    registry.run_tool("todo", "clear")
    registry.run_tool("todo", "add 学习 Day24 ToolRegistry")
    registry.run_tool("todo", "add 复习 Agent 工具调用流程")

    result = registry.run_tool("todo", "list")
    print_tool_result(result)

    print("\n========== 调用不存在的工具 ==========")
    result = registry.run_tool("weather", "北京天气")
    print_tool_result(result)

def interactive_registry() -> None:
    """
    交互式工具注册表 Demo。
    """

    registry = create_default_registry()

    print("\n========== Day24: Tool Registry ==========")
    print("输入 tools 查看所有工具")
    print("输入 工具名 + 空格 + 工具输入 来调用工具")
    print("输入 q 退出")
    print("------------------------------------------")
    print("示例：")
    print("calculator 1 + 2 * 3")
    print("file_reader README.md")
    print("todo add 学习 Tool Registry")
    print("todo list")
    print("------------------------------------------")

    while True:
        command = input("\nToolRegistry> ").strip()

        if command.lower() == "q":
            print("已退出 Tool Registry。")
            break

        if command.lower() == "tools":
            for tool_info in registry.list_tools():
                print(f"- {tool_info['name']}: {tool_info['description']}")
            continue

        if not command:
            print("请输入命令。")
            continue

        parts = command.split(maxsplit=1)

        if len(parts) < 2:
            print("格式错误，请输入：工具名 工具输入")
            continue

        tool_name = parts[0]
        tool_input = parts[1]

        result = registry.run_tool(tool_name, tool_input)
        print_tool_result(result)


def main() -> None:
    demo_registry_basic()
    interactive_registry()


if __name__ == "__main__":
    main()