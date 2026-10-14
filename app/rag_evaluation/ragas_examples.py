"""
Ragas RAG Evaluation 示例。

说明：
1. 这个文件展示生产环境评估指标思路。
2. 默认不运行。
3. 需要安装 ragas，并配置对应 LLM / Embedding。
"""


def demo_ragas_metrics():
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    dataset = Dataset.from_dict({
        "question": [
            "订单未发货可以退款吗？"
        ],
        "answer": [
            "订单未发货时可以申请取消订单并退款。"
        ],
        "contexts": [
            [
                "订单未发货时，用户可以申请取消订单并退款。"
            ]
        ],
        "ground_truth": [
            "订单未发货时，可以申请取消订单并退款。"
        ],
    })

    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
    )

    return result