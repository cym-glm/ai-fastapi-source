from pathlib import Path

from app.document_parsing.parsers import (
    BaseDocumentParser,
    DocxDocumentParser,
    HtmlDocumentParser,
    MarkdownDocumentParser,
    PdfDocumentParser,
    TxtDocumentParser,
)


class DocumentParserFactory:
    def __init__(self):
        self.parsers: dict[str, BaseDocumentParser] = {
            ".txt": TxtDocumentParser(),
            ".md": MarkdownDocumentParser(),
            ".markdown": MarkdownDocumentParser(),
            ".html": HtmlDocumentParser(),
            ".htm": HtmlDocumentParser(),
            ".docx": DocxDocumentParser(),
            ".pdf": PdfDocumentParser(),
        }

    def get_parser(
        self,
        file_path: str | Path,
    ) -> BaseDocumentParser:
        suffix = Path(file_path).suffix.lower()

        parser = self.parsers.get(suffix)

        if not parser:
            raise ValueError(
                f"暂不支持该文件类型：{suffix}"
            )

        return parser