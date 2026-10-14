from app.rag_evaluation.service import rag_evaluation_service


def main():
    results = rag_evaluation_service.compare_strategies()

    for item in results:
        strategy_name = item["strategy_name"]
        report = item["report"]

        print("strategy:", strategy_name)
        print("total_cases:", report["total_cases"])

        print("retrieval_metrics:")
        for key, value in report["retrieval_metrics"].items():
            print(f"  {key}: {round(value, 4)}")

        print("generation_metrics:")
        for key, value in report["generation_metrics"].items():
            print(f"  {key}: {round(value, 4)}")

        print("=" * 120)


if __name__ == "__main__":
    main()