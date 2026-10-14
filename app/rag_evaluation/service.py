from dataclasses import asdict

from app.advanced_retrieval.schemas import (
    RetrievalConfig,
    RetrievalMode,
)
from app.rag_evaluation.dataset import load_golden_dataset
from app.rag_evaluation.evaluator import RAGEvaluator
from app.rag_evaluation.experiments import RAGExperimentRunner


class RAGEvaluationService:
    def __init__(self):
        self.evaluator = RAGEvaluator()
        self.runner = RAGExperimentRunner()

    def list_cases(self) -> list[dict]:
        return [
            asdict(case)
            for case in load_golden_dataset()
        ]

    def evaluate_retrieval(
        self,
        mode: RetrievalMode = RetrievalMode.HYBRID,
        top_k: int = 3,
        use_query_rewrite: bool = True,
        use_multi_query: bool = True,
        use_mmr: bool = True,
        use_rerank: bool = True,
    ) -> dict:
        config = RetrievalConfig(
            mode=mode,
            top_k=top_k,
            candidate_k=10,
            use_query_rewrite=use_query_rewrite,
            use_multi_query=use_multi_query,
            use_mmr=use_mmr,
            use_rerank=use_rerank,
            min_score=0.01,
            metadata_filter={
                "tenant_id": "tenant_001",
            },
        )

        cases = load_golden_dataset()

        results = [
            self.evaluator.evaluate_retrieval_case(
                case=case,
                config=config,
            )
            for case in cases
        ]

        return {
            "total_cases": len(cases),
            "results": [
                asdict(result)
                for result in results
            ],
        }

    def evaluate_generation(
        self,
        mode: RetrievalMode = RetrievalMode.HYBRID,
        top_k: int = 3,
        use_query_rewrite: bool = True,
        use_multi_query: bool = True,
        use_mmr: bool = True,
        use_rerank: bool = True,
    ) -> dict:
        config = RetrievalConfig(
            mode=mode,
            top_k=top_k,
            candidate_k=10,
            use_query_rewrite=use_query_rewrite,
            use_multi_query=use_multi_query,
            use_mmr=use_mmr,
            use_rerank=use_rerank,
            min_score=0.01,
            metadata_filter={
                "tenant_id": "tenant_001",
            },
        )

        cases = load_golden_dataset()

        results = [
            self.evaluator.evaluate_generation_case(
                case=case,
                config=config,
            )
            for case in cases
        ]

        return {
            "total_cases": len(cases),
            "results": [
                asdict(result)
                for result in results
            ],
        }

    def run_full_report(self) -> dict:
        config = RetrievalConfig(
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
        )

        report = self.runner.run_report(
            name="default_hybrid_full",
            config=config,
        )

        return asdict(report)

    def compare_strategies(self) -> list[dict]:
        results = self.runner.compare_strategies()

        return [
            {
                "strategy_name": item.strategy_name,
                "report": asdict(item.report),
            }
            for item in results
        ]


rag_evaluation_service = RAGEvaluationService()