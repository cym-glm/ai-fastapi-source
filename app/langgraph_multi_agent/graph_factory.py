from app.langgraph_multi_agent.demo_07_ecommerce_multi_agent import (
    build_graph as build_ecommerce_multi_agent_graph,
)
from app.langgraph_multi_agent.demo_08_data_analysis_multi_agent import (
    build_graph as build_data_analysis_multi_agent_graph,
)


def create_multi_agent_graph(
    graph_type: str = "ecommerce",
):
    if graph_type == "data_analysis":
        return build_data_analysis_multi_agent_graph()

    return build_ecommerce_multi_agent_graph()