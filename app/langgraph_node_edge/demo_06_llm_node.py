import asyncio
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage

from langgraph.graph import END, START, StateGraph

from app.langchain_models.model_factory import LangChainModelFactory


class LLMNodeState(TypedDict):
    user_question: str
    draft_answer: str
    final_answer: str


async def draft_answer_node(state: LLMNodeState) -> dict:
    # 创建 LLM 模型实例
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.3,
    )
    # 调用 LLM 进行问答
    response = await model.ainvoke([
        SystemMessage(
            content=(
                "你是一个 AI Agent 课程助教。"
                "回答要简洁、口语化。"
            )
        ),
        HumanMessage(
            content=state["user_question"]
        ),
    ])

    return {
        "draft_answer": str(response.content)
    }


async def polish_answer_node(state: LLMNodeState) -> dict:
    return {
        "final_answer": (
            "【最终回答】\n"
            + state["draft_answer"].strip()
        )
    }


def build_graph():
    graph = StateGraph(LLMNodeState)

    graph.add_node("draft_answer", draft_answer_node)
    graph.add_node("polish_answer", polish_answer_node)

    graph.add_edge(START, "draft_answer")
    graph.add_edge("draft_answer", "polish_answer")
    graph.add_edge("polish_answer", END)

    return graph.compile()


async def main():
    app = build_graph()

    result = await app.ainvoke({
        "user_question": "为什么复杂 Agent 需要 LangGraph？",
        "draft_answer": "",
        "final_answer": "",
    })

    print(result["final_answer"])


if __name__ == "__main__":
    asyncio.run(main())