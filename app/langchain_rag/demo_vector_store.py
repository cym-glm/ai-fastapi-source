from app.langchain_rag.documents import load_markdown_documents
from app.langchain_rag.splitters import split_documents
from app.langchain_rag.vector_store import rebuild_vector_store


def main():
    documents = load_markdown_documents()
    chunks = split_documents(documents)

    vector_store = rebuild_vector_store(chunks)

    query = "员工年假有几天？"

    results = vector_store.similarity_search(
        query=query,
        k=3,
    )

    print("query:", query)
    print("=" * 80)

    for doc in results:
        print("metadata:", doc.metadata)
        print("content:")
        print(doc.page_content)
        print("=" * 80)


if __name__ == "__main__":
    main()