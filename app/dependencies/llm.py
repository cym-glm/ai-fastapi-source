


from app.core.config import settings
from app.langchain_models.langchain_provider import LangChainLLMProvider
from app.llm.base import BaseLLMProvider
from app.llm.factory import LLMProviderFactory



class MockLLMProvider:
    def __init__(self, model: str):
        self.model = model

    async def chat(self, message: str) -> str:
        return f"模型：{self.model}，回答内容：{message}"


# async def get_llm_provider() -> MockLLMProvider:
#     return MockLLMProvider(settings.default_model)

async def get_llm_provider() -> BaseLLMProvider:

    if settings.default_llm_provider.startswith("langchain_"):
        provider = settings.default_llm_provider.replace("langchain_", "")
        return LangChainLLMProvider(
            provider=provider,
            model=settings.default_model)

    return LLMProviderFactory.create(
        provider=settings.default_llm_provider
    )


#  ChatService   BaseLLMProvider ---  DeepSeekProvider / QwenProvider / OpenAIProvider

# 接入 Langchain  

# ChatService-- BaseLLMProvider --LangChainLLMProvider -- ChatOpenAI -- Deepseek  Qwen  OpenAI