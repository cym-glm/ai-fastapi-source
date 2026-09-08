from app.llm.factory import LLMProviderFactory, infer_provider_from_model


models = [
    "deepseek-chat",
    "qwen-plus",
    "gpt-4.1-mini",
    "unknown-model",
]

for model in models:
    provider = infer_provider_from_model(model)
    print(model, "=>", provider)

    