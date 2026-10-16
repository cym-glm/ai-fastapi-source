from dataclasses import asdict
from typing import Any, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.document_chunking.schemas import ChunkStrategy
from app.enterprise_kb.schemas import (
    FeedbackRating,
    KnowledgeChatRequest,
)
from app.enterprise_kb.service import enterprise_kb_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class IndexFileApiRequest(BaseModel):
    file_path: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")
    doc_type: str | None = None
    department: str | None = None
    version: str = "v1"
    chunk_strategy: Literal[
        "fixed_size",
        "paragraph",
        "page",
        "element",
        "heading",
        "table_aware",
        "code_aware",
    ] = "heading"
    chunk_size: int = Field(default=500, gt=0)
    chunk_overlap: int = Field(default=80, ge=0)


class ChatApiRequest(BaseModel):
    question: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")
    top_k: int = Field(default=3, ge=1, le=20)
    metadata_filter: dict[str, Any] | None = None


class FeedbackApiRequest(BaseModel):
    query_id: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")
    rating: Literal["good", "bad", "unknown"] = "unknown"
    comment: str = ""


@router.post(
    "/enterprise-kb/documents/index-file",
    response_model=ApiResponse[dict],
)
async def index_file(
    request: IndexFileApiRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = enterprise_kb_service.index_file(
        file_path=request.file_path,
        tenant_id=request.tenant_id,
        created_by=current_user.user_id,
        doc_type=request.doc_type,
        department=request.department,
        version=request.version,
        chunk_strategy=ChunkStrategy(request.chunk_strategy),
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )

    return ApiResponse[dict](
        data={
            "message": result.message,
            "chunk_count": result.chunk_count,
            "document": asdict(result.document),
        }
    )


@router.get(
    "/enterprise-kb/documents",
    response_model=ApiResponse[list[dict]],
)
async def list_documents(
    tenant_id: str = "tenant_001",
) -> ApiResponse[list[dict]]:
    documents = enterprise_kb_service.list_documents(
        tenant_id=tenant_id
    )

    return ApiResponse[list[dict]](
        data=[
            asdict(document)
            for document in documents
        ]
    )


@router.post(
    "/enterprise-kb/chat",
    response_model=ApiResponse[dict],
)
async def chat(
    request: ChatApiRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    response = enterprise_kb_service.chat(
        KnowledgeChatRequest(
            question=request.question,
            tenant_id=request.tenant_id,
            user_id=current_user.user_id,
            top_k=request.top_k,
            metadata_filter=request.metadata_filter,
        )
    )

    return ApiResponse[dict](
        data={
            "query_id": response.query_id,
            "question": response.question,
            "answer": response.answer,
            "sources": [
                asdict(source)
                for source in response.sources
            ],
            "fallback_reason": response.fallback_reason,
            "debug": response.debug,
        }
    )


@router.get(
    "/enterprise-kb/query-logs",
    response_model=ApiResponse[list[dict]],
)
async def list_query_logs(
    tenant_id: str = "tenant_001",
    limit: int = 20,
) -> ApiResponse[list[dict]]:
    logs = enterprise_kb_service.list_query_logs(
        tenant_id=tenant_id,
        limit=limit,
    )

    return ApiResponse[list[dict]](
        data=[
            asdict(log)
            for log in logs
        ]
    )


@router.post(
    "/enterprise-kb/feedback",
    response_model=ApiResponse[dict],
)
async def submit_feedback(
    request: FeedbackApiRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    feedback = enterprise_kb_service.submit_feedback(
        query_id=request.query_id,
        tenant_id=request.tenant_id,
        user_id=current_user.user_id,
        rating=FeedbackRating(request.rating),
        comment=request.comment,
    )

    return ApiResponse[dict](
        data=asdict(feedback)
    )


@router.get(
    "/enterprise-kb/feedbacks",
    response_model=ApiResponse[list[dict]],
)
async def list_feedbacks(
    tenant_id: str = "tenant_001",
    limit: int = 20,
) -> ApiResponse[list[dict]]:
    feedbacks = enterprise_kb_service.list_feedbacks(
        tenant_id=tenant_id,
        limit=limit,
    )

    return ApiResponse[list[dict]](
        data=[
            asdict(feedback)
            for feedback in feedbacks
        ]
    )


@router.get(
    "/enterprise-kb/stats",
    response_model=ApiResponse[dict],
)
async def get_stats(
    tenant_id: str = "tenant_001",
) -> ApiResponse[dict]:
    stats = enterprise_kb_service.get_stats(
        tenant_id=tenant_id
    )

    return ApiResponse[dict](
        data=asdict(stats)
    )


@router.post(
    "/enterprise-kb/evaluation",
    response_model=ApiResponse[dict],
)
async def run_evaluation() -> ApiResponse[dict]:
    report = enterprise_kb_service.run_evaluation()

    return ApiResponse[dict](
        data=report
    )