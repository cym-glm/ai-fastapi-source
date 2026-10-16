from dataclasses import asdict

from app.document_chunking.schemas import ChunkStrategy
from app.enterprise_kb.schemas import KnowledgeChatRequest
from app.enterprise_kb.service import enterprise_kb_service


def prepare_index():
    enterprise_kb_service.index_file(
        file_path="data/sample_docs/after_sales.txt",
        tenant_id="tenant_001",
        created_by="u_10001",
        doc_type="after_sales",
        department="customer_service",
        version="2026-08",
        chunk_strategy=ChunkStrategy.PARAGRAPH,
        chunk_size=120,
        chunk_overlap=20,
    )

    enterprise_kb_service.index_file(
        file_path="data/sample_docs/employee_handbook.md",
        tenant_id="tenant_001",
        created_by="u_10001",
        doc_type="employee_handbook",
        department="hr",
        version="2026-08",
        chunk_strategy=ChunkStrategy.HEADING,
        chunk_size=180,
        chunk_overlap=30,
    )

    enterprise_kb_service.index_file(
        file_path="data/sample_docs/help_center.html",
        tenant_id="tenant_001",
        created_by="u_10001",
        doc_type="help_center",
        department="customer_service",
        version="2026-08",
        chunk_strategy=ChunkStrategy.ELEMENT,
        chunk_size=180,
        chunk_overlap=20,
    )


def main():
    prepare_index()

    questions = [
        "订单还没发货，可以退款吗？",
        "入职多久可以申请年假？",
        "公司班车路线是什么？",
    ]

    for question in questions:
        response = enterprise_kb_service.chat(
            KnowledgeChatRequest(
                question=question,
                tenant_id="tenant_001",
                user_id="u_10001",
                top_k=3,
                metadata_filter=None,
            )
        )

        print("question:", response.question)
        print("query_id:", response.query_id)
        print("answer:", response.answer)
        print("fallback_reason:", response.fallback_reason)

        print("sources:")
        for source in response.sources:
            print(asdict(source))

        print("=" * 120)


if __name__ == "__main__":
    main()