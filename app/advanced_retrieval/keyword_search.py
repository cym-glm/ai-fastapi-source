import math
import re
from collections import Counter

from app.advanced_retrieval.schemas import KeywordSearchResult
from app.vector_knowledge.schemas import EmbeddedChunk


class SimpleKeywordSearchEngine:
    """
    教学版关键词检索。

    不是完整 BM25，但保留关键词匹配 + 简单 IDF 思路。
    """

    def __init__(self):
        self.items: dict[str, EmbeddedChunk] = {}
        self.doc_freq: Counter[str] = Counter()
        self.total_docs = 0

    def add_many(
        self,
        chunks: list[EmbeddedChunk],
    ) -> None:
        for chunk in chunks:
            self.items[chunk.chunk_id] = chunk

        self._rebuild_doc_freq()

    def clear(self) -> None:
        self.items.clear()
        self.doc_freq.clear()
        self.total_docs = 0

    def search(
        self,
        query: str,
        top_k: int = 10,
        metadata_filter: dict | None = None,
    ) -> list[KeywordSearchResult]:
        query_terms = self._tokenize(query)

        candidates = list(self.items.values())

        if metadata_filter:
            candidates = [
                item for item in candidates
                if self._match_metadata_filter(
                    item.metadata,
                    metadata_filter,
                )
            ]

        results: list[KeywordSearchResult] = []

        for item in candidates:
            score = self._score(
                query_terms=query_terms,
                content=item.content,
            )

            if score <= 0:
                continue

            results.append(
                KeywordSearchResult(
                    chunk_id=item.chunk_id,
                    document_id=item.document_id,
                    content=item.content,
                    score=score,
                    metadata=item.metadata,
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return results[:top_k]

    def _score(
        self,
        query_terms: list[str],
        content: str,
    ) -> float:
        if not query_terms:
            return 0.0

        content_terms = self._tokenize(content)
        term_count = Counter(content_terms)
        content_len = max(len(content_terms), 1)

        score = 0.0

        for term in query_terms:
            tf = term_count.get(term, 0)

            if tf == 0:
                continue

            df = self.doc_freq.get(term, 0)
            idf = math.log(
                (self.total_docs + 1) / (df + 1)
            ) + 1

            score += (tf / content_len) * idf

        return score

    def _rebuild_doc_freq(self) -> None:
        self.doc_freq.clear()
        self.total_docs = len(self.items)

        for item in self.items.values():
            terms = set(
                self._tokenize(item.content)
            )

            for term in terms:
                self.doc_freq[term] += 1

    def _tokenize(
        self,
        text: str,
    ) -> list[str]:
        normalized = text.lower().strip()

        english_terms = re.findall(
            r"[a-zA-Z0-9_\\-]+",
            normalized,
        )

        chinese_terms = [
            char for char in normalized
            if "\u4e00" <= char <= "\u9fff"
        ]

        business_terms = []

        for term in [
            "未发货",
            "已发货",
            "退款",
            "退货",
            "物流",
            "快递",
            "发票",
            "年假",
            "报销",
            "合同",
            "付款",
            "审批记录",
            "纳税人识别号",
        ]:
            if term in text:
                business_terms.append(term)

        return english_terms + chinese_terms + business_terms

    def _match_metadata_filter(
        self,
        metadata: dict,
        metadata_filter: dict,
    ) -> bool:
        for key, expected_value in metadata_filter.items():
            actual_value = metadata.get(key)

            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            else:
                if actual_value != expected_value:
                    return False

        return True