from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.document_chunking.schemas import ChunkConfig, ChunkStrategy
from app.document_chunking.service import document_chunking_service
from app.document_parsing.service import document_parsing_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class ChunkFileRequest(BaseModel):
    file_path: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")
    strategy: Literal[
        "fixed_size",
        "paragraph",
        "page",
        "element",
        "heading",
        "table_aware",
        "code_aware",
    ] = "paragraph"
    chunk_size: int = Field(default=500, gt=0)
    chunk_overlap: int = Field(default=80, ge=0)
    min_chunk_size: int = Field(default=30, ge=0)


@router.post(
    "/documents/chunk",
    response_model=ApiResponse[dict],
)
async def chunk_document(
    request: ChunkFileRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    parsed_document = document_parsing_service.parse_file(
        file_path=request.file_path,
        tenant_id=request.tenant_id,
        created_by=current_user.user_id,
    )

    config = ChunkConfig(
        strategy=ChunkStrategy(request.strategy),
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
        min_chunk_size=request.min_chunk_size,
    )

    result = document_chunking_service.split_document(
        document=parsed_document,
        config=config,
    )

    return ApiResponse[dict](
        data={
            "document_id": result.document_id,
            "title": result.title,
            "strategy": result.strategy.value,
            "total_chunks": result.total_chunks,
            "warnings": result.warnings,
            "chunks": [
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "strategy": chunk.strategy.value,
                    "metadata": chunk.metadata,
                }
                for chunk in result.chunks
            ],
        }
    )