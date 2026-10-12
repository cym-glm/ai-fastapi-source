from app.document_chunking.demo_utils import print_chunk_result
from app.document_chunking.schemas import ChunkConfig, ChunkStrategy
from app.document_chunking.service import document_chunking_service
from app.document_parsing.demo_04_parse_docx import create_sample_docx
from app.document_parsing.service import document_parsing_service


def main():
    file_path = create_sample_docx()

    parsed_document = document_parsing_service.parse_file(
        file_path,
        tenant_id="tenant_001",
        created_by="u_10001",
    )

    result = document_chunking_service.split_document(
        parsed_document,
        config=ChunkConfig(
            strategy=ChunkStrategy.TABLE_AWARE,
            chunk_size=180,
            chunk_overlap=20,
            min_chunk_size=5,
        ),
    )

    print_chunk_result(result)


if __name__ == "__main__":
    main()