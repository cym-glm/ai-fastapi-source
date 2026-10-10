
from langchain.agents import create_agent
from langchain_core.tools import tool
from app.langchain_models.model_factory import LangChainModelFactory


@tool
def get_course_progress(chapter: int) -> str:
    """查询 AI Agent 课程指定章节的学习阶段。"""
    if chapter <= 19:
        return "前 19 章属于原生 AI 应用开发和项目一阶段。"

    if 20 <= chapter <= 28:
        return "第 20 到 28 章属于 LangChain 阶段。"

    if 29 <= chapter <= 38:
        return "第 29 到 38 章属于 LangGraph 阶段。"

    return "该章节属于后续高级项目阶段。"


def main():
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0,
    )

    agent = create_agent(
        model=model,
        tools=[get_course_progress],
        system_prompt=(
            "你是一个 AI Agent 课程助教。"
            "当用户询问课程章节、阶段、进度时，可以调用工具查询。"
        )
    )

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": "请问第 26 章属于哪个阶段？",
            }
        ]
    })

    for message in result["messages"]:
        print(message.type, ":", message.content)
        print("tool_calls: ", getattr(message, "tool_calls", None))
        print("=====")

if __name__ == "__main__":
    main()
