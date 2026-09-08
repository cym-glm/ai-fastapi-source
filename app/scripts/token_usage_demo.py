from app.llm.schemas import LLMUsage


def estimate_cost(
    usage: LLMUsage,
    input_price_per_1k: float,
    output_price_per_1k: float,
) -> float:
    input_cost = usage.prompt_tokens / 1000 * input_price_per_1k
    output_cost = usage.completion_tokens / 1000 * output_price_per_1k

    return input_cost + output_cost


usage = LLMUsage(
    prompt_tokens=1200,
    completion_tokens=800,
    total_tokens=2000,
)

cost = estimate_cost(
    usage=usage,
    input_price_per_1k=0.001,
    output_price_per_1k=0.002,
)

print("usage:", usage.model_dump())
print("cost:", cost)