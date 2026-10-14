from app.rag_evaluation.dataset import load_golden_dataset
from app.rag_evaluation.metrics import (
    calculate_answer_correctness,
    calculate_answer_relevance,
    calculate_citation_accuracy,
    calculate_context_relevance,
    calculate_rule_based_faithfulness,
)
from app.rag_evaluation.schemas import GeneratedAnswerForEval


def main():
    case = load_golden_dataset()[0]

    generated = GeneratedAnswerForEval(
        answer="根据资料，订单未发货时，用户可以申请取消订单并退款。",
        context="订单未发货时，用户可以申请取消订单并退款。",
        sources=[
            {
                "source_path": "data/sample_docs/after_sales.txt",
                "chunk_id": "after_sales_001",
            }
        ],
    )

    faithfulness, unsupported_claims = calculate_rule_based_faithfulness(
        generated
    )

    print("case:", case.case_id)
    print("question:", case.question)
    print("=" * 80)

    print("faithfulness:", faithfulness)
    print("unsupported_claims:", unsupported_claims)
    print("answer_relevance:", calculate_answer_relevance(case, generated))
    print("answer_correctness:", calculate_answer_correctness(case, generated))
    print("context_relevance:", calculate_context_relevance(case, generated))
    print("citation_accuracy:", calculate_citation_accuracy(case, generated))


if __name__ == "__main__":
    main()