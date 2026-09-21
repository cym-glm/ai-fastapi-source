

from langchain_core.prompts import ChatPromptTemplate

def main():
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是一个专业的{role_name}课程助手，你需要回答用户的问题"
            "回答要求： \n"
            "1. 回答要简洁明了，不要啰嗦 \n"
            "2. 回答要专业严谨，不要口语化 "
        )),
        ("human", "用户问题： ${question}")
    ])

    prompt_value  = prompt.invoke({
        "role_name": "AI Agent",
        "question": "Langchain和直接调用大模型api有什么区别？"
    })

    print("type:", type(prompt_value))
    # print(prompt.format_messages())

    for message in prompt_value:
        print(message.type,":",message.countent)

if __name__ == "__main__":
    main()