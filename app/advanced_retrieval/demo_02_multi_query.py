from app.advanced_retrieval.query_rewrite import (
    RuleBasedMultiQueryExpander,
    RuleBasedQueryRewriter,
)


def main():
    query = "没发货能退钱吗？"

    rewriter = RuleBasedQueryRewriter()
    expander = RuleBasedMultiQueryExpander()

    rewrite_result = rewriter.rewrite(query)
    multi_query_result = expander.expand(
        query=query,
        rewrite_result=rewrite_result,
    )

    print("original:", multi_query_result.original_query)
    print("queries:")

    for item in multi_query_result.queries:
        print("-", item)


if __name__ == "__main__":
    main()