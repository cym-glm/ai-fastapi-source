
from pathlib import Path
from langchain_core.documents import Document

KNOWLEDGE_BASE_PATH = Path("data/knowledge_base")

def load_markdown_documents(base_dir: Path = KNOWLEDGE_BASE_PATH ) -> list[Document]:

    documents: list[Document] = []

    for file_path in sorted(base_dir.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        document_id  = file_path.stem
        documents.append(
            Document(
                page_content=content, 
                metadata={
                    "source": str(file_path),
                    "file_name": file_path.name,
                    "document_id": document_id,
                    "file_type":"markdown"
                }
            )
        )
    return documents

def print_documents(documents: list[Document]):
    for index, doc in  enumerate(documents, start=1):
        print(f"Document:{index}")
        print(f"metadata:{doc.metadata}")
        print(f"content :{doc.page_content[:100]}")
        # print(f"Source:{doc.metadata['source']}")
        # print(f"File Name:{doc.metadata['file_name']}")
        # print(f"Type:{doc.metadata['file_type']}")
        print("====================")