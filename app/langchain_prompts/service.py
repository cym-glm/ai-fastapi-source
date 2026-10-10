from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import ChatPromptValue

from app.langchain_prompts.registry import (
    LangChainPromptDefinition,
    langchain_prompt_registry,
)
from app.prompts.base import PromptScenario


class LangChainPromptService:
    def get_by_prompt_id(
        self,
        prompt_id: str,
        version: str = "v1",
    ) -> LangChainPromptDefinition:
        return langchain_prompt_registry.get_by_prompt_id(
            prompt_id=prompt_id,
            version=version,
        )

    def get_by_scenario(
        self,
        scenario: PromptScenario,
        version: str = "v1",
    ) -> LangChainPromptDefinition:
        return langchain_prompt_registry.get_by_scenario(
            scenario=scenario,
            version=version,
        )

    def render_by_prompt_id(
        self,
        prompt_id: str,
        variables: dict,
        version: str = "v1",
    ) -> ChatPromptValue:
        definition = self.get_by_prompt_id(
            prompt_id=prompt_id,
            version=version,
        )

        return definition.prompt.invoke(variables)

    def render_messages_by_prompt_id(
        self,
        prompt_id: str,
        variables: dict,
        version: str = "v1",
    ) -> list[BaseMessage]:
        prompt_value = self.render_by_prompt_id(
            prompt_id=prompt_id,
            variables=variables,
            version=version,
        )

        return prompt_value.messages

    def render_by_scenario(
        self,
        scenario: PromptScenario,
        variables: dict,
        version: str = "v1",
    ) -> ChatPromptValue:
        definition = self.get_by_scenario(
            scenario=scenario,
            version=version,
        )

        return definition.prompt.invoke(variables)

    def render_messages_by_scenario(
        self,
        scenario: PromptScenario,
        variables: dict,
        version: str = "v1",
    ) -> list[BaseMessage]:
        prompt_value = self.render_by_scenario(
            scenario=scenario,
            variables=variables,
            version=version,
        )

        return prompt_value.messages

    def list_prompts(self) -> list[dict]:
        return [
            {
                "prompt_id": definition.prompt_id,
                "name": definition.name,
                "scenario": definition.scenario.value,
                "version": definition.version,
                "description": definition.description,
                "enabled": definition.enabled,
                "input_variables": definition.prompt.input_variables,
                "optional_variables": definition.prompt.optional_variables,
                "metadata": definition.prompt.metadata,
                "tags": definition.prompt.tags,
            }
            for definition in langchain_prompt_registry.list()
        ]


langchain_prompt_service = LangChainPromptService()