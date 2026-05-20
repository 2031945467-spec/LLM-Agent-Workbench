from typing import Any
from src.tools.todo import TodoTool, format_tasks

def print_result(result) -> None:
    if not result.success:
        print(f"错误：{result.error}")
        return

    data: Any = result.result

    if isinstance(data, list):
        print(format_tasks(data))
    else:
        print(data)


def interactive_todo() -> None:
    tool = TodoTool(file_path="data/todos.json")

    print("========== Day23: Todo Tool ==========")
    print("支持命令：")
    print("add 任务内容")
    print("list")
    print("pending")
    print("done 任务ID")
    print("delete 任务ID")
    print("clear")
    print("q")
    print("--------------------------------------")

    while True:
        command = input("\nTodo> ").strip()

        if command.lower() == "q":
            print("已退出 Todo 工具。")
            break

        result = tool.run(command)
        print_result(result)


def main() -> None:
    interactive_todo()


if __name__ == "__main__":
    main()