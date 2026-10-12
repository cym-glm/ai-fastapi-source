from app.document_chunking.schemas import ChunkStrategy
from app.vector_knowledge.schemas import VectorSearchRequest
from app.vector_knowledge.service import VectorKnowledgeService


def main():
    service = VectorKnowledgeService()

    service.index_file(
        file_path="data/sample_docs/after_sales.txt",
        tenant_id="tenant_001",
        created_by="u_10001",
        chunk_strategy=ChunkStrategy.PARAGRAPH,
        chunk_size=120,
        chunk_overlap=20,
    )

    print("first count:", service.count())

    response = service.search(
        VectorSearchRequest(
            query="退款规则是什么？",
            top_k=3,
        )
    )

    print("first search:")
    for item in response.results:
        print(item.chunk_id, round(item.score, 4), item.content)

    print("=" * 80)

    service.clear_index()

    print("after clear count:", service.count())

    service.index_file(
        file_path="data/sample_docs/after_sales.txt",
        tenant_id="tenant_001",
        created_by="u_10001",
        chunk_strategy=ChunkStrategy.PARAGRAPH,
        chunk_size=80,
        chunk_overlap=10,
    )

    print("second count:", service.count())

    response = service.search(
        VectorSearchRequest(
            query="退款规则是什么？",
            top_k=3,
        )
    )

    print("second search:")
    for item in response.results:
        print(item.chunk_id, round(item.score, 4), item.content)


if __name__ == "__main__":
    main()