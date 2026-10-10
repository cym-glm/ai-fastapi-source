from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_rag.prompts import RAG_PROMPT
from app.langchain_rag.retriever import create_retriever
from app.langchain_rag.splitters import format_docs


def build_rag_chain(
    provider: str = "deepseek",
    model_name: str = "deepseek-chat",
    k: int = 4,
):
    retriever = create_retriever(k=k)

    model = LangChainModelFactory.create(
        provider=provider,
        model=model_name,
        temperature=0,
    )

    parser = StrOutputParser()

    def retrieve_context(inputs: dict[str, Any]) -> dict[str, Any]:
        question = inputs["question"]

        docs = retriever.invoke(question)

        return {
            "question": question,
            "context": format_docs(docs),
            "docs": docs,
        }

    def attach_sources(answer_inputs: dict[str, Any]) -> dict[str, Any]:
        return answer_inputs

    retrieve_runnable = RunnableLambda(retrieve_context)

    answer_chain = RAG_PROMPT | model | parser

    def run_answer(inputs: dict[str, Any]) -> dict[str, Any]:
        answer = answer_chain.invoke({
            "question": inputs["question"],
            "context": inputs["context"],
        })

        sources = []

        for doc in inputs["docs"]:
            sources.append({
                "document_id": doc.metadata.get("document_id"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "source": doc.metadata.get("source"),
                "content_preview": doc.page_content[:160],
            })

        return {
            "answer": answer,
            "sources": sources,
        }

    return retrieve_runnable | RunnableLambda(run_answer)