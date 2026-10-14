"""
LangSmith RAG Evaluation 示例。

说明：
1. 这个文件展示生产环境评估平台思路。
2. 默认不运行。
3. 需要配置 LANGSMITH_API_KEY。
"""


def demo_langsmith_evaluate():
    from langsmith import evaluate

    def rag_app(inputs: dict) -> dict:
        # 从评估数据集中取出本轮待回答的问题
        question = inputs["question"]

        # 这里可以调用你的真实 RAG 应用，返回答案与引用来源。
        # answer 会被评估器 answer_contains_expected 检查是否包含期望关键词。
        return {
            # 此处为占位回答，实际应替换为 RAG 链路生成的答案
            "answer": f"这里返回问题 {question} 的 RAG 回答",
            # 命中的文档片段/来源，供溯源评估使用
            "sources": [],
        }

    def answer_contains_expected(outputs: dict, reference_outputs: dict) -> bool:
        expected_keywords = reference_outputs.get("expected_keywords", [])
        answer = outputs.get("answer", "")

        return all(
            keyword in answer
            for keyword in expected_keywords
        )

    results = evaluate(
        rag_app,
        data="enterprise-rag-golden-dataset",
        evaluators=[answer_contains_expected],
        experiment_prefix="rag-eval-demo",
    )

    return results