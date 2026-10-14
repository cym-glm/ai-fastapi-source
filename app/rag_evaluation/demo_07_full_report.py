import json
from pathlib import Path

from app.rag_evaluation.service import rag_evaluation_service


def main():
    report = rag_evaluation_service.run_full_report()

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

    output_dir = Path("data/evaluation_reports")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_dir / "rag_eval_report.json"

    output_path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 80)
    print("report saved to:", output_path)


if __name__ == "__main__":
    main()