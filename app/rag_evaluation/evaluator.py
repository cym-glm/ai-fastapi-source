from dataclasses import asdict

from app.rag_evaluation.answer_generator import SimpleGroundedAnswerGenerator
from app.rag_evaluation.metrics import (
    calculate_answer_correctness,
    calculate_answer_relevance,
    calculate_citation_accuracy,
    calculate_context_relevance,
    calculate_hit_rate,
    calculate_mrr,
    calculate_ndcg_at_k,
    calculate_precision_at_k,
    calculate_recall_at_k,
    calculate_rule_based_faithfulness,
    calculate_source_accuracy,
)
from app.rag_evaluation.schemas import (
    GeneratedAnswerForEval,
    GenerationEvaluationResult,
    RAGEvaluationCase,
    RetrievalEvaluationResult,
    RetrievedItemForEval,
)
from app.advanced_retrieval.schemas import (
    AdvancedRetrievalRequest,
    RetrievalConfig,
)
from app.advanced_retrieval.service import advanced_retrieval_service


class RAGEvaluator:
    def __init__(self):
        self.answer_generator = SimpleGroundedAnswerGenerator()

    def evaluate_retrieval_case(
        self,
        case: RAGEvaluationCase,
        config: RetrievalConfig,
    ) -> RetrievalEvaluationResult:
        effective_config = self._merge_case_filter(
            config=config,
            case=case,
        )

        response = advanced_retrieval_service.retrieve(
            AdvancedRetrievalRequest(
                query=case.question,
                config=effective_config,
            )
        )

        retrieved_chunk_ids = [
            item.chunk_id
            for item in response.results
        ]

        retrieved_items = [
            RetrievedItemForEval(
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                content=item.content,
                score=item.final_score,
                source_path=item.metadata.get("source_path"),
                metadata=item.metadata,
            )
            for item in response.results
        ]

        k = config.top_k

        return RetrievalEvaluationResult(
            case_id=case.case_id,
            question=case.question,
            retrieved_chunk_ids=retrieved_chunk_ids,
            expected_chunk_ids=case.expected_chunk_ids,
            hit_rate=calculate_hit_rate(
                case.expected_chunk_ids,
                retrieved_chunk_ids,
            ),
            recall_at_k=calculate_recall_at_k(
                case.expected_chunk_ids,
                retrieved_chunk_ids[:k],
            ),
            precision_at_k=calculate_precision_at_k(
                case.expected_chunk_ids,
                retrieved_chunk_ids,
                k=k,
            ),
            mrr=calculate_mrr(
                case.expected_chunk_ids,
                retrieved_chunk_ids,
            ),
            ndcg_at_k=calculate_ndcg_at_k(
                case.expected_chunk_ids,
                retrieved_chunk_ids,
                k=k,
            ),
            source_accuracy=calculate_source_accuracy(
                case.expected_source_paths,
                retrieved_items,
            ),
        )

    def evaluate_generation_case(
        self,
        case: RAGEvaluationCase,
        config: RetrievalConfig,
    ) -> GenerationEvaluationResult:
        effective_config = self._merge_case_filter(
            config=config,
            case=case,
        )

        retrieval_response = advanced_retrieval_service.retrieve(
            AdvancedRetrievalRequest(
                query=case.question,
                config=effective_config,
            )
        )

        answer = self.answer_generator.generate(
            query=case.question,
            retrieval_response=retrieval_response,
        )

        generated = GeneratedAnswerForEval(
            answer=answer,
            sources=retrieval_response.sources,
            context=retrieval_response.context,
        )

        faithfulness, unsupported_claims = calculate_rule_based_faithfulness(
            generated
        )

        answer_relevance = calculate_answer_relevance(
            case,
            generated,
        )

        answer_correctness = calculate_answer_correctness(
            case,
            generated,
        )

        context_relevance = calculate_context_relevance(
            case,
            generated,
        )

        citation_accuracy = calculate_citation_accuracy(
            case,
            generated,
        )

        _coverage, missing_keywords = calculate_answer_relevance_with_missing(
            case,
            generated,
        )

        return GenerationEvaluationResult(
            case_id=case.case_id,
            question=case.question,
            answer=answer,
            faithfulness=faithfulness,
            answer_relevance=answer_relevance,
            answer_correctness=answer_correctness,
            context_relevance=context_relevance,
            citation_accuracy=citation_accuracy,
            missing_keywords=missing_keywords,
            unsupported_claims=unsupported_claims,
        )

    def _merge_case_filter(
        self,
        config: RetrievalConfig,
        case: RAGEvaluationCase,
    ) -> RetrievalConfig:
        merged_filter = dict(config.metadata_filter or {})

        for key, value in case.metadata_filter.items():
            merged_filter[key] = value

        return RetrievalConfig(
            mode=config.mode,
            top_k=config.top_k,
            candidate_k=config.candidate_k,
            vector_weight=config.vector_weight,
            keyword_weight=config.keyword_weight,
            use_query_rewrite=config.use_query_rewrite,
            use_multi_query=config.use_multi_query,
            use_mmr=config.use_mmr,
            use_rerank=config.use_rerank,
            min_score=config.min_score,
            max_context_chars=config.max_context_chars,
            metadata_filter=merged_filter or None,
        )


def calculate_answer_relevance_with_missing(
    case: RAGEvaluationCase,
    generated: GeneratedAnswerForEval,
) -> tuple[float, list[str]]:
    from app.rag_evaluation.metrics import calculate_keyword_coverage

    return calculate_keyword_coverage(
        expected_keywords=case.expected_answer_keywords,
        text=generated.answer,
    )


def to_dict(obj):
    return asdict(obj)