from dataclasses import asdict

from app.document_chunking.schemas import ChunkStrategy
from app.enterprise_kb.schemas import (
    FeedbackRating,
    KnowledgeChatRequest,
)
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

    response = enterprise_kb_service.chat(
        KnowledgeChatRequest(
            question="没发货可以退钱吗？",
            tenant_id="tenant_001",
            user_id="u_10001",
            top_k=3,
        )
    )

    feedback = enterprise_kb_service.submit_feedback(
        query_id=response.query_id,
        tenant_id="tenant_001",
        user_id="u_10001",
        rating=FeedbackRating.GOOD,
        comment="回答准确，有来源。",
    )

    print("query_id:", response.query_id)
    print("answer:", response.answer)

    print("=" * 80)
    print("feedback:")
    print(asdict(feedback))


if __name__ == "__main__":
    main()