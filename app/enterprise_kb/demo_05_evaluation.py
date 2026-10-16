from app.enterprise_kb.service import enterprise_kb_service


def main():
    report = enterprise_kb_service.run_evaluation()

    print("name:", report["name"])
    print("total_cases:", report["total_cases"])

    print("=" * 80)
    print("retrieval_metrics:")
    for key, value in report["retrieval_metrics"].items():
        print(key, "=", round(value, 4))

    print("=" * 80)
    print("generation_metrics:")
    for key, value in report["generation_metrics"].items():
        print(key, "=", round(value, 4))


if __name__ == "__main__":
    main()