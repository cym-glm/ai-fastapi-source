from app.document_chunking.schemas import ChunkStrategy
from app.vector_knowledge.schemas import VectorSearchRequest
from app.vector_knowledge.service import VectorKnowledgeService


def main():
    service = VectorKnowledgeService()

    files = [
        "data/sample_docs/after_sales.txt",
        "data/sample_docs/employee_handbook.md",
        "data/sample_docs/help_center.html",
    ]

    for file_path in files:
        result = service.index_file(
            file_path=file_path,
            tenant_id="tenant_001",
            created_by="u_10001",
            chunk_strategy=ChunkStrategy.HEADING,
            chunk_size=180,
            chunk_overlap=30,
        )

        print("indexed:", file_path)
        print(result)
        print("-" * 80)

    print("vector count:", service.count())
    print("=" * 120)

    questions = [
        "订单还没发货，可以退款吗？",
        "年假制度是什么？",
        "帮助中心可以查什么问题？",
        "企业发票需要什么？",
    ]

    for question in questions:
        response = service.search(
            VectorSearchRequest(
                query=question,
                top_k=3,
                metadata_filter={
                    "tenant_id": "tenant_001",
                },
            )
        )

        print("question:", question)
        for item in response.results:
            print("score:", round(item.score, 4))
            print("content:", item.content)
            print("source:", item.metadata.get("source_path"))
            print("heading:", item.metadata.get("heading"))
            print("-" * 80)

        print("=" * 120)


if __name__ == "__main__":
    main()