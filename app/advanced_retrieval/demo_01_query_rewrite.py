from app.advanced_retrieval.query_rewrite import RuleBasedQueryRewriter


def main():
    rewriter = RuleBasedQueryRewriter()

    queries = [
        "我刚买的课还没开始学，现在不想要了怎么办？",
        "快递好几天没动了怎么处理？",
        "企业发票需要填什么？",
        "年假怎么申请？",
        "差旅报销要哪些材料？",
    ]

    for query in queries:
        result = rewriter.rewrite(query)

        print("original:", result.original_query)
        print("intent:", result.intent)
        print("rewritten:", result.rewritten_query)
        print("keywords:", result.keywords)
        print("filters:", result.filters)
        print("=" * 100)


if __name__ == "__main__":
    main()