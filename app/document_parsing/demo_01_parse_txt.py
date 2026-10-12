from app.document_parsing.service import document_parsing_service


def main():
    result = document_parsing_service.parse_file(
        "data/sample_docs/after_sales.txt",
        tenant_id="tenant_001",
        created_by="u_10001",
    )

    print("status:", result.status)
    print("title:", result.title)
    print("file_type:", result.file_type)

    print("=" * 80)
    print("text:")
    print(result.text)

    print("=" * 80)
    print("elements:")
    for element in result.elements:
        print(element)


if __name__ == "__main__":
    main()