from app.mcp_intro.service import mcp_intro_service


def main():
    cases = [
        "帮我查一下订单 10001 到哪了",
        "订单未发货可以退款吗？",
        "帮我查一下手机号 13800000000 的客户信息",
        "你好，随便聊聊",
    ]

    for case in cases:
        result = mcp_intro_service.run_host_agent(case)

        print("user_request:", result["user_request"])
        print("selected_tool:", result["selected_tool"])
        print("final_answer:")
        print(result["final_answer"])
        print("trace:")
        for item in result["trace"]:
            print("-", item)
        print("=" * 100)


if __name__ == "__main__":
    main()