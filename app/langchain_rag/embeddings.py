import hashlib
import math
import re
from collections import Counter

from langchain_core.embeddings import Embeddings


class SimpleHashEmbeddings(Embeddings):
    """
    教学用本地 Embedding。

    说明：
    1. 不需要 API Key。
    2. 可以跑通 RAG 流程。
    3. 不适合生产环境。
    4. 生产环境请替换为 OpenAIEmbeddings / Qwen Embeddings / bge 等。
    """

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            self._embed(text)
            for text in texts
        ]

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        tokens = self._tokenize(text)
        counter = Counter(tokens)

        vector = [0.0] * self.dimension

        for token, count in counter.items():
            index = self._hash_to_index(token)
            vector[index] += float(count)

        return self._normalize(vector)

    def _tokenize(self, text: str) -> list[str]:
        chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
        english_words = re.findall(r"[a-zA-Z0-9_]+", text.lower())

        return chinese_chars + english_words

    def _hash_to_index(self, token: str) -> int:
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        return int(digest, 16) % self.dimension

    def _normalize(
        self,
        vector: list[float],
    ) -> list[float]:
        norm = math.sqrt(sum(value * value for value in vector))

        if norm == 0:
            return vector

        return [
            value / norm
            for value in vector
        ]


def create_embeddings() -> Embeddings:
    return SimpleHashEmbeddings(
        dimension=128,
    )