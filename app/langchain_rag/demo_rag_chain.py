import json

from app.langchain_rag.chains import build_rag_chain
from app.langchain_rag.documents import load_markdown_documents
from app.langchain_rag.splitters import split_documents
from app.langchain_rag.vector_store import rebuild_vector_store


def main():
    documents = load_markdown_documents()
    chunks = split_documents(documents)
    rebuild_vector_store(chunks)

    chain = build_rag_chain(
        provider="deepseek",
        model_name="deepseek-chat",
        k=3,
    )

    result = chain.invoke({
        "question": "员工入职满一年后年假有几天？"
    })

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()