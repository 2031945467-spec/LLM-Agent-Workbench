"""
Basic RAG Chain

作用：
1. 接收用户问题
2. 使用 Retriever 检索相关文本块
3. 将检索结果拼接为上下文
4. 让 LLM 基于上下文生成回答
"""

from dataclasses import dataclass, field
from typing import Any

from src.llm.client import LLMClient
from src.rag.retriever import Retriever
from src.rag.vector_store import SearchResult


@dataclass
class RAGResponse:
    """
    RAG 问答的统一返回结果。
    """

    query: str
    answer: str
    success: bool
    retrieved_results: list[SearchResult] = field(
        default_factory=list
    )
    error: str | None = None

    def get_sources(self) -> list[dict[str, Any]]:
        """
        提取适合展示的来源信息。
        """

        sources = []

        for result in self.retrieved_results:
            chunk = result.chunk

            sources.append(
                {
                    "score": result.score,
                    "source": chunk.metadata.get(
                        "relative_path",
                        chunk.source,
                    ),
                    "chunk_id": chunk.chunk_id,
                    "start_index": chunk.start_index,
                    "end_index": chunk.end_index,
                }
            )

        return sources


class BasicRAG:
    """
    基础 RAG 问答链。

    流程：

        用户问题
        → Retriever
        → 相关文本块
        → 构造上下文
        → LLM 回答
    """

    def __init__(
        self,
        client: LLMClient,
        retriever: Retriever,
        max_context_chars: int = 6000,
    ) -> None:
        if max_context_chars <= 0:
            raise ValueError(
                "max_context_chars 必须大于 0。"
            )

        self.client = client
        self.retriever = retriever
        self.max_context_chars = max_context_chars

    def ask(
        self,
        query: str,
        top_k: int | None = None,
    ) -> RAGResponse:
        """
        执行一次 RAG 问答。
        """

        query = query.strip()

        if not query:
            return RAGResponse(
                query=query,
                answer="请输入问题。",
                success=False,
                error="用户问题为空。",
            )

        try:
            # 第一步：检索相关文本块
            results = self.retriever.retrieve(
                query=query,
                top_k=top_k,
            )

            if not results:
                return RAGResponse(
                    query=query,
                    answer="知识库中没有检索到相关内容。",
                    success=False,
                    retrieved_results=[],
                    error="检索结果为空。",
                )

            # 第二步：把检索结果构造成上下文
            context = self._build_context(results)

            # 第三步：构造 RAG Prompt
            prompt = self._build_prompt(
                query=query,
                context=context,
            )

            # 第四步：让 LLM 基于检索内容回答
            answer = self.client.chat(
                user_message=prompt,
                system_prompt=(
                    "你是一个知识库问答助手。"
                    "必须优先根据提供的参考资料回答，"
                    "不要编造资料中没有的信息。"
                ),
                history=[],
            )

            return RAGResponse(
                query=query,
                answer=answer,
                success=True,
                retrieved_results=results,
            )

        except Exception as e:
            return RAGResponse(
                query=query,
                answer=f"RAG 问答失败：{e}",
                success=False,
                error=str(e),
            )

    def _build_context(
        self,
        results: list[SearchResult],
    ) -> str:
        """
        把多个检索结果拼接成上下文。
        """

        context_parts: list[str] = []
        current_length = 0

        for index, result in enumerate(
            results,
            start=1,
        ):
            chunk = result.chunk

            source = chunk.metadata.get(
                "relative_path",
                chunk.source,
            )

            part = f"""
[参考资料 {index}]
来源：{source}
文本块编号：{chunk.chunk_id}
相似度：{result.score:.4f}

{chunk.content}
""".strip()

            # 防止拼接后的上下文过长
            remaining_length = (
                self.max_context_chars - current_length
            )

            if remaining_length <= 0:
                break

            if len(part) > remaining_length:
                part = part[:remaining_length]

            context_parts.append(part)
            current_length += len(part)

        return "\n\n".join(context_parts)

    @staticmethod
    def _build_prompt(
        query: str,
        context: str,
    ) -> str:
        """
        构造发送给大模型的 RAG Prompt。
        """

        return f"""
请根据下面的参考资料回答用户问题。

用户问题：

{query}

参考资料：

{context}

回答要求：

1. 优先依据参考资料回答
2. 不要编造参考资料中没有的信息
3. 如果资料不足，请明确说明“根据当前资料无法确定”
4. 使用中文回答
5. 回答后标明使用了哪些参考资料，例如：[参考资料 1]
6. 不要仅复制原文，要组织成自然、清晰的回答
"""