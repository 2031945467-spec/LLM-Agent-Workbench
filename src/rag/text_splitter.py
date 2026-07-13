"""
Text Splitter

作用：
1. 把长文档切成多个较小的文本块
2. 支持 Chunk Overlap，保留上下文连续性
3. 为后续 Embedding 和向量检索做准备
"""

from dataclasses import dataclass, field
from typing import Any

from src.rag.document_loader import Document


@dataclass
class TextChunk:
    """
    一个切分后的文本块。

    chunk_id:
        文本块编号

    content:
        文本块内容

    source:
        来自哪个文档

    start_index / end_index:
        该文本块在原文中的字符位置
    """

    chunk_id: int
    content: str
    source: str
    start_index: int
    end_index: int
    metadata: dict[str, Any] = field(default_factory=dict)


class TextSplitter:
    """
    基础字符切块器。

    chunk_size:
        每个文本块最多包含多少个字符

    chunk_overlap:
        相邻文本块重复保留多少个字符
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size 必须大于 0。")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap 不能小于 0。")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap 必须小于 chunk_size。"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_document(
        self,
        document: Document,
        start_chunk_id: int = 1,
    ) -> list[TextChunk]:
        """
        切分单个 Document。
        """

        content = document.content

        if not content.strip():
            return []

        chunks: list[TextChunk] = []

        start = 0
        chunk_id = start_chunk_id
        content_length = len(content)

        while start < content_length:
            end = min(
                start + self.chunk_size,
                content_length,
            )

            chunk_content = content[start:end].strip()

            if chunk_content:
                chunk = TextChunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    source=document.source,
                    start_index=start,
                    end_index=end,
                    metadata={
                        **document.metadata,
                        "chunk_size": len(chunk_content),
                    },
                )

                chunks.append(chunk)
                chunk_id += 1

            if end >= content_length:
                break

            # 下一块向前回退一部分，形成重叠区域
            start = end - self.chunk_overlap

        return chunks

    def split_documents(
        self,
        documents: list[Document],
    ) -> list[TextChunk]:
        """
        切分多个 Document，并保证 chunk_id 连续。
        """

        all_chunks: list[TextChunk] = []
        next_chunk_id = 1

        for document in documents:
            chunks = self.split_document(
                document=document,
                start_chunk_id=next_chunk_id,
            )

            all_chunks.extend(chunks)
            next_chunk_id += len(chunks)

        return all_chunks