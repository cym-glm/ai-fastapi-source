from app.advanced_retrieval.keyword_search import SimpleKeywordSearchEngine
from app.advanced_retrieval.service import build_sample_chunks
from app.vector_knowledge.service import EmbeddingService


def main():
    embedding_service = EmbeddingService()

    chunks = build_sample_chunks()
    embedded_chunks = embedding_service.embed_chunks(chunks)

    engine = SimpleKeywordSearchEngine()
    engine.add_many(embedded_chunks)

    queries = [
        "退款",
        "HR 年假",
        "纳税人识别号",
    ]

    for query in queries:
        print("query:", query)
        results = engine.search(
            query=query,
            top_k=5,
        )

        for item in results:
            print(item.chunk_id, round(item.score, 4), item.content)
        print("=" * 100)


if __name__ == "__main__":
    main()