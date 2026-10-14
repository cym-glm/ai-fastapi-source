"""
LangChain 高级 Retrieval 示例。

说明：
1. 这些示例展示真实 LangChain 生态写法。
2. 本章默认运行教学版 advanced_retrieval。
3. 真实项目可逐步替换为 LangChain 内置组件。
"""


def demo_vectorstore_as_mmr_retriever(vectorstore):
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 20,
            "lambda_mult": 0.5,
        },
    )

    return retriever.invoke("订单未发货可以退款吗？")


def demo_bm25_retriever(documents):
    from langchain_community.retrievers import BM25Retriever

    retriever = BM25Retriever.from_documents(
        documents
    )
    retriever.k = 5

    return retriever.invoke("退款 未发货")


def demo_multi_query_retriever(llm, base_retriever):
    from langchain_classic.retrievers.multi_query import MultiQueryRetriever

    retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm,
    )

    return retriever.invoke("没发货能退钱吗？")


def demo_cross_encoder_reranker(base_retriever):
    from langchain_classic.retrievers.contextual_compression import (
        ContextualCompressionRetriever,
    )
    from langchain_classic.retrievers.document_compressors import (
        CrossEncoderReranker,
    )
    from langchain_community.cross_encoders import HuggingFaceCrossEncoder

    cross_encoder = HuggingFaceCrossEncoder(
        model_name="BAAI/bge-reranker-v2-m3"
    )

    reranker = CrossEncoderReranker(
        model=cross_encoder,
        top_n=3,
    )

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=base_retriever,
    )

    return compression_retriever.invoke("订单未发货可以退款吗？")