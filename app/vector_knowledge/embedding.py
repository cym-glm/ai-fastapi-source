import hashlib
import re
from abc import ABC, abstractmethod

from app.vector_knowledge.schemas import EmbeddingConfig
from app.vector_knowledge.similarity import normalize_vector


class BaseEmbeddingModel(ABC):
    @abstractmethod
    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        raise NotImplementedError

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            self.embed_text(text)
            for text in texts
        ]


class DeterministicHashEmbedding(BaseEmbeddingModel):
    """
    教学版 Embedding。

    特点：
    1. 不依赖外部 API Key。
    2. 同一段文本每次生成相同向量。
    3. 支持中文关键词和字符级 hash。
    4. 只用于教学，不代表真实语义 Embedding 效果。
    """

    def __init__(
        self,
        config: EmbeddingConfig,
    ):
        self.config = config
        self.dimension = config.dimension

        self.keyword_boosts = {
            "订单": 3.0,
            "未发货": 3.0,
            "发货": 2.0,
            "退款": 3.0,
            "退货": 2.5,
            "售后": 2.5,
            "物流": 3.0,
            "快递": 2.5,
            "发票": 3.0,
            "企业": 2.0,
            "个人": 2.0,
            "年假": 3.0,
            "报销": 3.0,
            "合同": 3.0,
            "付款": 2.5,
            "客服": 2.0,
        }

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        vector = [0.0 for _ in range(self.dimension)]

        tokens = self._tokenize(text)

        for token in tokens:
            index = self._hash_to_index(token)
            vector[index] += 1.0

        for keyword, weight in self.keyword_boosts.items():
            if keyword in text:
                index = self._hash_to_index(f"keyword:{keyword}")
                vector[index] += weight

        if self.config.normalize:
            vector = normalize_vector(vector)

        return vector

    def _tokenize(
        self,
        text: str,
    ) -> list[str]:
        normalized = text.lower().strip()

        english_tokens = re.findall(
            r"[a-zA-Z0-9_]+",
            normalized,
        )

        chinese_chars = [
            char for char in normalized
            if "\u4e00" <= char <= "\u9fff"
        ]

        return english_tokens + chinese_chars

    def _hash_to_index(
        self,
        token: str,
    ) -> int:
        digest = hashlib.md5(
            token.encode("utf-8")
        ).hexdigest()

        return int(digest, 16) % self.dimension


class EmbeddingModelFactory:
    def create(
        self,
        config: EmbeddingConfig,
    ) -> BaseEmbeddingModel:
        # 教学版仅内置 hash provider，其余厂商需接入外部 API
        if config.provider.value == "hash":
            return DeterministicHashEmbedding(config)

        # 未支持的 provider 直接报错，避免静默降级
        raise ValueError(
            f"当前教学版暂不支持该 Embedding Provider：{config.provider}"
        )