from langchain_openai import ChatOpenAI

from app.core.config import settings


class LangChainModelFactory:
    @staticmethod
    def create(
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        streaming: bool = False,
    ) -> ChatOpenAI:
        # 未指定时使用全局默认配置
        provider = provider or settings.default_llm_provider
        model = model or settings.default_model

        # 根据供应商分发到对应的工厂方法
        if provider == "deepseek":
            return LangChainModelFactory.create_deepseek(
                model=model,
                temperature=temperature,
                streaming=streaming,
            )

        if provider == "qwen":
            return LangChainModelFactory.create_qwen(
                model=model,
                temperature=temperature,
                streaming=streaming,
            )

        if provider == "openai":
            return LangChainModelFactory.create_openai(
                model=model,
                temperature=temperature,
                streaming=streaming,
            )

        raise ValueError(f"不支持的 LangChain 模型供应商：{provider}")

    @staticmethod
    def create_deepseek(
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        streaming: bool = False,
    ) -> ChatOpenAI:
        if not settings.deepseek_api_key:
            raise RuntimeError("请先配置 DEEPSEEK_API_KEY")

        return ChatOpenAI(
            model=model,
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            temperature=temperature,
            streaming=streaming,
        )

    @staticmethod
    def create_qwen(
        model: str = "qwen-plus",
        temperature: float = 0.7,
        streaming: bool = False,
    ) -> ChatOpenAI:
        if not settings.dashscope_api_key:
            raise RuntimeError("请先配置 DASHSCOPE_API_KEY")

        return ChatOpenAI(
            model=model,
            api_key=settings.dashscope_api_key,
            base_url=settings.qwen_base_url,
            temperature=temperature,
            streaming=streaming,
        )

    @staticmethod
    def create_openai(
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        streaming: bool = False,
    ) -> ChatOpenAI:
        if not settings.openai_api_key:
            raise RuntimeError("请先配置 OPENAI_API_KEY")

        return ChatOpenAI(
            model=model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=temperature,
            streaming=streaming,
        )