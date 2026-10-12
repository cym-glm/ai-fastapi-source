from app.vector_knowledge.service import EmbeddingService
from app.vector_knowledge.similarity import (
    cosine_similarity,
    dot_product,
    euclidean_distance,
)


def main():
    service = EmbeddingService()

    query = "没发货能退钱吗？"

    docs = [
        "订单未发货时，可以申请取消订单并退款。",
        "用户可以在订单完成后申请电子发票。",
        "物流超过 7 天没有更新，建议联系客服。",
    ]

    query_vector = service.embed_text(query)

    print("query:", query)
    print("=" * 80)

    for doc in docs:
        doc_vector = service.embed_text(doc)

        print("doc:", doc)
        print("cosine:", round(cosine_similarity(query_vector, doc_vector), 4))
        print("dot:", round(dot_product(query_vector, doc_vector), 4))
        print("euclidean:", round(euclidean_distance(query_vector, doc_vector), 4))
        print("-" * 80)


if __name__ == "__main__":
    main()