import math

from app.rag_principles.schemas import (
    ChunkDocument,
    EmbeddedChunk,
    RetrievedChunk,
)


def cosine_similarity(
    left: list[float],
    right: list[float],
) -> float:
    if len(left) != len(right):
        raise ValueError("两个向量长度必须一致")

    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot / (left_norm * right_norm)


class SimpleVectorStore:
    def __init__(self):
        self.items: list[EmbeddedChunk] = []

    def add_documents(
        self,
        chunks: list[ChunkDocument],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks 和 embeddings 数量必须一致")

        for chunk, embedding in zip(chunks, embeddings):
            self.items.append(
                EmbeddedChunk(
                    chunk=chunk,
                    embedding=embedding,
                )
            )

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> list[RetrievedChunk]:
        candidates = self.items

        if metadata_filter:
            candidates = [
                item for item in candidates
                if all(
                    item.chunk.metadata.get(key) == value
                    for key, value in metadata_filter.items()
                )
            ]

        scored: list[RetrievedChunk] = []

        for item in candidates:
            score = cosine_similarity(
                query_embedding,
                item.embedding,
            )

            scored.append(
                RetrievedChunk(
                    chunk=item.chunk,
                    score=score,
                )
            )

        scored.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return scored[:top_k]