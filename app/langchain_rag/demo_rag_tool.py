import asyncio

from app.langchain_rag.documents import load_markdown_documents
from app.langchain_rag.splitters import split_documents
from app.langchain_rag.tools import search_knowledge_base_tool
from app.langchain_rag.vector_store import rebuild_vector_store


async def main():
    documents = load_markdown_documents()
    chunks = split_documents(documents)
    rebuild_vector_store(chunks)

    result = await search_knowledge_base_tool.ainvoke({
        "query": "第 20 到 28 章属于什么阶段？"
    })

    print(result)


if __name__ == "__main__":
    asyncio.run(main())