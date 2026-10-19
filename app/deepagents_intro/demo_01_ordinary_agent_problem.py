from app.deepagents_intro.ordinary_agent import OrdinaryAgent


def main():
    agent = OrdinaryAgent()

    result = agent.run(
        "帮我调研一下 AI Agent 平台竞品，并输出一份结构化报告。"
    )

    print(result)


if __name__ == "__main__":
    main()