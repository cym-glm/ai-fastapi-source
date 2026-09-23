from typing import Any

from pydantic import BaseModel, Field

from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger
from app.langchain_rag.chains import build_rag_chain
from app.langchain_rag.documents import load_markdown_documents
from app.langchain_rag.splitters import split_documents
from app.langchain_rag.vector_store import rebuild_vector_store


logger = get_logger(__name__)


class RAGSource(BaseModel):
    document_id: str | None = Field(default=None)
    chunk_id: str | None = Field(default=None)
    source: str | None = Field(default=None)
    content_preview: str = Field(default="")


class RAGAnswer(BaseModel):
    answer: str = Field(..., description="RAG 回答")
    sources: list[RAGSource] = Field(
        default_factory=list,
        description="引用来源",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="扩展信息",
    )


class LangChainRAGService:
    def rebuild_index(self) -> dict:
        documents = load_markdown_documents()
        chunks = split_documents(documents)

        rebuild_vector_store(chunks)

        return {
            "document_count": len(documents),
            "chunk_count": len(chunks),
        }

    def ask(
        self,
        question: str,
        provider: str = "deepseek",
        model_name: str = "deepseek-chat",
        k: int = 4,
    ) -> RAGAnswer:
        logger.info(
            f"langchain_rag_ask_start model={model_name} k={k}"
        )

        try:
            chain = build_rag_chain(
                provider=provider,
                model_name=model_name,
                k=k,
            )

            result = chain.invoke({
                "question": question,
            })

        except Exception as exc:
            logger.exception("langchain_rag_ask_failed")

            raise AppException(
                message="LangChain RAG 问答失败",
                code=ErrorCode.LLM_CALL_FAILED,
                status_code=500,
                data={
                    "error": repr(exc),
                    "provider": provider,
                    "model": model_name,
                },
            ) from exc

        sources = [
            RAGSource(**item)
            for item in result.get("sources", [])
        ]

        return RAGAnswer(
            answer=result["answer"],
            sources=sources,
            metadata={
                "provider": provider,
                "model": model_name,
                "k": k,
                "source_count": len(sources),
            },
        )


langchain_rag_service = LangChainRAGService()