from app.langgraph_multi_agent.service import langgraph_multi_agent_service


def main():
    ecommerce_result = langgraph_multi_agent_service.chat(
        question="我的订单 10002 可以退款吗？",
        graph_type="ecommerce",
    )

    print("ecommerce_result:")
    print(ecommerce_result)
    print("=" * 120)

    data_result = langgraph_multi_agent_service.chat(
        question="帮我分析最近 30 天销售数据。",
        graph_type="data_analysis",
    )

    print("data_result:")
    print(data_result)


if __name__ == "__main__":
    main()