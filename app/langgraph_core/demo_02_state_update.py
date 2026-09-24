from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class ProfileState(TypedDict):
    user_name: str
    role: str
    intro: str


def fill_role_node(state: ProfileState) -> dict:
    return {
        "role": "AI Agent 全栈工程师"
    }


def generate_intro_node(state: ProfileState) -> dict:
    return {
        "intro": f"{state['user_name']} 是一名 {state['role']}。"
    }


def build_graph():
    graph = StateGraph(ProfileState)

    graph.add_node("fill_role", fill_role_node)
    graph.add_node("generate_intro", generate_intro_node)

    graph.add_edge(START, "fill_role")
    graph.add_edge("fill_role", "generate_intro")
    graph.add_edge("generate_intro", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke({
        "user_name": "小陈",
        "role": "",
        "intro": "",
    })

    print(result)


if __name__ == "__main__":
    main()