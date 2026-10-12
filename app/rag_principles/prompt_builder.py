from app.rag_principles.schemas import RetrievedChunk


class RAGPromptBuilder:
    def build_context(
        self,
        retrieved_chunks: list[RetrievedChunk],
    ) -> str:
        if not retrieved_chunks:
            return "暂无可用参考资料。"

        context_parts = []

        for index, item in enumerate(retrieved_chunks, start=1):
            chunk = item.chunk

            context_parts.append(
                f"资料 {index}：\n"
                f"标题：{chunk.title}\n"
                f"来源文档：{chunk.document_id}\n"
                f"Chunk：{chunk.chunk_id}\n"
                f"相似度：{item.score:.4f}\n"
                f"内容：{chunk.content}"
            )

        return "\n\n".join(context_parts)

    def build_prompt(
        self,
        question: str,
        retrieved_chunks: list[RetrievedChunk],
    ) -> str:
        context = self.build_context(retrieved_chunks)

        return (
            "你是一个企业知识库问答助手。\n"
            "请严格根据【参考资料】回答用户问题。\n"
            "如果参考资料不足，请回答：根据当前资料无法确认。\n"
            "不要编造参考资料中没有的信息。\n\n"
            f"【参考资料】\n{context}\n\n"
            f"【用户问题】\n{question}\n"
        )