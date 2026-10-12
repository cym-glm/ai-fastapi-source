from app.rag_principles.schemas import RetrievedChunk


class SimpleAnswerGenerator:
    """
    教学版回答生成器。

    真实项目里这里会调用 LLM。
    这里为了让代码下载后不用 API Key，也能跑通。
    """

    def generate(
        self,
        question: str,
        retrieved_chunks: list[RetrievedChunk],
    ) -> str:
        if not retrieved_chunks:
            return "根据当前资料无法确认。"

        valid_chunks = [
            item for item in retrieved_chunks
            if item.score > 0
        ]

        if not valid_chunks:
            return "根据当前资料无法确认。"

        best = valid_chunks[0]

        return (
            "根据知识库资料，可以这样回答："
            f"{best.chunk.content}\n\n"
            f"来源：{best.chunk.title} / {best.chunk.chunk_id}"
        )