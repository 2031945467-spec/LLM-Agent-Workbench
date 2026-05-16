from src.tools.file_reader import FileReaderTool

def interactive_file_reader()->None:
    tool=FileReaderTool(base_dir=".")
    
    print("========== Day22: File Reader Tool ==========")
    print("输入文件路径读取内容")
    print("输入 q 退出")
    print("---------------------------------------------")
    print("示例：")
    print("README.md")
    print("docs/learning_log.md")
    print("requirements.txt")
    print("---------------------------------------------")
    
    while True:
        file_path = input("\n文件路径:").strip()

        if file_path.lower() == "q":
            print("已退出文件读取工具。")
            break

        result = tool.run(file_path)

        if result.success:
            data = result.result
            content = data["content"]

            print(f"\n文件路径:{data['path']}")
            print(f"文件大小：{data['size']} bytes")
            print("\n========== 文件内容预览 ==========")
            print(content[:1000])

            if len(content) > 1000:
                print("\n... 文件内容较长，只显示前 1000 字符 ...")

        else:
            print(f"错误：{result.error}")


def main() -> None:
    interactive_file_reader()


if __name__ == "__main__":
    main()