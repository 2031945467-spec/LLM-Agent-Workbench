"""
Day35: Embedding + FAISS Demo

流程：
1. 加载 docs 文件夹
2. 把文档切成 TextChunk
3. 把 TextChunk 转换成 Embedding
4. 加入 FAISS 向量库
5. 根据用户问题搜索相关文本块

运行方式：
    python -m examples.day35_embedding_faiss_demo
"""

from src.rag.document_loader import DocumentLoader
from src.rag.embedding_model import EmbeddingModel
from src.rag.text_splitter import TextSplitter
from src.rag.vector_store import FaissVectorStore


def build_vector_store() -> tuple[
    EmbeddingModel,
    FaissVectorStore,
]:
    """
    构建一个内存中的向量库。
    """

    print("1. 正在加载文档……")

    loader = DocumentLoader(base_dir=".")

    documents = loader.load_directory(
        directory_path="docs",
        recursive=True,
    )

    if not documents:
        raise RuntimeError(
            "docs 目录中没有可加载的文档。"
        )

    print(f"已加载文档数量：{len(documents)}")

    print("\n2. 正在切分文档……")

    splitter = TextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise RuntimeError(
            "没有生成任何文本块。"
        )

    print(f"文本块数量：{len(chunks)}")

    print("\n3. 正在加载 Embedding 模型……")

    embedding_model = EmbeddingModel()

    print("模型名称：", embedding_model.model_name)
    print("向量维度：", embedding_model.dimension)

    print("\n4. 正在生成文本向量……")

    embeddings = embedding_model.encode_chunks(
        chunks=chunks,
        batch_size=32,
    )

    print("向量数组形状：", embeddings.shape)

    print("\n5. 正在建立 FAISS 索引……")

    vector_store = FaissVectorStore(
        dimension=embedding_model.dimension,
    )

    vector_store.add(
        chunks=chunks,
        embeddings=embeddings,
    )

    print("索引中的向量数量：", vector_store.size)

    return embedding_model, vector_store


def print_search_results(results) -> None:
    """
    打印搜索结果。
    """

    if not results:
        print("没有搜索到结果。")
        return

    print("\n========== Search Results ==========")

    for rank, result in enumerate(
        results,
        start=1,
    ):
        chunk = result.chunk

        print("\n" + "-" * 70)
        print(f"Rank：{rank}")
        print(f"Score：{result.score:.4f}")
        print(
            "Source：",
            chunk.metadata.get(
                "relative_path",
                chunk.source,
            ),
        )
        print(f"Chunk ID：{chunk.chunk_id}")
        print(
            "Position：",
            f"{chunk.start_index}-{chunk.end_index}",
        )
        print("Content：")
        print(chunk.content[:700])


def interactive_search(
    embedding_model: EmbeddingModel,
    vector_store: FaissVectorStore,
) -> None:
    """
    用户输入问题，执行向量检索。
    """

    print("\n========== Day35 Semantic Search ==========")
    print("输入 q 退出")
    print("-------------------------------------------")
    print("示例：")
    print("Planner 的作用是什么？")
    print("项目中有哪些 Agent 工具？")
    print("短期记忆和长期记忆有什么区别？")
    print("-------------------------------------------")

    while True:
        query = input("\n查询问题：").strip()

        if query.lower() == "q":
            print("已退出向量搜索。")
            break

        if not query:
            print("查询内容不能为空。")
            continue

        query_embedding = embedding_model.encode_query(
            query
        )

        results = vector_store.search(
            query_embedding=query_embedding,
            top_k=3,
        )

        print_search_results(results)


def main() -> None:
    try:
        embedding_model, vector_store = (
            build_vector_store()
        )

        interactive_search(
            embedding_model=embedding_model,
            vector_store=vector_store,
        )

    except Exception as e:
        print("Day35 运行失败：", e)


if __name__ == "__main__":
    main()