from app.advanced_retrieval.schemas import (
    AdvancedRetrievalRequest,
    RetrievalConfig,
    RetrievalMode,
)
from app.advanced_retrieval.service import advanced_retrieval_service


def main():
    response = advanced_retrieval_service.retrieve(
        AdvancedRetrievalRequest(
            query="没发货可以退款吗？退款多久能到账？",
            config=RetrievalConfig(
                mode=RetrievalMode.HYBRID,
                top_k=3,
                candidate_k=10,
                use_query_rewrite=True,
                use_multi_query=True,
                use_mmr=True,
                use_rerank=True,
                min_score=0.01,
                max_context_chars=800,
                metadata_filter={
                    "tenant_id": "tenant_001",
                },
            ),
        )
    )

    print("context:")
    print(response.context)

    print("=" * 80)
    print("sources:")
    for source in response.sources:
        print(source)


if __name__ == "__main__":
    main()