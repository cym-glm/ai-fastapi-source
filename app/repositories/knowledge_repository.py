from typing import Any

from app.schemas.chat import SourceDocument


class KnowledgeRepository:
    async def search_documents(
        self,
        question: str,
        knowledge_base_id: str,
        top_k: int,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[SourceDocument]:
        return [
            SourceDocument(
                document_id="doc_001",
                title="AI Agent 课程资料",
                content="RAG 是检索增强生成，用于让大模型结合外部知识回答问题。",
                score=0.92,
                metadata={
                    "knowledge_base_id": knowledge_base_id,
                    "page": 1,
                    "filter": metadata_filter or {},
                },
            )
        ][:top_k]


knowledge_repository = KnowledgeRepository()