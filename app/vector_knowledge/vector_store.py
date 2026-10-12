from app.vector_knowledge.schemas import (
    EmbeddedChunk,
    VectorSearchResult,
)
from app.vector_knowledge.similarity import cosine_similarity


class InMemoryVectorStore:
    """
    教学版 Vector Store。

    特点：
    1. 不依赖外部数据库。
    2. 支持 add / delete / search。
    3. 支持 metadata_filter。
    4. 只用于教学，不适合生产。
    """

    def __init__(self):
        self.items: dict[str, EmbeddedChunk] = {}

    def add(
        self,
        embedded_chunk: EmbeddedChunk,
    ) -> None:
        self.items[embedded_chunk.chunk_id] = embedded_chunk

    def add_many(
        self,
        embedded_chunks: list[EmbeddedChunk],
    ) -> None:
        for item in embedded_chunks:
            self.add(item)

    def delete(
        self,
        chunk_id: str,
    ) -> None:
        self.items.pop(
            chunk_id,
            None,
        )

    def delete_by_document_id(
        self,
        document_id: str,
    ) -> int:
        chunk_ids = [
            chunk_id
            for chunk_id, item in self.items.items()
            if item.document_id == document_id
        ]

        for chunk_id in chunk_ids:
            self.delete(chunk_id)

        return len(chunk_ids)

    def clear(self) -> None:
        self.items.clear()

    def count(self) -> int:
        return len(self.items)

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        metadata_filter: dict | None = None,
    ) -> list[VectorSearchResult]:
        candidates = list(self.items.values())

        if metadata_filter:
            candidates = [
                item for item in candidates
                if self._match_metadata_filter(
                    item.metadata,
                    metadata_filter,
                )
            ]

        results: list[VectorSearchResult] = []

        for item in candidates:
            score = cosine_similarity(
                query_embedding,
                item.embedding,
            )

            results.append(
                VectorSearchResult(
                    chunk_id=item.chunk_id,
                    document_id=item.document_id,
                    content=item.content,
                    score=score,
                    metadata=item.metadata,
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return results[:top_k]

    def _match_metadata_filter(
        self,
        metadata: dict,
        metadata_filter: dict,
    ) -> bool:
        for key, expected_value in metadata_filter.items():
            actual_value = metadata.get(key)

            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            else:
                if actual_value != expected_value:
                    return False

        return True