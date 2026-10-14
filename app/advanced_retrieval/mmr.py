from app.advanced_retrieval.schemas import HybridSearchResult
from app.vector_knowledge.similarity import cosine_similarity
from app.vector_knowledge.service import VectorKnowledgeService


class MMRSelector:
    def __init__(
        self,
        vector_service: VectorKnowledgeService,
    ):
        self.vector_service = vector_service

    def select(
        self,
        query: str,
        candidates: list[HybridSearchResult],
        top_k: int,
        lambda_mult: float = 0.7,
    ) -> list[HybridSearchResult]:
        if not candidates:
            return []

        if top_k >= len(candidates):
            return candidates

        query_embedding = self.vector_service.embedding_service.embed_text(
            query
        )

        candidate_embeddings = {
            item.chunk_id: self.vector_service.embedding_service.embed_text(
                item.content
            )
            for item in candidates
        }

        selected: list[HybridSearchResult] = []
        remaining = candidates[:]

        while remaining and len(selected) < top_k:
            best_item = None
            best_score = -999999.0

            for item in remaining:
                relevance = cosine_similarity(
                    query_embedding,
                    candidate_embeddings[item.chunk_id],
                )

                if not selected:
                    diversity_penalty = 0.0
                else:
                    diversity_penalty = max(
                        cosine_similarity(
                            candidate_embeddings[item.chunk_id],
                            candidate_embeddings[selected_item.chunk_id],
                        )
                        for selected_item in selected
                    )

                mmr_score = (
                    lambda_mult * relevance
                    - (1 - lambda_mult) * diversity_penalty
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_item = item

            if best_item is None:
                break

            selected.append(best_item)
            remaining = [
                item for item in remaining
                if item.chunk_id != best_item.chunk_id
            ]

        return selected