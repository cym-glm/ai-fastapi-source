from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="AI Agent Course API")
    app_env: str = Field(default="development")
    app_version: str = Field(default="0.1.0")
    api_v1_prefix: str = Field(default="/api/v1")
    debug: bool = Field(default=False)

    app_api_key: str = Field(default="dev-api-key-123")
    default_model: str = Field(default="deepseek-chat")
    supported_models: str = Field(default="deepseek-chat,qwen-plus,gpt-4o-mini")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:sohucw@localhost:5432/ai_agent"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_default_ttl_seconds: int = Field(default=300)
    rate_limit_window_seconds: int = Field(default=60)
    rate_limit_max_requests: int = Field(default=20)

    openai_api_key: str = Field(default="")
    openai_base_url: str = Field(default="https://api.openai.com/v1")

    deepseek_api_key: str = Field(default="")
    deepseek_base_url: str = Field(default="https://api.deepseek.com")

    dashscope_api_key: str = Field(default="")
    qwen_base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1")


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def supported_model_list(self) -> list[str]:
        return [
            model.strip()
            for model in self.supported_models.split(",")
            if model.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()