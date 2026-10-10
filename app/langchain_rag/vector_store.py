from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from app.langchain_rag.embeddings import create_embeddings


CHROMA_DIR = Path("data/chroma_langchain_rag")
COLLECTION_NAME = "ai_agent_course_kb"


def create_vector_store() -> Chroma:
    embeddings = create_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )


def rebuild_vector_store(
    chunks: list[Document],
) -> Chroma:
    if CHROMA_DIR.exists():
        import shutil
        shutil.rmtree(CHROMA_DIR)

    vector_store = create_vector_store()

    ids = [
        chunk.metadata.get("chunk_id", f"chunk_{index}")
        for index, chunk in enumerate(chunks)
    ]

    vector_store.add_documents(
        documents=chunks,
        ids=ids,
    )

    return vector_store


def similarity_search(
    query: str,
    k: int = 4,
) -> list[Document]:
    vector_store = create_vector_store()

    return vector_store.similarity_search(
        query=query,
        k=k,
    )