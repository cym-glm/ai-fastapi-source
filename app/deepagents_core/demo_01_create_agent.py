from app.deepagents_core.graph import create_teaching_deep_agent
from app.deepagents_core.tools import build_default_tools


def main():
    agent = create_teaching_deep_agent(
        model="teaching-model",
        tools=build_default_tools(),
        system_prompt="你是企业 DeepAgent。",
        name="demo-agent",
    )

    print("agent:", agent)
    print("config name:", agent.config.name)
    print("model:", agent.config.model)
    print("tools:", [tool.name for tool in agent.config.tools])


if __name__ == "__main__":
    main()