import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from app.dependencies.auth import get_current_user
from app.document_parsing.service import document_parsing_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()

UPLOAD_DIR = Path("data/uploaded_docs")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


class ParsedElementResponse(BaseModel):
    element_id: str
    type: str
    content: str
    page_number: int | None = None
    order_index: int
    metadata: dict


class ParsedDocumentResponse(BaseModel):
    document_id: str
    title: str
    source_path: str
    file_name: str
    file_type: str
    text: str
    status: str
    metadata: dict
    errors: list[str]
    elements: list[ParsedElementResponse]


@router.post(
    "/documents/parse",
    response_model=ApiResponse[ParsedDocumentResponse],
)
async def parse_document(
    file: UploadFile = File(...),
    tenant_id: str = "tenant_001",
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[ParsedDocumentResponse]:
    safe_file_name = Path(file.filename or "uploaded_file").name
    target_path = UPLOAD_DIR / safe_file_name

    with target_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    result = document_parsing_service.parse_file(
        target_path,
        tenant_id=tenant_id,
        created_by=current_user.user_id,
    )

    response = ParsedDocumentResponse(
        document_id=result.document_id,
        title=result.title,
        source_path=result.source_path,
        file_name=result.file_name,
        file_type=result.file_type,
        text=result.text,
        status=result.status.value,
        metadata=result.metadata,
        errors=result.errors,
        elements=[
            ParsedElementResponse(
                element_id=element.element_id,
                type=element.type.value,
                content=element.content,
                page_number=element.page_number,
                order_index=element.order_index,
                metadata=element.metadata,
            )
            for element in result.elements
        ],
    )

    return ApiResponse[ParsedDocumentResponse](
        data=response
    )