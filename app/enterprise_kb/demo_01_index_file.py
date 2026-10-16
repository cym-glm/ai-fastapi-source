from dataclasses import asdict

from app.document_chunking.schemas import ChunkStrategy
from app.enterprise_kb.service import enterprise_kb_service


def main():
    result = enterprise_kb_service.index_file(
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

    print("message:", result.message)
    print("chunk_count:", result.chunk_count)
    print("document:")
    print(asdict(result.document))


if __name__ == "__main__":
    main()