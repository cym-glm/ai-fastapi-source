from app.advanced_retrieval.keyword_search import SimpleKeywordSearchEngine
from app.advanced_retrieval.schemas import (
    HybridSearchResult,
    RetrievalConfig,
)
from app.vector_knowledge.schemas import (
    VectorSearchRequest,
)
from app.vector_knowledge.service import VectorKnowledgeService


class HybridRetriever:
    def __init__(
        self,
        vector_service: VectorKnowledgeService,
        keyword_engine: SimpleKeywordSearchEngine,
    ):
        self.vector_service = vector_service
        self.keyword_engine = keyword_engine

    def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> list[HybridSearchResult]:
        merged: dict[str, HybridSearchResult] = {}

        if config.mode.value in ["vector", "hybrid"]:
            vector_response = self.vector_service.search(
                VectorSearchRequest(
                    query=query,
                    top_k=config.candidate_k,
                    metadata_filter=config.metadata_filter,
                )
            )

            for item in vector_response.results:
                merged[item.chunk_id] = HybridSearchResult(
                    chunk_id=item.chunk_id,
                    document_id=item.document_id,
                    content=item.content,
                    vector_score=item.score,
                    keyword_score=0.0,
                    final_score=item.score * config.vector_weight,
                    metadata=item.metadata,
                    matched_by=["vector"],
                )

        if config.mode.value in ["keyword", "hybrid"]:
            keyword_results = self.keyword_engine.search(
                query=query,
                top_k=config.candidate_k,
                metadata_filter=config.metadata_filter,
            )

            for item in keyword_results:
                existing = merged.get(item.chunk_id)

                if existing:
                    existing.keyword_score = item.score
                    existing.final_score += item.score * config.keyword_weight

                    if "keyword" not in existing.matched_by:
                        existing.matched_by.append("keyword")
                else:
                    merged[item.chunk_id] = HybridSearchResult(
                        chunk_id=item.chunk_id,
                        document_id=item.document_id,
                        content=item.content,
                        vector_score=0.0,
                        keyword_score=item.score,
                        final_score=item.score * config.keyword_weight,
                        metadata=item.metadata,
                        matched_by=["keyword"],
                    )

        results = list(merged.values())

        results.sort(
            key=lambda item: item.final_score,
            reverse=True,
        )

        return results[:config.candidate_k]