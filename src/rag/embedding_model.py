"""
Embedding Model

作用：
1. 加载预训练 Sentence Transformer 模型
2. 把文本转换成向量
3. 支持批量处理 TextChunk
4. 对向量进行归一化，方便计算余弦相似度
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from src.rag.text_splitter import TextChunk


class EmbeddingModel:
    """
    文本向量模型。

    当前默认使用多语言模型，能够处理中文和英文文本。
    """

    DEFAULT_MODEL_NAME = (
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: str | None = None,
    ) -> None:
        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name_or_path=model_name,
            device=device,
        )

    @property
    def dimension(self) -> int:
        """
        返回当前模型生成的向量维度。
        """

        dimension = self.model.get_sentence_embedding_dimension()

        if dimension is None:
            raise RuntimeError("无法获取 Embedding 向量维度。")

        return dimension

    def encode_texts(
        self,
        texts: list[str],
        batch_size: int = 32,
    ) -> np.ndarray:
        """
        把多个文本转换成二维向量数组。

        返回形状：

            文本数量 × 向量维度

        例如：

            10 个文本 × 384 维
            shape = (10, 384)
        """

        if not texts:
            return np.empty(
                shape=(0, self.dimension),
                dtype=np.float32,
            )

        embeddings = self.model.encode(
            sentences=texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return np.asarray(
            embeddings,
            dtype=np.float32,
        )

    def encode_query(self, query: str) -> np.ndarray:
        """
        把一个用户问题转换成向量。
        """

        query = query.strip()

        if not query:
            raise ValueError("查询文本不能为空。")

        embeddings = self.encode_texts([query])

        return embeddings[0]

    def encode_chunks(
        self,
        chunks: list[TextChunk],
        batch_size: int = 32,
    ) -> np.ndarray:
        """
        把多个 TextChunk 转换成向量。
        """

        texts = [
            chunk.content
            for chunk in chunks
        ]

        return self.encode_texts(
            texts=texts,
            batch_size=batch_size,
        )