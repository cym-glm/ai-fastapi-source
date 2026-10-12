from pathlib import Path

import fitz

from app.document_parsing.service import document_parsing_service


def create_sample_pdf():
    output_path = Path("data/sample_docs/refund_policy.pdf")
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    doc = fitz.open()

    page = doc.new_page()
    page.insert_text(
        (72, 72),
        "Refund Policy",
        fontsize=18,
    )
    page.insert_text(
        (72, 120),
        "Orders that have not been shipped can be cancelled and refunded.",
        fontsize=12,
    )
    page.insert_text(
        (72, 150),
        "Refunds are usually returned within 1 to 3 business days after approval.",
        fontsize=12,
    )

    doc.save(output_path)
    doc.close()

    return output_path


def main():
    file_path = create_sample_pdf()

    result = document_parsing_service.parse_file(
        file_path,
        tenant_id="tenant_001",
        created_by="u_10001",
    )

    print("status:", result.status)
    print("title:", result.title)
    print("metadata:", result.metadata)

    print("=" * 80)
    print("elements:")
    for element in result.elements:
        print(
            element.type,
            "page:",
            element.page_number,
            "=>",
            element.content,
        )

    print("=" * 80)
    print("errors:")
    print(result.errors)


if __name__ == "__main__":
    main()