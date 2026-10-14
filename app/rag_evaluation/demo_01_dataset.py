from app.rag_evaluation.dataset import load_golden_dataset


def main():
    cases = load_golden_dataset()

    print("total cases:", len(cases))
    print("=" * 80)

    for case in cases:
        print("case_id:", case.case_id)
        print("question:", case.question)
        print("category:", case.category.value)
        print("expected_chunk_ids:", case.expected_chunk_ids)
        print("expected_answer_keywords:", case.expected_answer_keywords)
        print("metadata_filter:", case.metadata_filter)
        print("notes:", case.notes)
        print("-" * 80)


if __name__ == "__main__":
    main()