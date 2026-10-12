
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal


class ParsedElementType(str, Enum):
    TITLE = "title"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    LIST = "list"
    CODE = "code"
    PAGE_TEXT = "page_text"
    UNKNOWN = "unknown"


class ParseStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    NEED_OCR = "need_ocr"
    UNSUPPORTED = "unsupported"


@dataclass
class ParsedElement:
    element_id: str
    type: ParsedElementType
    content: str
    page_number: int | None = None
    order_index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDocument:
    document_id: str
    title: str
    source_path: str
    file_name: str
    file_type: str
    text: str
    elements: list[ParsedElement]
    status: ParseStatus
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass
class ParseRequest:
    file_path: str
    tenant_id: str = "tenant_001"
    created_by: str = "system"


@dataclass
class ParseDirectoryResult:
    total: int
    success: int
    failed: int
    documents: list[ParsedDocument]


SUPPORTED_FILE_TYPES: set[str] = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
    ".pdf",
}


def get_file_type(file_path: str | Path) -> str:
    path = Path(file_path)
    return path.suffix.lower()