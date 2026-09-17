from app.prompts.base import PromptScenario
from app.services.prompt_service import prompt_service


def main():
    messages = prompt_service.render_by_scenario(
        scenario=PromptScenario.GENERAL_CHAT,
        variables={
            "user_question": "什么是 Prompt Engineering？"
        },
    )

    for message in messages:
        print("role:", message.role)
        print("content:")
        print(message.content)
        print("=" * 60)


if __name__ == "__main__":
    main()