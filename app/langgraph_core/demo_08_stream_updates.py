from app.langgraph_core.demo_03_sequence_graph import build_graph


def main():
    app = build_graph()

    input_state = {
        "topic": "LangGraph Streaming",
        "outline": "",
        "script": "",
        "summary": "",
    }

    print("stream_mode=updates")
    print("=" * 80)

    for chunk in app.stream(
        input_state,
        stream_mode="updates",
    ):
        print(chunk)

    print("=" * 80)
    print("stream_mode=values")
    print("=" * 80)

    for chunk in app.stream(
        input_state,
        stream_mode="values",
    ):
        print(chunk)
        print("-" * 80)


if __name__ == "__main__":
    main()