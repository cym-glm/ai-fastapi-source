from dataclasses import asdict
from statistics import mean

from app.advanced_retrieval.schemas import (
    RetrievalConfig,
    RetrievalMode,
)
from app.rag_evaluation.dataset import load_golden_dataset
from app.rag_evaluation.evaluator import RAGEvaluator
from app.rag_evaluation.schemas import (
    EvaluationReport,
    StrategyComparisonResult,
)


class RAGExperimentRunner:
    def __init__(self):
        self.evaluator = RAGEvaluator()

    def run_report(
        self,
        name: str,
        config: RetrievalConfig,
    ) -> EvaluationReport:
        cases = load_golden_dataset()

        retrieval_results = []
        generation_results = []
        case_results = []

        for case in cases:
            retrieval_result = self.evaluator.evaluate_retrieval_case(
                case=case,
                config=config,
            )

            generation_result = self.evaluator.evaluate_generation_case(
                case=case,
                config=config,
            )

            retrieval_results.append(retrieval_result)
            generation_results.append(generation_result)

            case_results.append({
                "case": asdict(case),
                "retrieval": asdict(retrieval_result),
                "generation": asdict(generation_result),
            })

        retrieval_metrics = {
            "hit_rate": _mean([item.hit_rate for item in retrieval_results]),
            "recall_at_k": _mean([item.recall_at_k for item in retrieval_results]),
            "precision_at_k": _mean([item.precision_at_k for item in retrieval_results]),
            "mrr": _mean([item.mrr for item in retrieval_results]),
            "ndcg_at_k": _mean([item.ndcg_at_k for item in retrieval_results]),
            "source_accuracy": _mean([item.source_accuracy for item in retrieval_results]),
        }

        generation_metrics = {
            "faithfulness": _mean([item.faithfulness for item in generation_results]),
            "answer_relevance": _mean([item.answer_relevance for item in generation_results]),
            "answer_correctness": _mean([item.answer_correctness for item in generation_results]),
            "context_relevance": _mean([item.context_relevance for item in generation_results]),
            "citation_accuracy": _mean([item.citation_accuracy for item in generation_results]),
        }

        return EvaluationReport(
            name=name,
            total_cases=len(cases),
            retrieval_metrics=retrieval_metrics,
            generation_metrics=generation_metrics,
            case_results=case_results,
            config={
                "mode": config.mode.value,
                "top_k": config.top_k,
                "candidate_k": config.candidate_k,
                "vector_weight": config.vector_weight,
                "keyword_weight": config.keyword_weight,
                "use_query_rewrite": config.use_query_rewrite,
                "use_multi_query": config.use_multi_query,
                "use_mmr": config.use_mmr,
                "use_rerank": config.use_rerank,
                "min_score": config.min_score,
                "max_context_chars": config.max_context_chars,
                "metadata_filter": config.metadata_filter,
            },
        )

    def compare_strategies(self) -> list[StrategyComparisonResult]:
        strategies = [
            (
                "vector_only",
                RetrievalConfig(
                    mode=RetrievalMode.VECTOR,
                    top_k=3,
                    candidate_k=10,
                    use_query_rewrite=False,
                    use_multi_query=False,
                    use_mmr=False,
                    use_rerank=False,
                    min_score=0.01,
                    metadata_filter={
                        "tenant_id": "tenant_001",
                    },
                ),
            ),
            (
                "hybrid_basic",
                RetrievalConfig(
                    mode=RetrievalMode.HYBRID,
                    top_k=3,
                    candidate_k=10,
                    use_query_rewrite=False,
                    use_multi_query=False,
                    use_mmr=False,
                    use_rerank=False,
                    min_score=0.01,
                    metadata_filter={
                        "tenant_id": "tenant_001",
                    },
                ),
            ),
            (
                "hybrid_rewrite_multi",
                RetrievalConfig(
                    mode=RetrievalMode.HYBRID,
                    top_k=3,
                    candidate_k=10,
                    use_query_rewrite=True,
                    use_multi_query=True,
                    use_mmr=False,
                    use_rerank=False,
                    min_score=0.01,
                    metadata_filter={
                        "tenant_id": "tenant_001",
                    },
                ),
            ),
            (
                "hybrid_full",
                RetrievalConfig(
                    mode=RetrievalMode.HYBRID,
                    top_k=3,
                    candidate_k=10,
                    use_query_rewrite=True,
                    use_multi_query=True,
                    use_mmr=True,
                    use_rerank=True,
                    min_score=0.01,
                    metadata_filter={
                        "tenant_id": "tenant_001",
                    },
                ),
            ),
        ]

        results: list[StrategyComparisonResult] = []

        for strategy_name, config in strategies:
            report = self.run_report(
                name=strategy_name,
                config=config,
            )

            results.append(
                StrategyComparisonResult(
                    strategy_name=strategy_name,
                    report=report,
                )
            )

        return results


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0

    return mean(values)