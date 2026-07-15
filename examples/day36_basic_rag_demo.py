"""
Day36: Basic RAG Demo

流程：
1. 加载 docs 文件夹中的文档
2. 文本切块
3. 生成 Embedding
4. 建立 FAISS 索引
5. Retriever 检索
6. LLM 根据检索结果回答

运行方式：
    python -m examples.day36_basic_rag_demo
"""

from src.config.settings import load_app_config
from src.llm.client import LLMClient
from src.rag.document_loader import DocumentLoader
from src.rag.embedding_model import EmbeddingModel
from src.rag.rag_chain import BasicRAG
from src.rag.retriever import Retriever
from src.rag.text_splitter import TextSplitter
from src.rag.vector_store import FaissVectorStore


def build_rag() -> BasicRAG:
    """
    构建完整的基础 RAG 系统。
    """

    print("1. 加载配置和大模型……")

    config = load_app_config()
    client = LLMClient(config)

    print("2. 加载 docs 文件夹……")

    loader = DocumentLoader(base_dir=".")

    documents = loader.load_directory(
        directory_path="docs",
        recursive=True,
    )

    if not documents:
        raise RuntimeError(
            "docs 文件夹中没有可用文档。"
        )

    print(f"文档数量：{len(documents)}")

    print("3. 切分文档……")

    splitter = TextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise RuntimeError(
            "没有生成有效文本块。"
        )

    print(f"文本块数量：{len(chunks)}")

    print("4. 加载 Embedding 模型……")

    embedding_model = EmbeddingModel()

    print("模型：", embedding_model.model_name)
    print("向量维度：", embedding_model.dimension)

    print("5. 生成文本块向量……")

    embeddings = embedding_model.encode_chunks(
        chunks=chunks,
        batch_size=32,
    )

    print("向量形状：", embeddings.shape)

    print("6. 建立 FAISS 向量库……")

    vector_store = FaissVectorStore(
        dimension=embedding_model.dimension,
    )

    vector_store.add(
        chunks=chunks,
        embeddings=embeddings,
    )

    print("索引大小：", vector_store.size)

    print("7. 创建 Retriever 和 BasicRAG……")

    retriever = Retriever(
        embedding_model=embedding_model,
        vector_store=vector_store,
        default_top_k=3,
    )

    return BasicRAG(
        client=client,
        retriever=retriever,
        max_context_chars=6000,
    )


def print_sources(response) -> None:
    """
    打印 RAG 使用的检索来源。
    """

    sources = response.get_sources()

    if not sources:
        print("\n没有检索来源。")
        return

    print("\n========== Retrieval Sources ==========")

    for index, source in enumerate(
        sources,
        start=1,
    ):
        print(f"\n参考资料 {index}")
        print(f"来源：{source['source']}")
        print(f"Chunk ID：{source['chunk_id']}")
        print(f"相似度：{source['score']:.4f}")
        print(
            "原文位置："
            f"{source['start_index']}"
            f"-{source['end_index']}"
        )


def interactive_demo(rag: BasicRAG) -> None:
    """
    交互式知识库问答。
    """

    print("\n========== Day36: Basic RAG ==========")
    print("输入 q 退出")
    print("--------------------------------------")
    print("示例：")
    print("Planner 的作用是什么？")
    print("Executor 是如何执行计划的？")
    print("项目中有哪些工具？")
    print("短期记忆和长期记忆有什么区别？")
    print("--------------------------------------")

    while True:
        query = input("\n你的问题：").strip()

        if query.lower() == "q":
            print("已退出 Basic RAG。")
            break

        if not query:
            print("问题不能为空。")
            continue

        response = rag.ask(
            query=query,
            top_k=3,
        )

        print("\nRAG 回答：")
        print(response.answer)

        print("\n执行是否成功：", response.success)

        if response.error:
            print("错误信息：", response.error)

        print_sources(response)


def main() -> None:
    try:
        rag = build_rag()
        interactive_demo(rag)

    except Exception as e:
        print("Day36 运行失败：", e)


if __name__ == "__main__":
    main()