import json

from app.langchain_rag.service import langchain_rag_service


def main():
    index_result = langchain_rag_service.rebuild_index()
    print("index_result:")
    print(json.dumps(index_result, ensure_ascii=False, indent=2))
    print("=" * 80)

    answer = langchain_rag_service.ask(
        question="订单未发货时可以退款吗？",
        provider="deepseek",
        model_name="deepseek-chat",
        k=3,
    )

    print(answer.model_dump_json(indent=2))


if __name__ == "__main__":
    main()