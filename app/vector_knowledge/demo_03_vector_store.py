from app.document_chunking.schemas import ChunkDocument, ChunkStrategy
from app.vector_knowledge.schemas import VectorSearchRequest
from app.vector_knowledge.service import VectorKnowledgeService


def build_mock_chunks() -> list[ChunkDocument]:
    return [
        ChunkDocument(
            chunk_id="chunk_after_sales_001",
            document_id="doc_after_sales",
            title="电商售后规则",
            content="订单未发货时，用户可以申请取消订单并退款。",
            chunk_index=0,
            strategy=ChunkStrategy.PARAGRAPH,
            metadata={
                "tenant_id": "tenant_001",
                "doc_type": "after_sales",
                "source_path": "after_sales.txt",
            },
        ),
        ChunkDocument(
            chunk_id="chunk_logistics_001",
            document_id="doc_logistics",
            title="物流说明",
            content="物流超过 7 天没有更新，建议联系客服协助核查。",
            chunk_index=0,
            strategy=ChunkStrategy.PARAGRAPH,
            metadata={
                "tenant_id": "tenant_001",
                "doc_type": "logistics",
                "source_path": "logistics.txt",
            },
        ),
        ChunkDocument(
            chunk_id="chunk_invoice_001",
            document_id="doc_invoice",
            title="发票规则",
            content="企业发票需要填写公司名称和纳税人识别号。",
            chunk_index=0,
            strategy=ChunkStrategy.PARAGRAPH,
            metadata={
                "tenant_id": "tenant_001",
                "doc_type": "invoice",
                "source_path": "invoice.txt",
            },
        ),
    ]


def main():
    service = VectorKnowledgeService()

    chunks = build_mock_chunks()

    index_result = service.index_chunks(chunks)

    print("index_result:")
    print(index_result)
    print("=" * 80)

    response = service.search(
        VectorSearchRequest(
            query="没发货可以退款吗？",
            top_k=3,
        )
    )

    print("search response:")
    for result in response.results:
        print("chunk_id:", result.chunk_id)
        print("score:", round(result.score, 4))
        print("content:", result.content)
        print("metadata:", result.metadata)
        print("-" * 80)


if __name__ == "__main__":
    main()