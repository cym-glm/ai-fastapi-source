from app.rag_principles.pipeline import MiniRAGPipeline


def print_answer(question: str, result):
    print("用户问题:")
    print(question)

    print("=" * 80)
    print("最终回答:")
    print(result.answer)

    print("=" * 80)
    print("召回结果:")
    for item in result.retrieved_chunks:
        print("chunk_id:", item.chunk.chunk_id)
        print("title:", item.chunk.title)
        print("score:", round(item.score, 4))
        print("content:", item.chunk.content)
        print("metadata:", item.chunk.metadata)
        print("-" * 80)

    print("=" * 120)


def main():
    pipeline = MiniRAGPipeline()
    pipeline.build_index()

    questions = [
        "订单还没发货，可以退款吗？",
        "物流超过 7 天没更新怎么办？",
        "企业发票需要填写什么？",
        "会员积分规则是什么？",
    ]

    for question in questions:
        result = pipeline.ask(
            question=question,
            top_k=3,
        )

        print_answer(question, result)

    print("测试 metadata_filter:")
    result = pipeline.ask(
        question="退款规则是什么？",
        top_k=3,
        metadata_filter={
            "doc_type": "after_sales"
        },
    )

    print_answer("退款规则是什么？", result)


if __name__ == "__main__":
    main()