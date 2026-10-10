from app.langchain_rag.documents import load_markdown_documents

from app.langchain_rag.retriever import retrieve_documents

from app.langchain_rag.splitters import split_documents

from app.langchain_rag.vector_store import rebuild_vector_store



def main():

    documents = load_markdown_documents()
    chunks = split_documents(documents)
    rebuild_vector_store(chunks)
    questions = [
        "员工年假有几天？",
        "订单未发货可以退款吗？",
        "第 20 到 28 章属于哪个阶段？",
    ]
    for question in questions:
        print("question:", question)
        print("=" * 80)

        docs = retrieve_documents(
            query=question,
            k=3,
        )

        for doc in docs:
            print("metadata:", doc.metadata)
            print("content preview:", doc.page_content[:100])
            print("-" * 80)

        print("=" * 120)


if __name__ == "__main__":
    main()
