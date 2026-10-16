from dataclasses import asdict

from app.document_chunking.schemas import ChunkStrategy
from app.enterprise_kb.schemas import KnowledgeChatRequest
from app.enterprise_kb.service import enterprise_kb_service


def main():
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

    enterprise_kb_service.chat(
        KnowledgeChatRequest(
            question="没发货可以退款吗？",
            tenant_id="tenant_001",
            user_id="u_10001",
            top_k=3,
        )
    )

    enterprise_kb_service.chat(
        KnowledgeChatRequest(
            question="退款多久到账？",
            tenant_id="tenant_001",
            user_id="u_10001",
            top_k=3,
        )
    )

    logs = enterprise_kb_service.list_query_logs(
        tenant_id="tenant_001",
        limit=10,
    )

    for log in logs:
        print(asdict(log))
        print("-" * 100)


if __name__ == "__main__":
    main()