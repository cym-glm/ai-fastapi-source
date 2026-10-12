def demo_recursive_character_splitter():
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text = (
        "订单未发货时，用户可以申请取消订单并退款。\n\n"
        "订单已发货后，用户需要收到商品后再申请退货退款。\n\n"
        "如果商品存在质量问题，用户可以提交照片或视频凭证申请售后。"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=50,
        chunk_overlap=10,
        separators=[
            "\n\n",
            "\n",
            "。",
            "，",
            "",
        ],
    )

    chunks = splitter.split_text(text)

    for index, chunk in enumerate(chunks):
        print("chunk", index)
        print(chunk)
        print("-" * 80)


def demo_markdown_header_splitter():
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    markdown_text = """
# 员工手册

## 考勤制度

员工需要按照公司规定时间打卡。

## 年假制度

员工入职满一年后，可以申请年假。
申请年假需要提前提交审批。

## 报销制度

差旅报销需要提交发票、行程单和审批记录。
"""

    headers_to_split_on = [
        ("#", "一级标题"),
        ("##", "二级标题"),
        ("###", "三级标题"),
    ]

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
    )

    docs = splitter.split_text(markdown_text)

    for index, doc in enumerate(docs):
        print("doc", index)
        print("content:", doc.page_content)
        print("metadata:", doc.metadata)
        print("-" * 80)


def demo_python_code_splitter():
    from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

    code = '''
class OrderService:
    def query_order(self, order_id: str):
        return {"order_id": order_id}

    def refund_order(self, order_id: str):
        return {"success": True}
'''

    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=80,
        chunk_overlap=0,
    )

    docs = splitter.create_documents([code])

    for index, doc in enumerate(docs):
        print("doc", index)
        print(doc.page_content)
        print("-" * 80)


def main():
    print("RecursiveCharacterTextSplitter:")
    demo_recursive_character_splitter()

    print("=" * 120)
    print("MarkdownHeaderTextSplitter:")
    demo_markdown_header_splitter()

    print("=" * 120)
    print("PythonCodeTextSplitter:")
    demo_python_code_splitter()


if __name__ == "__main__":
    main()