
from deepagents import create_deep_agent 
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing_extensions import TypedDict

class EnterpriseDeepAgentContext(TypedDict):
    tenant_id: str
    user_id: str
    department: str
    roles: list[str]
    task_id: str
class ResearchReportOutput(BaseModel):
    title: str
    summary: str
    findings: list[str]
    risks: list[str]
    next_steps: list[str]

def search_knowledge_base(query: str) -> str:
    """Search enterprise knowledge base."""
    return f"知识库中与 {query} 相关的资料：订单未发货可以申请退款。"


def query_order(order_id: str) -> str:
    """Query order details."""
    return {
        "order_status": "未发货",
        "refundable": True,
    }

def wirte_report(report: str) -> None:
    """Write report to file."""
    with open("report.txt", "w") as f:
        f.write(report)


def query_customer(customer_id: str) -> dict[str, Any]:
    """Query customer details."""
    return {
        "name": "张三",
        "email": "zhangsan@example.com",
    }


model = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    max_tokens=100,
    streaming=False,
    verbose=True,
)

research_subagent = {
    "name": "research-agent",
    "description": "负责资料检索、阅读和整理，只返回结构化研究笔记。",
    "prompt": """
你是 Research SubAgent。
你的任务是收集资料、提取事实、整理来源。
不要写最终报告，只输出研究笔记。
""",
    "tools": [wirte_report],
}


checkpointer = InMemorySaver()

agent = create_deep_agent(
    model= model,
    tools=[search_knowledge_base, query_order, wirte_report],
    system_prompt="你是一个企业知识库助理，专门帮助用户查询企业知识库中的资料。",
    middleware=[],
    subagents=[research_subagent],
    skills=["search_knowledge_base"],
    memory=[],
    permissions=None,
    backend=None,
    interrupt_on={
        "send_email": True,
        "delete_file": True,
    },
    response_format=ResearchReportOutput,
    state_schema=None,
    context_schema=None,
    checkpointer=checkpointer,
    store=None,
    debug=False,
    name="enterprise_kb_assistant",
    cache=None,
)


res = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "我想查询订单未发货的退款政策。"
        }
    ]},
    config={
        "configurable": {
            "thread_id": "thread_001",
        }
    }
    )

print(res)