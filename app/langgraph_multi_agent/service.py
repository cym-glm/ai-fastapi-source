from app.langgraph_multi_agent.graph_factory import create_multi_agent_graph
from app.langgraph_multi_agent.schemas import create_initial_multi_agent_state


class LangGraphMultiAgentService:
    def __init__(self):
        self.ecommerce_graph = create_multi_agent_graph("ecommerce")
        self.data_analysis_graph = create_multi_agent_graph("data_analysis")

    def chat(
        self,
        question: str,
        graph_type: str = "ecommerce",
    ) -> dict:
        graph = (
            self.data_analysis_graph
            if graph_type == "data_analysis"
            else self.ecommerce_graph
        )

        result = graph.invoke(
            create_initial_multi_agent_state(question),
            config={
                "recursion_limit": 30
            },
        )

        return {
            "answer": result["final_answer"],
            "task_type": result["task_type"],
            "plan": result["plan"],
            "agent_trace": result["agent_trace"],
            "logs": result["logs"],
        }


langgraph_multi_agent_service = LangGraphMultiAgentService()