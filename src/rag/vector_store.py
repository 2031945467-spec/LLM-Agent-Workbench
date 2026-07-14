from dataclasses import dataclass

import faiss
import numpy as np

from src.rag.text_splitter import TextChunk

@dataclass
class SearchResult:
    score:float
    chunk:TextChunk
    
class FaissVectorStore:
    def __init__(self,dimension:int)->None:
        if dimension <= 0:
            raise ValueError("向量维度必须大于 0。")
        
        self.dimension=dimension
        
        self.index=faiss.IndexFlatIP(dimension)
        
        self.chunks:list[TextChunk]=[]
        
    @property
    def size(self)->int:
        return self.index.ntotal
    
    def add(
        self,
        chunks:list[TextChunk],
        embeddings:np.ndarray,
    )->None:
        if not chunks:
            return
        
        embeddings=np.asarray(
            embeddings,
            dtype=np.float32,
        )
        
        if embeddings.ndim != 2:
            raise ValueError(
                "embeddings 必须是二维数组。"
            )
        
        if len(chunks) != embeddings.shape[0]:
            raise ValueError(
                "文本块数量和向量数量不一致。"
            )
            
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                "向量维度不匹配："
                f"期望 {self.dimension},"
                f"实际 {embeddings.shape[1]}。"
            )
            
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)
        self.chunks.extend(chunks)
        
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 3,
    ) -> list[SearchResult]:
        """
        搜索与查询向量最相似的文本块。
        """

        if self.size == 0:
            return []

        if top_k <= 0:
            raise ValueError("top_k 必须大于 0。")

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        # 单个向量 (384,) 转成二维数组 (1, 384)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        if query_embedding.ndim != 2:
            raise ValueError(
                "query_embedding 必须是一维或二维数组。"
            )

        if query_embedding.shape[1] != self.dimension:
            raise ValueError(
                "查询向量维度不匹配。"
            )

        faiss.normalize_L2(query_embedding)

        real_top_k = min(top_k, self.size)

        scores, indices = self.index.search(
            query_embedding,
            real_top_k,
        )

        results: list[SearchResult] = []

        for score, index_position in zip(
            scores[0],
            indices[0],
        ):
            # FAISS 在无结果时可能返回 -1
            if index_position < 0:
                continue

            results.append(
                SearchResult(
                    score=float(score),
                    chunk=self.chunks[index_position],
                )
            )

        return results