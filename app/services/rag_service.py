import uuid

from app.schemas.chat import SourceDocument, TokenUsage
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.repositories.knowledge_repository import knowledge_repository

from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger

logger = get_logger(__name__)

async def query_rag(request: RAGQueryRequest) -> RAGQueryResponse:

    logger.info(
        f"rag_query_start knowledge_base_id={request.knowledge_base_id} top_k={request.top_k}"
    )

    sources = await knowledge_repository.search_documents(
        question=request.question,
        knowledge_base_id=request.knowledge_base_id,
        top_k=request.top_k,
        metadata_filter=request.metadata_filter,
    )
    # source = SourceDocument(
    #     document_id="doc_001",
    #     title="AI Agent 课程资料",
    #     content="RAG 是检索增强生成，用于让大模型结合外部知识回答问题。",
    #     score=0.92,
    #     metadata={
    #         "knowledge_base_id": request.knowledge_base_id,
    #         "page": 1,
    #     },
    # )
    answer = f"根据知识库 {request.knowledge_base_id} 的内容，RAG 是检索增强生成。"

    logger.info(
        f"rag_query_success knowledge_base_id={request.knowledge_base_id} source_count={len(answer)}"
    )

    return RAGQueryResponse(
        answer=answer,
        knowledge_base_id=request.knowledge_base_id,
        sources=sources,
        usage=TokenUsage(
            prompt_tokens=len(request.question),
            completion_tokens=len(answer),
            total_tokens=len(request.question) + len(answer),
        ),
        trace_id=f"trace_{uuid.uuid4().hex[:8]}",
    )