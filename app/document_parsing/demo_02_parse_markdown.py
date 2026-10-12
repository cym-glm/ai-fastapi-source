from app.document_parsing.service import document_parsing_service


def main():
    result = document_parsing_service.parse_file(
        "data/sample_docs/employee_handbook.md",
        tenant_id="tenant_001",
        created_by="u_10001",
    )

    print("status:", result.status)
    print("title:", result.title)

    print("=" * 80)
    print("elements:")
    for element in result.elements:
        print(
            element.type,
            "=>",
            element.content[:80],
        )

    print("=" * 80)
    print("text:")
    print(result.text)


if __name__ == "__main__":
    main()