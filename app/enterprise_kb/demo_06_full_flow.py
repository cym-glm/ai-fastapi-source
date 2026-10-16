from dataclasses import asdict

from app.document_chunking.schemas import ChunkStrategy
from app.enterprise_kb.schemas import (
    FeedbackRating,
    KnowledgeChatRequest,
)
from app.enterprise_kb.service import enterprise_kb_service


def main():
    print("1. 索引文档")
    files = [
        {
            "file_path": "data/sample_docs/after_sales.txt",
            "doc_type": "after_sales",
            "department": "customer_service",
            "strategy": ChunkStrategy.PARAGRAPH,
        },
        {
            "file_path": "data/sample_docs/employee_handbook.md",
            "doc_type": "employee_handbook",
            "department": "hr",
            "strategy": ChunkStrategy.HEADING,
        },
        {
            "file_path": "data/sample_docs/help_center.html",
            "doc_type": "help_center",
            "department": "customer_service",
            "strategy": ChunkStrategy.ELEMENT,
        },
    ]

    for item in files:
        result = enterprise_kb_service.index_file(
            file_path=item["file_path"],
            tenant_id="tenant_001",
            created_by="u_10001",
            doc_type=item["doc_type"],
            department=item["department"],
            version="2026-08",
            chunk_strategy=item["strategy"],
            chunk_size=180,
            chunk_overlap=30,
        )

        print(result.message, result.document.file_name, result.chunk_count)

    print("=" * 120)
    print("2. 查看知识库统计")

    stats = enterprise_kb_service.get_stats(
        tenant_id="tenant_001"
    )
    print(asdict(stats))

    print("=" * 120)
    print("3. 用户提问")

    response = enterprise_kb_service.chat(
        KnowledgeChatRequest(
            question="订单还没发货，可以退款吗？",
            tenant_id="tenant_001",
            user_id="u_10001",
            top_k=3,
        )
    )

    print("query_id:", response.query_id)
    print("answer:", response.answer)
    print("sources:")
    for source in response.sources:
        print(asdict(source))

    print("=" * 120)
    print("4. 提交反馈")

    feedback = enterprise_kb_service.submit_feedback(
        query_id=response.query_id,
        tenant_id="tenant_001",
        user_id="u_10001",
        rating=FeedbackRating.GOOD,
        comment="回答准确，来源清楚。",
    )
    print(asdict(feedback))

    print("=" * 120)
    print("5. 查看 Query Logs")

    logs = enterprise_kb_service.list_query_logs(
        tenant_id="tenant_001",
        limit=10,
    )

    for log in logs:
        print(asdict(log))

    print("=" * 120)
    print("6. 运行 Evaluation")

    report = enterprise_kb_service.run_evaluation()
    print("retrieval_metrics:", report["retrieval_metrics"])
    print("generation_metrics:", report["generation_metrics"])


if __name__ == "__main__":
    main()