from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ValidateState(TypedDict):
    pending_payload: dict
    human_decision: dict | None
    final_answer: str
    errors: list[str]


def validate_decision(decision: dict) -> list[str]:
    errors = []

    decision_type = decision.get("type")

    if decision_type not in ["approve", "reject", "edit"]:
        errors.append("type 必须是 approve / reject / edit")

    if not decision.get("reviewer_id"):
        errors.append("reviewer_id 不能为空")

    if decision_type == "edit":
        edited_payload = decision.get("edited_payload")

        if not isinstance(edited_payload, dict):
            errors.append("edit 时 edited_payload 必须是 dict")
        else:
            amount = edited_payload.get("amount")

            if not isinstance(amount, int | float) or amount <= 0:
                errors.append("edited_payload.amount 必须是大于 0 的数字")

    return errors


def review_node(state: ValidateState) -> dict:
    decision = interrupt({
        "type": "validate_review",
        "pending_payload": state["pending_payload"],
        "options": ["approve", "reject", "edit"],
    })

    errors = validate_decision(decision)

    if errors:
        return {
            "human_decision": decision,
            "errors": errors,
            "final_answer": "人工审核输入不合法，需要重新提交。",
        }

    return {
        "human_decision": decision,
        "errors": [],
    }


def route_after_review(
    state: ValidateState,
) -> Literal["invalid", "valid"]:
    if state["errors"]:
        return "invalid"

    return "valid"


def invalid_node(state: ValidateState) -> dict:
    return {
        "final_answer": "审核失败：" + "；".join(state["errors"])
    }


def valid_node(state: ValidateState) -> dict:
    return {
        "final_answer": f"审核通过，决策为：{state['human_decision']}"
    }


def build_graph():
    graph = StateGraph(ValidateState)

    graph.add_node("review", review_node)
    graph.add_node("invalid", invalid_node)
    graph.add_node("valid", valid_node)

    graph.add_edge(START, "review")

    graph.add_conditional_edges(
        "review",
        route_after_review,
        {
            "invalid": "invalid",
            "valid": "valid",
        },
    )

    graph.add_edge("invalid", END)
    graph.add_edge("valid", END)

    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "thread_validate_human_input"
        }
    }

    first = app.invoke(
        {
            "pending_payload": {
                "order_id": "10003",
                "amount": 1299.0,
            },
            "human_decision": None,
            "final_answer": "",
            "errors": [],
        },
        config=config,
    )

    print("first:")
    print(first)

    print("=" * 80)

    second = app.invoke(
        Command(resume={
            "type": "edit",
            "reviewer_id": "admin_001",
            "edited_payload": {
                "order_id": "10003",
                "amount": 1099.0,
            },
        }),
        config=config,
    )

    print("second:")
    print(second)


if __name__ == "__main__":
    main()