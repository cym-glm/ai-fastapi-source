from app.mcp_intro.service import mcp_intro_service


def main():
    result = mcp_intro_service.show_without_mcp_problem(
        order_id="10001"
    )

    for key, value in result.items():
        print(key)
        print(value)
        print("=" * 80)


if __name__ == "__main__":
    main()