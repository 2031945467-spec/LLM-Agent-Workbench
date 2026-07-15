"""
Retriever

作用：
1. 接收用户问题
2. 把问题转换为查询向量
3. 从 FAISS 向量库中检索相关文本块
4. 返回相似度最高的 SearchResult
"""

from src.rag.embedding_model import EmbeddingModel
from src.rag.vector_store import FaissVectorStore, SearchResult


class Retriever:
    """
    基础向量检索器。

    EmbeddingModel 负责：
        用户问题 → 查询向量

    FaissVectorStore 负责：
        查询向量 → 相似文本块
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: FaissVectorStore,
        default_top_k: int = 3,
    ) -> None:
        if default_top_k <= 0:
            raise ValueError("default_top_k 必须大于 0。")

        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.default_top_k = default_top_k

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[SearchResult]:
        """
        根据用户问题检索相关文本块。
        """

        query = query.strip()

        if not query:
            raise ValueError("查询内容不能为空。")

        real_top_k = (
            top_k
            if top_k is not None
            else self.default_top_k
        )

        if real_top_k <= 0:
            raise ValueError("top_k 必须大于 0。")

        # 1. 用户问题转向量
        query_embedding = self.embedding_model.encode_query(
            query
        )

        # 2. 在 FAISS 中搜索相关文本块
        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=real_top_k,
        )