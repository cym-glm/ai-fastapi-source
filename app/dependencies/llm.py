


from app.core.config import settings


class MockLLMProvider:
    def __init__(self, model: str):
        self.model = model

    async def chat(self, message: str) -> str:
        return f"模型：{self.model}，回答内容：{message}"


async def get_llm_provider() -> MockLLMProvider:
    return MockLLMProvider(settings.default_model)

