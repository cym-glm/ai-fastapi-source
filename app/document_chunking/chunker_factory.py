from app.document_chunking.chunkers import (
    BaseChunker,
    CodeAwareChunker,
    ElementChunker,
    FixedSizeChunker,
    HeadingChunker,
    PageChunker,
    ParagraphChunker,
    TableAwareChunker,
)
from app.document_chunking.schemas import (
    ChunkConfig,
    ChunkStrategy,
)


class DocumentChunkerFactory:
    def create_chunker(
        self,
        config: ChunkConfig,
    ) -> BaseChunker:
        if config.strategy == ChunkStrategy.FIXED_SIZE:
            return FixedSizeChunker(config)

        if config.strategy == ChunkStrategy.PARAGRAPH:
            return ParagraphChunker(config)

        if config.strategy == ChunkStrategy.PAGE:
            return PageChunker(config)

        if config.strategy == ChunkStrategy.ELEMENT:
            return ElementChunker(config)

        if config.strategy == ChunkStrategy.HEADING:
            return HeadingChunker(config)

        if config.strategy == ChunkStrategy.TABLE_AWARE:
            return TableAwareChunker(config)

        if config.strategy == ChunkStrategy.CODE_AWARE:
            return CodeAwareChunker(config)

        raise ValueError(
            f"不支持的 Chunk 策略：{config.strategy}"
        )