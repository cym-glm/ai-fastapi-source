from app.advanced_retrieval.schemas import RetrievalMode
from app.rag_evaluation.service import rag_evaluation_service


def main():
    result = rag_evaluation_service.evaluate_generation(
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
        print("answer:", item["answer"])
        print("faithfulness:", round(item["faithfulness"], 4))
        print("answer_relevance:", round(item["answer_relevance"], 4))
        print("answer_correctness:", round(item["answer_correctness"], 4))
        print("context_relevance:", round(item["context_relevance"], 4))
        print("citation_accuracy:", round(item["citation_accuracy"], 4))
        print("missing_keywords:", item["missing_keywords"])
        print("unsupported_claims:", item["unsupported_claims"])
        print("-" * 80)


if __name__ == "__main__":
    main()