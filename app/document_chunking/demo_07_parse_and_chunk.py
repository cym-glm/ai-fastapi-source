from app.document_chunking.demo_utils import print_chunk_result
from app.document_chunking.schemas import ChunkConfig, ChunkStrategy
from app.document_chunking.service import document_chunking_service
from app.document_parsing.service import document_parsing_service


def run_case(
    file_path: str,
    strategy: ChunkStrategy,
):
    print("文件:", file_path)
    print("策略:", strategy)
    print("=" * 80)

    parsed_document = document_parsing_service.parse_file(
        file_path,
        tenant_id="tenant_001",
        created_by="u_10001",
    )

    result = document_chunking_service.split_document(
        parsed_document,
        config=ChunkConfig(
            strategy=strategy,
            chunk_size=180,
            chunk_overlap=30,
            min_chunk_size=10,
        ),
    )

    print_chunk_result(result)


def main():
    cases = [
        ("data/sample_docs/after_sales.txt", ChunkStrategy.PARAGRAPH),
        ("data/sample_docs/employee_handbook.md", ChunkStrategy.HEADING),
        ("data/sample_docs/help_center.html", ChunkStrategy.ELEMENT),
    ]

    for file_path, strategy in cases:
        run_case(file_path, strategy)
        print("=" * 120)


if __name__ == "__main__":
    main()