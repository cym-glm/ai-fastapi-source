
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.langchain_rag.vector_store import create_vector_store

def create_retriever(
    k: int = 4,
)-> BaseRetriever:
    vector_store = create_vector_store()

    return vector_store.as_retriever(
        search_kwargs={"k": k},
    )

def retrieve_documents(
    query: str,
    k: int = 4,
) -> list[Document]:
    retriever = create_retriever(k=k)
    return retriever.invoke(input=query)
