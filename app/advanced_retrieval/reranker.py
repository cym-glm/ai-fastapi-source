from app.advanced_retrieval.schemas import HybridSearchResult


class SimpleRuleReranker:
    """
    教学版 Reranker。

    生产环境可以换成：
    1. Cross Encoder Reranker
    2. Cohere Rerank
    3. BGE Reranker
    4. VoyageAI Rerank
    """

    def rerank(
        self,
        query: str,
        candidates: list[HybridSearchResult],
        top_k: int,
    ) -> list[HybridSearchResult]:
        query_keywords = self._extract_business_keywords(query)

        reranked: list[HybridSearchResult] = []

        for item in candidates:
            bonus = 0.0
            content = item.content

            for keyword in query_keywords:
                if keyword in content:
                    bonus += 0.2

            if item.metadata.get("is_latest") is True:
                bonus += 0.1

            if item.metadata.get("doc_type") and item.metadata.get("doc_type") in query:
                bonus += 0.1

            item.final_score = item.final_score + bonus
            reranked.append(item)

        reranked.sort(
            key=lambda item: item.final_score,
            reverse=True,
        )

        return reranked[:top_k]

    def _extract_business_keywords(
        self,
        query: str,
    ) -> list[str]:
        keywords = []

        for keyword in [
            "退款",
            "未发货",
            "退货",
            "物流",
            "快递",
            "发票",
            "年假",
            "报销",
            "合同",
            "付款",
        ]:
            if keyword in query:
                keywords.append(keyword)

        if "退钱" in query or "不想要" in query:
            keywords.extend(["退款", "未发货"])

        return list(dict.fromkeys(keywords))