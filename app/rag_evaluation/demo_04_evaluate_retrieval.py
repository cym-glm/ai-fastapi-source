from dataclasses import asdict

from app.advanced_retrieval.schemas import RetrievalMode
from app.rag_evaluation.service import rag_evaluation_service


def main():
    result = rag_evaluation_service.evaluate_retrieval(
        mode=RetrievalMode.HYBRID,
        top_k=3,
        use_query_rewrite=True,
        use_multi_query=True,
        use_mmr=True,
        use_rerank=True,
    )

    print("total_cases:", result["total_cases"])
    print("=" * 80)

    for item in result["results"]:
        print("case_id:", item["case_id"])
        print("question:", item["question"])
        print("expected:", item["expected_chunk_ids"])
        print("retrieved:", item["retrieved_chunk_ids"])
        print("hit_rate:", item["hit_rate"])
        print("recall_at_k:", round(item["recall_at_k"], 4))
        print("precision_at_k:", round(item["precision_at_k"], 4))
        print("mrr:", round(item["mrr"], 4))
        print("ndcg_at_k:", round(item["ndcg_at_k"], 4))
        print("source_accuracy:", item["source_accuracy"])
        print("-" * 80)


if __name__ == "__main__":
    main()