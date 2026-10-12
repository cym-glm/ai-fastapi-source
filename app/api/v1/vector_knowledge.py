from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.document_chunking.schemas import ChunkStrategy
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
from app.vector_knowledge.schemas import VectorSearchRequest
from app.vector_knowledge.service import vector_knowledge_service


router = APIRouter()


class IndexFileRequest(BaseModel):
    file_path: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")
    chunk_strategy: str = Field(default="heading")
    chunk_size: int = Field(default=500, gt=0)
    chunk_overlap: int = Field(default=80, ge=0)


class SearchKnowledgeRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    metadata_filter: dict[str, Any] | None = None


@router.post(
    "/knowledge/index-file",
    response_model=ApiResponse[dict],
)
async def index_file(
    request: IndexFileRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = vector_knowledge_service.index_file(
        file_path=request.file_path,
        tenant_id=request.tenant_id,
        created_by=current_user.user_id,
        chunk_strategy=ChunkStrategy(request.chunk_strategy),
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )

    return ApiResponse[dict](
        data={
            "total_chunks": result.total_chunks,
            "embedded_chunks": result.embedded_chunks,
            "provider": result.provider.value,
            "vector_store": result.vector_store.value,
            "warnings": result.warnings,
        }
    )


@router.post(
    "/knowledge/search",
    response_model=ApiResponse[dict],
)
async def search_knowledge(
    request: SearchKnowledgeRequest,
) -> ApiResponse[dict]:
    response = vector_knowledge_service.search(
        VectorSearchRequest(
            query=request.query,
            top_k=request.top_k,
            metadata_filter=request.metadata_filter,
        )
    )

    return ApiResponse[dict](
        data={
            "query": response.query,
            "top_k": response.top_k,
            "results": [
                {
                    "chunk_id": item.chunk_id,
                    "document_id": item.document_id,
                    "content": item.content,
                    "score": item.score,
                    "metadata": item.metadata,
                }
                for item in response.results
            ],
        }
    )


@router.delete(
    "/knowledge/index",
    response_model=ApiResponse[dict],
)
async def clear_index() -> ApiResponse[dict]:
    vector_knowledge_service.clear_index()

    return ApiResponse[dict](
        data={
            "message": "向量索引已清空",
            "count": vector_knowledge_service.count(),
        }
    )