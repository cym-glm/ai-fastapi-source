from app.document_parsing.service import document_parsing_service


def main():
    result = document_parsing_service.parse_directory(
        "data/sample_docs",
        tenant_id="tenant_001",
        created_by="u_10001",
    )

    print("total:", result.total)
    print("success:", result.success)
    print("failed:", result.failed)

    print("=" * 80)

    for document in result.documents:
        print("file:", document.file_name)
        print("status:", document.status)
        print("title:", document.title)
        print("elements:", len(document.elements))
        print("errors:", document.errors)
        print("-" * 80)


if __name__ == "__main__":
    main()