import math
from collections import Counter


class SimpleKeywordEmbedding:
    """
    教学版 Embedding。

    说明：
    1. 不依赖外部模型。
    2. 用关键词词频构造一个小向量。
    3. 只用于理解 RAG 流程，不代表真实 Embedding 效果。
    """

    def __init__(self):
        self.vocabulary = [
            "订单",
            "未发货",
            "发货",
            "退款",
            "退货",
            "售后",
            "物流",
            "快递",
            "发票",
            "企业",
            "个人",
            "质量",
            "客服",
            "审核",
        ]

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        counter = Counter()

        for word in self.vocabulary:
            counter[word] = text.count(word)

        vector = [
            float(counter[word])
            for word in self.vocabulary
        ]

        norm = math.sqrt(
            sum(value * value for value in vector)
        )

        if norm == 0:
            return vector

        return [
            value / norm
            for value in vector
        ]

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            self.embed_text(text)
            for text in texts
        ]

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        return self.embed_text(query)