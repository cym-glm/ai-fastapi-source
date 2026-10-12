"""
LangChain VectorStore 示例。

说明：
1. 需要安装 langchain-core。
2. 这里使用 InMemoryVectorStore 做教学。
3. 真实项目可以替换成 Chroma / PGVector / Qdrant / Milvus。
"""


def demo_langchain_in_memory_vector_store():
    from langchain_core.documents import Document
    from langchain_core.embeddings import Embeddings
    from langchain_core.vectorstores import InMemoryVectorStore

    class SimpleEmbeddings(Embeddings):
        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [
                self.embed_query(text)
                for text in texts
            ]

        def embed_query(self, text: str) -> list[float]:
            vector = [0.0, 0.0, 0.0]

            if "退款" in text or "未发货" in text:
                vector[0] = 1.0

            if "物流" in text or "快递" in text:
                vector[1] = 1.0

            if "发票" in text:
                vector[2] = 1.0

            return vector

    documents = [
        Document(
            page_content="订单未发货时，可以申请取消订单并退款。",
            metadata={
                "source": "after_sales",
                "doc_type": "after_sales",
            },
        ),
        Document(
            page_content="物流超过 7 天没有更新，建议联系客服。",
            metadata={
                "source": "logistics",
                "doc_type": "logistics",
            },
        ),
        Document(
            page_content="企业发票需要填写公司名称和纳税人识别号。",
            metadata={
                "source": "invoice",
                "doc_type": "invoice",
            },
        ),
    ]

    vector_store = InMemoryVectorStore(
        embedding=SimpleEmbeddings()
    )

    vector_store.add_documents(documents)

    results = vector_store.similarity_search(
        "没发货可以退款吗？",
        k=2,
        filter={
            "doc_type": "after_sales",
        },
    )

    for doc in results:
        print(doc.page_content, doc.metadata)


def main():
    demo_langchain_in_memory_vector_store()


if __name__ == "__main__":
    main()