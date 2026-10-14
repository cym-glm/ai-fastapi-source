from app.advanced_retrieval.schemas import (
    AdvancedRetrievalRequest,
    RetrievalConfig,
    RetrievalMode,
)
from app.advanced_retrieval.service import advanced_retrieval_service


def main():
    cases = [
        "我刚买的课还没开始学，现在不想要了怎么办？",
        "快递超过 7 天没动怎么办？",
        "企业发票需要填写什么？",
        "年假怎么申请？",
        "公司班车路线是什么？",
    ]

    for query in cases:
        response = advanced_retrieval_service.retrieve(
            AdvancedRetrievalRequest(
                query=query,
                config=RetrievalConfig(
                    mode=RetrievalMode.HYBRID,
                    top_k=3,
                    candidate_k=10,
                    vector_weight=0.7,
                    keyword_weight=0.3,
                    use_query_rewrite=True,
                    use_multi_query=True,
                    use_mmr=True,
                    use_rerank=True,
                    min_score=0.05,
                    max_context_chars=1200,
                    metadata_filter={
                        "tenant_id": "tenant_001",
                    },
                ),
            )
        )

        print("original_query:", response.original_query)
        print("rewritten_query:", response.rewritten_query)
        print("queries:", response.queries)
        print("fallback_reason:", response.fallback_reason)

        print("=" * 80)
        print("results:")
        for item in response.results:
            print("chunk_id:", item.chunk_id)
            print("score:", round(item.final_score, 4))
            print("matched_by:", item.matched_by)
            print("heading:", item.metadata.get("heading"))
            print("content:", item.content)
            print("-" * 80)

        print("context:")
        print(response.context)

        print("=" * 120)


if __name__ == "__main__":
    main()