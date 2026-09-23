
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_default_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=[
            "\n## ",
            "\n# ",
            "\n\n",
            "\n",
            "。",
            "，",
            " ",
            "",
        ],
    )

def split_documents(
        documents: list[Document],
    ) -> list[Document]:
    splitter = create_default_text_splitter()
    chunks =  splitter.split_documents(documents)

    for index, chunk in enumerate(chunks, start=1):
        chunk.metadata = {
            **chunk.metadata,
            "chunk_id": f"{chunk.metadata.get('document_id', 'doc')}_chunk_{index}",
            "chunk_index": index,
        }
    return chunks

def format_docs(docs: list[Document]) -> str:
    lines = []
    for index, doc in enumerate(docs, start=1):
        document_id = doc.metadata.get("document_id", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "unknown")
        source = doc.metadata.get("source", "unknown")
        lines.append(
            f"[{index}] document_id={document_id}, chunk_id={chunk_id}, source={source}\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(lines)
