from pathlib import Path

from app.document_parsing.parser_factory import DocumentParserFactory
from app.document_parsing.schemas import (
    ParsedDocument,
    ParseDirectoryResult,
    ParseStatus,
    SUPPORTED_FILE_TYPES,
)


class DocumentParsingService:
    def __init__(self):
        self.factory = DocumentParserFactory()

    def parse_file(
        self,
        file_path: str | Path,
        tenant_id: str = "tenant_001",
        created_by: str = "system",
    ) -> ParsedDocument:
        path = Path(file_path)

        if not path.exists():
            return ParsedDocument(
                document_id="",
                title=path.stem,
                source_path=str(path),
                file_name=path.name,
                file_type=path.suffix.lower(),
                text="",
                elements=[],
                status=ParseStatus.FAILED,
                metadata={
                    "tenant_id": tenant_id,
                    "created_by": created_by,
                },
                errors=[f"文件不存在：{path}"],
            )

        if path.suffix.lower() not in SUPPORTED_FILE_TYPES:
            return ParsedDocument(
                document_id="",
                title=path.stem,
                source_path=str(path),
                file_name=path.name,
                file_type=path.suffix.lower(),
                text="",
                elements=[],
                status=ParseStatus.UNSUPPORTED,
                metadata={
                    "tenant_id": tenant_id,
                    "created_by": created_by,
                },
                errors=[f"暂不支持该文件类型：{path.suffix.lower()}"],
            )

        parser = self.factory.get_parser(path)

        return parser.parse(
            file_path=path,
            tenant_id=tenant_id,
            created_by=created_by,
        )

    def parse_directory(
        self,
        directory: str | Path,
        tenant_id: str = "tenant_001",
        created_by: str = "system",
    ) -> ParseDirectoryResult:
        directory_path = Path(directory)

        documents: list[ParsedDocument] = []

        if not directory_path.exists():
            return ParseDirectoryResult(
                total=0,
                success=0,
                failed=0,
                documents=[],
            )

        files = [
            path for path in directory_path.rglob("*")
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_FILE_TYPES
        ]

        for file_path in files:
            documents.append(
                self.parse_file(
                    file_path=file_path,
                    tenant_id=tenant_id,
                    created_by=created_by,
                )
            )

        success_count = sum(
            1 for doc in documents
            if doc.status in [
                ParseStatus.SUCCESS,
                ParseStatus.PARTIAL_SUCCESS,
            ]
        )

        failed_count = len(documents) - success_count

        return ParseDirectoryResult(
            total=len(documents),
            success=success_count,
            failed=failed_count,
            documents=documents,
        )


document_parsing_service = DocumentParsingService()