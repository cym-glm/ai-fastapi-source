from app.document_chunking.demo_utils import print_chunk_result
from app.document_chunking.schemas import ChunkConfig, ChunkStrategy
from app.document_chunking.service import document_chunking_service
from app.document_parsing.service import document_parsing_service


def main():
    parsed_document = document_parsing_service.parse_file(
        "data/sample_docs/employee_handbook.md",
        tenant_id="tenant_001",
        created_by="u_10001",
    )

    result = document_chunking_service.split_document(
        parsed_document,
        config=ChunkConfig(
            strategy=ChunkStrategy.PARAGRAPH,
            chunk_size=120,
            chunk_overlap=20,
            min_chunk_size=10,
        ),
    )

    print_chunk_result(result)


if __name__ == "__main__":
    main()