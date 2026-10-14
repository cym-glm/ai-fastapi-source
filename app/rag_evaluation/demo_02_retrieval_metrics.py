from app.rag_evaluation.metrics import (
    calculate_hit_rate,
    calculate_mrr,
    calculate_ndcg_at_k,
    calculate_precision_at_k,
    calculate_recall_at_k,
)


def main():
    expected = ["a", "b", "c"]
    retrieved = ["x", "a", "y", "b", "z"]

    k = 5

    print("expected:", expected)
    print("retrieved:", retrieved)
    print("=" * 80)

    print("Hit Rate:", calculate_hit_rate(expected, retrieved))
    print("Recall@K:", calculate_recall_at_k(expected, retrieved[:k]))
    print("Precision@K:", calculate_precision_at_k(expected, retrieved, k))
    print("MRR:", calculate_mrr(expected, retrieved))
    print("NDCG@K:", calculate_ndcg_at_k(expected, retrieved, k))


if __name__ == "__main__":
    main()