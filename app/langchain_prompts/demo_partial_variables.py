from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate


def main():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个专业的 {role_name}。\n"
                "当前日期：{current_date}\n"
                "回答要求：{answer_style}"
            ),
        ),
        (
            "human",
            "{user_question}",
        ),
    ])

    prompt = prompt.partial(
        role_name="AI Agent 课程助教",
        current_date=datetime.now().strftime("%Y-%m-%d"),
        answer_style="口语化、结构清晰、不要编造。",
    )

    print("input_variables:", prompt.input_variables)
    print("partial_variables:", prompt.partial_variables)

    prompt_value = prompt.invoke({
        "user_question": "为什么 Prompt 需要版本管理？",
    })

    for message in prompt_value.messages:
        print(message.type, ":", message.content)
        print("-" * 80)


if __name__ == "__main__":
    main()