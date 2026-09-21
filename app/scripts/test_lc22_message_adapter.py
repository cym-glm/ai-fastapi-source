from app.langchain_models.message_adapter import to_langchain_messages
from app.llm.schemas import LLMMessage, LLMRole


def main():
    messages = [
        LLMMessage(
            role=LLMRole.SYSTEM,
            content="你是一个专业 AI Agent 课程助教。",
        ),
        LLMMessage(
            role=LLMRole.USER,
            content="请解释 MessageAdapter 的作用。",
        ),
    ]

    langchain_messages = to_langchain_messages(messages)

    for message in langchain_messages:
        print(message.__class__.__name__)
        print(message.type)
        print(message.content)
        print("=" * 80)


if __name__ == "__main__":
    main()