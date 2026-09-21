
from langchain_core.prompts import ChatPromptTemplate

def run_prompt_template():
    # prompt_template = ChatPromptTemplate.from_messages([
    #     SystemMessage(content="你是一个专业的AIAAgent课程助手，你需要回答用户的问题"),
    #     HumanMessage(content="{question}")
    # ])
    prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的{role_name}课程助手，你需要回答用户的问题"),
            ("human", "请用一句话解释：{question}")
        ])
    res = prompt.invoke({
        "role_name": "Langchain",
        "question": "什么是Langchain",
    })
    print(type(res))
    print("messages: ")
    print(res)
    for msg in res.messages:
        print(msg.type, ":",msg.content)


if __name__ == "__main__":
    run_prompt_template()