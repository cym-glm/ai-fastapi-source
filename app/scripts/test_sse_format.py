from app.utils.sse import format_done_event, format_error_event, format_sse


def main():
    print("message event:")
    print(
        format_sse(
            event="message",
            data={
                "content": "AI Agent"
            },
        )
    )

    print("done event:")
    print(format_done_event())

    print("error event:")
    print(
        format_error_event(
            message="模型调用失败",
            code=50002,
        )
    )


if __name__ == "__main__":
    main()