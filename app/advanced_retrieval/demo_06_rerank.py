from app.advanced_retrieval.schemas import (
    AdvancedRetrievalRequest,
    RetrievalConfig,
    RetrievalMode,
)
from app.advanced_retrieval.service import advanced_retrieval_service


def run_case(use_rerank: bool):
    response = advanced_retrieval_service.retrieve(
        AdvancedRetrievalRequest(
            query="企业发票需要填写什么？",
            config=RetrievalConfig(
                mode=RetrievalMode.HYBRID,
                top_k=3,
                candidate_k=10,
                use_query_rewrite=True,
                use_multi_query=True,
                use_mmr=False,
                use_rerank=use_rerank,
                min_score=0.01,
                metadata_filter={
                    "tenant_id": "tenant_001",
                },
            ),
        )
    )

    print("use_rerank:", use_rerank)

    for item in response.results:
        print("chunk:", item.chunk_id)
        print("score:", round(item.final_score, 4))
        print("heading:", item.metadata.get("heading"))
        print("content:", item.content)
        print("-" * 80)

    print("=" * 120)


def main():
    run_case(use_rerank=False)
    run_case(use_rerank=True)


if __name__ == "__main__":
    main()