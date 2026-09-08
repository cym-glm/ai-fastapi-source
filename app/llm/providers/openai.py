from collections.abc import AsyncGenerator

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider
from app.llm.errors import (
    LLMProviderConfigError,
    LLMProviderError,
    LLMProviderResponseParseError,
    LLMProviderTimeoutError,
)
from app.llm.http_client import create_llm_http_client
from app.llm.schemas import (
    LLMProviderName,
    LLMRequest,
    LLMResponse,
    LLMStreamChunk,
    LLMUsage,
)


logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.openai_api_key:
            raise LLMProviderConfigError(
                message="OpenAI API Key 未配置",
                provider=LLMProviderName.OPENAI.value,
            )

        self.provider_name = LLMProviderName.OPENAI
        self.api_key = settings.openai_api_key
        self.base_url = settings.openai_base_url.rstrip("/")
        self.default_model = "gpt-4.1-mini"
        self.timeout_seconds = 60

    async def chat(self, request: LLMRequest) -> LLMResponse:
        url = f"{self.base_url}/responses"

        payload = {
            "model": request.model or self.default_model,
            "input": self._messages_to_input(request),
        }

        logger.info(
            f"llm_chat_start provider=openai model={payload['model']} "
            f"message_count={len(request.messages)}"
        )

        try:
            async with create_llm_http_client(self.timeout_seconds) as client:
                response = await client.post(
                    url,
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()

        except httpx.TimeoutException as exc:
            logger.exception("llm_chat_timeout provider=openai")
            raise LLMProviderTimeoutError(
                message="OpenAI 调用超时",
                provider=self.provider_name.value,
            ) from exc

        except httpx.HTTPStatusError as exc:
            logger.exception(
                f"llm_chat_http_error provider=openai status_code={exc.response.status_code}"
            )
            raise LLMProviderError(
                message="OpenAI HTTP 调用失败",
                provider=self.provider_name.value,
                status_code=exc.response.status_code,
                raw_error=exc.response.text,
            ) from exc

        except httpx.RequestError as exc:
            logger.exception("llm_chat_request_error provider=openai")
            raise LLMProviderError(
                message="OpenAI 网络请求失败",
                provider=self.provider_name.value,
                raw_error=repr(exc),
            ) from exc

        data = response.json()

        try:
            return self._parse_response(data)
        except Exception as exc:
            logger.exception("llm_chat_parse_error provider=openai")
            raise LLMProviderResponseParseError(
                message="OpenAI 响应解析失败",
                provider=self.provider_name.value,
                raw_error=str(data),
            ) from exc

    async def stream_chat(
        self,
        request: LLMRequest,
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        raise NotImplementedError(
            "OpenAI Responses API streaming 会在后续 Streaming 章节单独完善"
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _messages_to_input(self, request: LLMRequest) -> str:
        lines = []

        for message in request.messages:
            lines.append(f"{message.role.value}: {message.content}")

        return "\n".join(lines)

    def _parse_response(self, data: dict) -> LLMResponse:
        content = data.get("output_text", "")

        usage_data = data.get("usage") or {}

        usage = LLMUsage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        return LLMResponse(
            provider=self.provider_name,
            model=data.get("model", self.default_model),
            content=content,
            usage=usage,
            raw_response=data,
        )