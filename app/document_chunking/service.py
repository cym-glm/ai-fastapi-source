from app.document_chunking.chunker_factory import DocumentChunkerFactory
from app.document_chunking.schemas import (
    ChunkConfig,
    ChunkResult,
    ChunkStrategy,
)
from app.document_parsing.schemas import ParsedDocument


class DocumentChunkingService:
    def __init__(self):
        self.factory = DocumentChunkerFactory()

    def split_document(
        self,
        document: ParsedDocument,
        config: ChunkConfig | None = None,
    ) -> ChunkResult:
        if config is None:
            config = ChunkConfig(
                strategy=ChunkStrategy.PARAGRAPH,
                chunk_size=500,
                chunk_overlap=80,
            )

        chunker = self.factory.create_chunker(config)

        return chunker.split(document)

    def split_with_strategy(
        self,
        document: ParsedDocument,
        strategy: ChunkStrategy,
        chunk_size: int = 500,
        chunk_overlap: int = 80,
        min_chunk_size: int = 30,
    ) -> ChunkResult:
        config = ChunkConfig(
            strategy=strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            min_chunk_size=min_chunk_size,
        )

        return self.split_document(
            document=document,
            config=config,
        )


document_chunking_service = DocumentChunkingService()