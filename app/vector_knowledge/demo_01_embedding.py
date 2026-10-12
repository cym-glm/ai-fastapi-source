from app.vector_knowledge.service import EmbeddingService


def main():
    service = EmbeddingService()

    texts = [
        "订单未发货时，可以申请取消订单并退款。",
        "没发货能不能退钱？",
        "企业发票需要填写公司名称和纳税人识别号。",
    ]

    for text in texts:
        vector = service.embed_text(text)

        print("text:", text)
        print("dimension:", len(vector))
        print("first 10 dims:", vector[:10])
        print("norm approx:", round(sum(v * v for v in vector) ** 0.5, 4))
        print("-" * 80)


if __name__ == "__main__":
    main()