from typing import Any
from src.tools.registry import create_default_registry
from src.tools.router import ToolRouter
from src.tools.todo import format_tasks

def print_tool_result(data: Any) -> None:
    if isinstance(data, list):
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
    
def demo_router_basic() -> None:
    registry = create_default_registry()
    router = ToolRouter(registry)

    examples = [
        "帮我算一下 123 * 456",
        "计算 (10 + 5) / 3",
        "读取 README.md",
        "打开 docs/learning_log.md",
        "添加任务 复习 Transformer",
        "添加任务 完成 Day25 ToolRouter",
        "查看任务列表",
        "完成任务 1",
        "未完成任务有哪些",
        "删除任务 2",
        "今天天气怎么样",
    ]

    print("========== Day25: Tool Router Basic Demo ==========")

    registry.run_tool("todo", "clear")

    for user_input in examples:
        print("\n用户输入:", user_input)

        route, result = router.run(user_input)

        print("是否调用工具：", route.should_use_tool)
        print("工具名：", route.tool_name)
        print("工具输入：", route.tool_input)
        print("路由原因：", route.reason)

        if result.success:
            print("工具结果：")
            print_tool_result(result.result)
        else:
            print("工具失败：", result.error)
            
def interactive_router() -> None:
    """
    交互式 ToolRouter Demo。
    """

    registry = create_default_registry()
    router = ToolRouter(registry)

    print("\n========== Day25: Tool Router ==========")
    print("你可以输入自然语言，Router 会尝试选择工具")
    print("输入 tools 查看工具")
    print("输入 q 退出")
    print("----------------------------------------")
    print("示例：")
    print("帮我算一下 123 * 456")
    print("读取 README.md")
    print("添加任务 明天复习 Transformer")
    print("查看任务列表")
    print("完成任务 1")
    print("----------------------------------------")

    while True:
        user_input = input("\n你:").strip()

        if user_input.lower() == "q":
            print("已退出 ToolRouter。")
            break

        if user_input.lower() == "tools":
            for tool_info in registry.list_tools():
                print(f"- {tool_info['name']}: {tool_info['description']}")
            continue

        route, result = router.run(user_input)

        print("\n路由结果:")
        print(f"should_use_tool: {route.should_use_tool}")
        print(f"tool_name: {route.tool_name}")
        print(f"tool_input: {route.tool_input}")
        print(f"reason: {route.reason}")

        if not route.should_use_tool:
            print("没有调用工具。")
            continue

        print("\n工具执行结果:")

        if result.success:
            print_tool_result(result.result)
        else:
            print(f"执行失败：{result.error}")


def main() -> None:
    demo_router_basic()
    interactive_router()


if __name__ == "__main__":
    main()