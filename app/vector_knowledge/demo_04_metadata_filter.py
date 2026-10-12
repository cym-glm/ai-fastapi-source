from app.vector_knowledge.demo_03_vector_store import build_mock_chunks
from app.vector_knowledge.schemas import VectorSearchRequest
from app.vector_knowledge.service import VectorKnowledgeService


def print_results(title: str, response):
    print(title)
    print("=" * 80)

    for result in response.results:
        print("chunk_id:", result.chunk_id)
        print("score:", round(result.score, 4))
        print("doc_type:", result.metadata.get("doc_type"))
        print("content:", result.content)
        print("-" * 80)

    print("=" * 120)


def main():
    service = VectorKnowledgeService()
    service.index_chunks(build_mock_chunks())

    no_filter = service.search(
        VectorSearchRequest(
            query="退款规则是什么？",
            top_k=3,
        )
    )

    print_results("不加 filter", no_filter)

    after_sales_filter = service.search(
        VectorSearchRequest(
            query="退款规则是什么？",
            top_k=3,
            metadata_filter={
                "doc_type": "after_sales",
            },
        )
    )

    print_results("只查售后规则", after_sales_filter)

    invoice_filter = service.search(
        VectorSearchRequest(
            query="退款规则是什么？",
            top_k=3,
            metadata_filter={
                "doc_type": "invoice",
            },
        )
    )

    print_results("只查发票规则", invoice_filter)


if __name__ == "__main__":
    main()