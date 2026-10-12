from app.document_chunking.schemas import (
    ChunkConfig,
    ChunkDocument,
    ChunkStrategy,
)
from app.document_chunking.service import document_chunking_service
from app.document_parsing.service import document_parsing_service
from app.vector_knowledge.embedding import EmbeddingModelFactory
from app.vector_knowledge.schemas import (
    EmbeddedChunk,
    EmbeddingConfig,
    IndexBuildResult,
    VectorSearchRequest,
    VectorSearchResponse,
    VectorStoreProvider,
)
from app.vector_knowledge.vector_store import InMemoryVectorStore


class EmbeddingService:
    def __init__(
        self,
        config: EmbeddingConfig | None = None,
    ):
        self.config = config or EmbeddingConfig()
        self.model = EmbeddingModelFactory().create(self.config)

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        return self.model.embed_text(text)

    def embed_chunks(
        self,
        chunks: list[ChunkDocument],
    ) -> list[EmbeddedChunk]:
        texts = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = self.model.embed_texts(texts)

        embedded_chunks: list[EmbeddedChunk] = []

        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append(
                EmbeddedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    embedding=embedding,
                    metadata={
                        **chunk.metadata,
                        "embedding_provider": self.config.provider.value,
                        "embedding_model": self.config.model_name,
                        "embedding_dimension": self.config.dimension,
                    },
                )
            )

        return embedded_chunks


class VectorKnowledgeService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = InMemoryVectorStore()

    def index_chunks(
        self,
        chunks: list[ChunkDocument],
    ) -> IndexBuildResult:
        embedded_chunks = self.embedding_service.embed_chunks(
            chunks
        )

        self.vector_store.add_many(
            embedded_chunks
        )

        return IndexBuildResult(
            total_chunks=len(chunks),
            embedded_chunks=len(embedded_chunks),
            provider=self.embedding_service.config.provider,
            vector_store=VectorStoreProvider.IN_MEMORY,
            warnings=[
                "当前使用 InMemoryVectorStore，仅适合教学和本地 Demo。"
            ],
        )

    def index_file(
        self,
        file_path: str,
        tenant_id: str = "tenant_001",
        created_by: str = "system",
        chunk_strategy: ChunkStrategy = ChunkStrategy.HEADING,
        chunk_size: int = 500,
        chunk_overlap: int = 80,
    ) -> IndexBuildResult:
        parsed_document = document_parsing_service.parse_file(
            file_path=file_path,
            tenant_id=tenant_id,
            created_by=created_by,
        )

        chunk_result = document_chunking_service.split_document(
            parsed_document,
            config=ChunkConfig(
                strategy=chunk_strategy,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                min_chunk_size=10,
            ),
        )

        return self.index_chunks(
            chunk_result.chunks
        )

    def search(
        self,
        request: VectorSearchRequest,
    ) -> VectorSearchResponse:
        query_embedding = self.embedding_service.embed_text(
            request.query
        )

        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=request.top_k,
            metadata_filter=request.metadata_filter,
        )

        return VectorSearchResponse(
            query=request.query,
            top_k=request.top_k,
            results=results,
        )

    def clear_index(self) -> None:
        self.vector_store.clear()

    def count(self) -> int:
        return self.vector_store.count()


vector_knowledge_service = VectorKnowledgeService()