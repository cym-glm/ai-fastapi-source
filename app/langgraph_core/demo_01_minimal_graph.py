from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class HelloState(TypedDict):
    user_name:str
    greeting:str


def greeting_node(state:HelloState) -> dict:
    user_name = state["user_name"]
    return {
        "greeting":f"你好，{user_name}!"
    }


def build_graph():
    
    graph = StateGraph(HelloState)

    graph.add_node("greeting", greeting_node)

    graph.add_edge(START, "greeting")
    graph.add_edge("greeting", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"user_name":"张三", "greeting": ""})
    print(result)

