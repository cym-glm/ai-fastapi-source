from app.core.config import settings
from app.llm.providers.openai_compatible import OpenAICompatibleProvider
from app.llm.schemas import LLMProviderName, LLMRequest


class QwenProvider(OpenAICompatibleProvider):
    provider_name = LLMProviderName.QWEN

    def __init__(self):
        super().__init__(
            api_key=settings.dashscope_api_key,
            base_url=settings.qwen_base_url,
            default_model="qwen-plus",
            timeout_seconds=60,
        )

    def _build_payload(
        self,
        request: LLMRequest,
        stream: bool,
    ) -> dict:
        payload = super()._build_payload(request=request, stream=stream)

        if stream:
            payload["stream_options"] = {
                "include_usage": True
            }

        return payload