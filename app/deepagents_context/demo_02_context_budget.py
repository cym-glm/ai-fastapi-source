from app.deepagents_context.schemas import ContextBudget


def main():
    budget = ContextBudget(
        max_tokens=4000,
        reserved_for_system=500,
        reserved_for_user_goal=500,
        reserved_for_answer=800,
    )

    print("max_tokens:", budget.max_tokens)
    print("reserved_for_system:", budget.reserved_for_system)
    print("reserved_for_user_goal:", budget.reserved_for_user_goal)
    print("reserved_for_answer:", budget.reserved_for_answer)
    print("available_tokens:", budget.available_tokens)


if __name__ == "__main__":
    main()