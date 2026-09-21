from collections.abc import AsyncGenerator

from langchain_core.messages import AIMessageChunk

from app.langchain_models.message_adapter import (
    to_langchain_messages,
    to_llm_response,
)
from app.langchain_models.model_factory import LangChainModelFactory
from app.llm.base import BaseLLMProvider
from app.llm.schemas import (
    LLMProviderName,
    LLMRequest,
    LLMResponse,
    LLMStreamChunk,
    LLMUsage,
)


class LangChainLLMProvider(BaseLLMProvider):
    def __init__(
        self,
        provider: str = "deepseek",
        model: str = "deepseek-chat",
    ):
        self.provider = provider
        self.model = model

    @property
    def provider_name(self) -> LLMProviderName:
        if self.provider == "deepseek":
            return LLMProviderName.DEEPSEEK

        if self.provider == "qwen":
            return LLMProviderName.QWEN

        if self.provider == "openai":
            return LLMProviderName.OPENAI

        return LLMProviderName.MOCK

    async def chat(self, request: LLMRequest) -> LLMResponse:
        model = LangChainModelFactory.create(
            provider=self.provider,
            model=request.model or self.model,
            temperature=request.temperature,
            streaming=False,
        )

        messages = to_langchain_messages(request.messages)

        if request.tools:
            model = model.bind_tools(request.tools)

        ai_message = await model.ainvoke(messages)

        return to_llm_response(
            ai_message=ai_message,
            provider=self.provider_name,
            model=request.model or self.model,
        )

    async def stream_chat(
        self,
        request: LLMRequest,
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        model = LangChainModelFactory.create(
            provider=self.provider,
            model=request.model or self.model,
            temperature=request.temperature,
            streaming=True,
        )

        messages = to_langchain_messages(request.messages)

        async for chunk in model.astream(messages):
            yield self._to_stream_chunk(
                chunk=chunk,
                model=request.model or self.model,
            )

    def _to_stream_chunk(
        self,
        chunk: AIMessageChunk,
        model: str,
    ) -> LLMStreamChunk:
        return LLMStreamChunk(
            provider=self.provider_name,
            model=model,
            content=str(chunk.content or ""),
            usage=LLMUsage(),
            finish_reason=None,
            raw_chunk={
                "id": chunk.id,
                "content": chunk.content,
                "response_metadata": chunk.response_metadata,
            },
        )