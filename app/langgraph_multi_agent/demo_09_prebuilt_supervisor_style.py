"""
这个文件是预构建 supervisor 风格示例。

注意：
1. 需要安装 langgraph-supervisor。
2. 需要配置真实模型。
3. 本课程核心仍然推荐先掌握手写 StateGraph。
"""

from langchain.agents import create_agent
from langgraph_supervisor import create_supervisor


def build_prebuilt_supervisor(model):
    order_agent = create_agent(
        model=model,
        tools=[],
        system_prompt=(
            "你是 OrderAgent，只负责订单相关问题。"
            "不要处理退款政策，不要处理数据分析。"
        ),
    )

    refund_agent = create_agent(
        model=model,
        tools=[],
        system_prompt=(
            "你是 RefundAgent，只负责退款规则和退款建议。"
            "不要处理订单查询，不要处理数据分析。"
        ),
    )

    supervisor = create_supervisor(
        agents=[
            order_agent,
            refund_agent,
        ],
        model=model,
        prompt=(
            "你是 Supervisor。"
            "根据用户问题，把任务交给最合适的 Agent。"
            "如果是订单状态，交给 OrderAgent。"
            "如果是退款规则，交给 RefundAgent。"
        ),
    )

    return supervisor.compile()


def main():
    print("这是预构建 supervisor 风格示例，需要真实 model 才能运行。")
    print("课程项目中建议先使用手写 StateGraph 掌握原理。")


if __name__ == "__main__":
    main()