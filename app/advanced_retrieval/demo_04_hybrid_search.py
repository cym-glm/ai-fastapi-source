from app.advanced_retrieval.schemas import (
    AdvancedRetrievalRequest,
    RetrievalConfig,
    RetrievalMode,
)
from app.advanced_retrieval.service import advanced_retrieval_service


def main():
    queries = [
        "没发货能退钱吗？",
        "物流超过 7 天没动怎么办？",
        "企业发票需要填写什么？",
    ]

    for query in queries:
        response = advanced_retrieval_service.retrieve(
            AdvancedRetrievalRequest(
                query=query,
                config=RetrievalConfig(
                    mode=RetrievalMode.HYBRID,
                    top_k=5,
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
            )
        )

        print("query:", query)
        print("rewritten:", response.rewritten_query)
        print("expanded queries:", response.queries)
        print("results:")

        for item in response.results:
            print("chunk_id:", item.chunk_id)
            print("final_score:", round(item.final_score, 4))
            print("vector_score:", round(item.vector_score, 4))
            print("keyword_score:", round(item.keyword_score, 4))
            print("matched_by:", item.matched_by)
            print("content:", item.content)
            print("-" * 80)

        print("=" * 120)


if __name__ == "__main__":
    main()