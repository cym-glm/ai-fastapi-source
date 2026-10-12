from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.document_parsing.schemas import ParsedDocument


class ChunkStrategy(str, Enum):
    FIXED_SIZE = "fixed_size"
    PARAGRAPH = "paragraph"
    PAGE = "page"
    ELEMENT = "element"
    HEADING = "heading"
    TABLE_AWARE = "table_aware"
    CODE_AWARE = "code_aware"


@dataclass
class ChunkConfig:
    strategy: ChunkStrategy = ChunkStrategy.PARAGRAPH
    chunk_size: int = 500
    chunk_overlap: int = 80
    min_chunk_size: int = 30
    preserve_metadata: bool = True


@dataclass
class ChunkDocument:
    chunk_id: str
    document_id: str
    title: str
    content: str
    chunk_index: int
    strategy: ChunkStrategy
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkResult:
    document_id: str
    title: str
    total_chunks: int
    strategy: ChunkStrategy
    chunks: list[ChunkDocument]
    warnings: list[str] = field(default_factory=list)


@dataclass
class ChunkRequest:
    parsed_document: ParsedDocument
    config: ChunkConfig