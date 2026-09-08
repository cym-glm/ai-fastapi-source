import json
from collections.abc import AsyncGenerator

import httpx

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


class OpenAICompatibleProvider(BaseLLMProvider):
    provider_name: LLMProviderName

    def __init__(
        self,
        api_key: str,
        base_url: str,
        default_model: str,
        timeout_seconds: float = 60,
    ):
        if not api_key:
            raise LLMProviderConfigError(
                message="LLM API Key 未配置",
                provider=self.provider_name.value,
            )

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds

    async def chat(self, request: LLMRequest) -> LLMResponse:
        payload = self._build_payload(request=request, stream=False)
        url = f"{self.base_url}/chat/completions"

        logger.info(
            f"llm_chat_start provider={self.provider_name.value} "
            f"model={payload['model']} message_count={len(request.messages)}"
        )

        try:
            async with create_llm_http_client(self.timeout_seconds) as client:
                response = await client.post(
                    url,
                    headers=self._headers(),
                    json=payload,
                )
                # 这里不直接抛出异常，因为有些模型会返回 200 但内容有问题
                response.raise_for_status()

        except httpx.TimeoutException as exc:
            logger.exception(
                f"llm_chat_timeout provider={self.provider_name.value}"
            )
            raise LLMProviderTimeoutError(
                message="大模型调用超时",
                provider=self.provider_name.value,
            ) from exc

        except httpx.HTTPStatusError as exc:
            logger.exception(
                f"llm_chat_http_error provider={self.provider_name.value} "
                f"status_code={exc.response.status_code}"
            )
            raise LLMProviderError(
                message="大模型 HTTP 调用失败",
                provider=self.provider_name.value,
                status_code=exc.response.status_code,
                raw_error=exc.response.text,
            ) from exc

        except httpx.RequestError as exc:
            logger.exception(
                f"llm_chat_request_error provider={self.provider_name.value}"
            )
            raise LLMProviderError(
                message="大模型网络请求失败",
                provider=self.provider_name.value,
                raw_error=repr(exc),
            ) from exc

        data = response.json()

        try:
            llm_response = self._parse_chat_response(data)
        except Exception as exc:
            logger.exception(
                f"llm_chat_parse_error provider={self.provider_name.value}"
            )
            raise LLMProviderResponseParseError(
                message="大模型响应解析失败",
                provider=self.provider_name.value,
                raw_error=json.dumps(data, ensure_ascii=False),
            ) from exc

        logger.info(
            f"llm_chat_success provider={self.provider_name.value} "
            f"model={llm_response.model} total_tokens={llm_response.usage.total_tokens}"
        )

        return llm_response

    async def stream_chat(
        self,
        request: LLMRequest,
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        payload = self._build_payload(request=request, stream=True)
        url = f"{self.base_url}/chat/completions"

        logger.info(
            f"llm_stream_start provider={self.provider_name.value} "
            f"model={payload['model']} message_count={len(request.messages)}"
        )

        try:
            async with create_llm_http_client(self.timeout_seconds) as client:
                async with client.stream(
                    "POST",
                    url,
                    headers=self._headers(),
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        if not line.startswith("data:"):
                            continue

                        data = line.removeprefix("data:").strip()

                        if data == "[DONE]":
                            break

                        chunk_data = json.loads(data)
                        chunk = self._parse_stream_chunk(chunk_data)

                        yield chunk

        except httpx.TimeoutException as exc:
            logger.exception(
                f"llm_stream_timeout provider={self.provider_name.value}"
            )
            raise LLMProviderTimeoutError(
                message="大模型流式调用超时",
                provider=self.provider_name.value,
            ) from exc

        except httpx.HTTPStatusError as exc:
            logger.exception(
                f"llm_stream_http_error provider={self.provider_name.value} "
                f"status_code={exc.response.status_code}"
            )
            raise LLMProviderError(
                message="大模型流式 HTTP 调用失败",
                provider=self.provider_name.value,
                status_code=exc.response.status_code,
                raw_error=exc.response.text,
            ) from exc

        except httpx.RequestError as exc:
            logger.exception(
                f"llm_stream_request_error provider={self.provider_name.value}"
            )
            raise LLMProviderError(
                message="大模型流式网络请求失败",
                provider=self.provider_name.value,
                raw_error=repr(exc),
            ) from exc

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(
        self,
        request: LLMRequest,
        stream: bool,
    ) -> dict:
        payload = {
            "model": request.model or self.default_model,
            "messages": [
                {
                    "role": message.role.value,
                    "content": message.content,
                }
                for message in request.messages
            ],
            "temperature": request.temperature,
            "stream": stream,
            # "stream_options": {}
        }

        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        return payload

    def _parse_chat_response(self, data: dict) -> LLMResponse:
        choice = data["choices"][0]
        message = choice["message"]

        usage_data = data.get("usage") or {}

        usage = LLMUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        return LLMResponse(
            provider=self.provider_name,
            model=data.get("model", self.default_model),
            content=message.get("content", ""),
            usage=usage,
            raw_response=data,
        )

    def _parse_stream_chunk(self, data: dict) -> LLMStreamChunk:
        choice = data["choices"][0]
        delta = choice.get("delta") or {}
        usage_data = data.get("usage")

        usage = None

        if usage_data:
            usage = LLMUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

        return LLMStreamChunk(
            provider=self.provider_name,
            model=data.get("model", self.default_model),
            content=delta.get("content") or "",
            finish_reason=choice.get("finish_reason"),
            usage=usage,
            raw_chunk=data,
        )