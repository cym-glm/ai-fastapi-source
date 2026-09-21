from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def main():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "你是一个专业 AI Agent 课程助教。",
        ),
        MessagesPlaceholder(
            variable_name="history",
            optional=True,
            n_messages=2,
        ),
        (
            "human",
            "{user_question}",
        ),
    ])

    history = [
        HumanMessage(content="什么是 AI Agent？"),
        AIMessage(content="AI Agent 是可以理解目标、规划步骤并调用工具的智能体。"),
    ]

    prompt_value = prompt.invoke({
        "history": [],
        "user_question": "那 LangChain 和 AI Agent 有什么关系？",
    })

    for message in prompt_value.messages:
        print(message.type, ":", message.content)
        print("-" * 80)


if __name__ == "__main__":
    main()