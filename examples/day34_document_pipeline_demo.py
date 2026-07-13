"""
Day34: Document Loader + Text Splitter Demo

运行方式：
    python -m examples.day34_document_pipeline_demo
"""

from src.rag.document_loader import DocumentLoader
from src.rag.text_splitter import TextSplitter


def print_document(document) -> None:
    print("\n========== Document ==========")
    print("source:", document.source)
    print("file_name:", document.metadata.get("file_name"))
    print("extension:", document.metadata.get("extension"))
    print("size:", document.metadata.get("size"))
    print("content preview:")
    print(document.content[:300])


def print_chunks(chunks, max_show: int = 5) -> None:
    print("\n========== Text Chunks ==========")
    print("chunk count:", len(chunks))

    for chunk in chunks[:max_show]:
        print("\n" + "-" * 60)
        print("chunk_id:", chunk.chunk_id)
        print("source:", chunk.source)
        print(
            "position:",
            f"{chunk.start_index} - {chunk.end_index}",
        )
        print("chunk_size:", len(chunk.content))
        print("content:")
        print(chunk.content[:500])


def single_file_demo() -> None:
    """
    测试读取并切分 README.md。
    """

    loader = DocumentLoader(base_dir=".")

    document = loader.load_file("README.md")

    splitter = TextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_document(document)

    print_document(document)
    print_chunks(chunks)


def directory_demo() -> None:
    """
    测试读取并切分 docs 目录。
    """

    loader = DocumentLoader(base_dir=".")

    documents = loader.load_directory(
        directory_path="docs",
        recursive=True,
    )

    splitter = TextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(documents)

    print("\n========== Directory Result ==========")
    print("document count:", len(documents))
    print("chunk count:", len(chunks))

    print_chunks(chunks, max_show=5)


def interactive_demo() -> None:
    loader = DocumentLoader(base_dir=".")

    print("\n========== Interactive Demo ==========")
    print("输入项目内的文件路径，例如：")
    print("README.md")
    print("docs/learning_log.md")

    file_path = input("\n文件路径：").strip()

    if not file_path:
        print("文件路径不能为空。")
        return

    try:
        document = loader.load_file(file_path)

        splitter = TextSplitter(
            chunk_size=500,
            chunk_overlap=100,
        )

        chunks = splitter.split_document(document)

        print_document(document)
        print_chunks(chunks)

    except Exception as e:
        print("处理失败：", e)


def main() -> None:
    single_file_demo()

    print("\n是否测试 docs 目录？")
    choice = input("输入 y 测试，其他键跳过：").strip().lower()

    if choice == "y":
        directory_demo()

    print("\n是否进入交互模式？")
    choice = input("输入 y 进入，其他键退出：").strip().lower()

    if choice == "y":
        interactive_demo()


if __name__ == "__main__":
    main()