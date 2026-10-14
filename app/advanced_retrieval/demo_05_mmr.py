from app.advanced_retrieval.schemas import (
    AdvancedRetrievalRequest,
    RetrievalConfig,
    RetrievalMode,
)
from app.advanced_retrieval.service import advanced_retrieval_service


def run_case(use_mmr: bool):
    response = advanced_retrieval_service.retrieve(
        AdvancedRetrievalRequest(
            query="退款和售后规则是什么？",
            config=RetrievalConfig(
                mode=RetrievalMode.HYBRID,
                top_k=4,
                candidate_k=10,
                use_query_rewrite=True,
                use_multi_query=True,
                use_mmr=use_mmr,
                use_rerank=False,
                min_score=0.01,
                metadata_filter={
                    "tenant_id": "tenant_001",
                },
            ),
        )
    )

    print("use_mmr:", use_mmr)

    for item in response.results:
        print(item.chunk_id, round(item.final_score, 4), item.metadata.get("heading"))
        print(item.content)
        print("-" * 80)

    print("=" * 120)


def main():
    run_case(use_mmr=False)
    run_case(use_mmr=True)


if __name__ == "__main__":
    main()