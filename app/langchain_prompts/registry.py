from pydantic import BaseModel, ConfigDict, Field
from langchain_core.prompts import ChatPromptTemplate

from app.prompts.base import PromptScenario
from app.langchain_prompts.templates import (
    AGENT_PLANNER_PROMPT,
    ECOMMERCE_CUSTOMER_SERVICE_PROMPT,
    GENERAL_CHAT_PROMPT,
    RAG_QA_PROMPT,
)


class LangChainPromptDefinition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    prompt_id: str = Field(..., description="Prompt ID")
    name: str = Field(..., description="Prompt 名称")
    scenario: PromptScenario = Field(..., description="Prompt 场景")
    version: str = Field(default="v1", description="Prompt 版本")
    description: str = Field(default="", description="Prompt 描述")
    prompt: ChatPromptTemplate = Field(..., description="LangChain ChatPromptTemplate")
    enabled: bool = Field(default=True, description="是否启用")


class LangChainPromptRegistry:
    def __init__(self):
        self._prompts: dict[str, LangChainPromptDefinition] = {}

    def register(self, definition: LangChainPromptDefinition):
        key = self._build_key(
            prompt_id=definition.prompt_id,
            version=definition.version,
        )

        self._prompts[key] = definition

    def get_by_prompt_id(
        self,
        prompt_id: str,
        version: str = "v1",
    ) -> LangChainPromptDefinition:
        key = self._build_key(
            prompt_id=prompt_id,
            version=version,
        )

        if key not in self._prompts:
            raise KeyError(f"Prompt 不存在：{prompt_id}@{version}")

        definition = self._prompts[key]

        if not definition.enabled:
            raise KeyError(f"Prompt 已禁用：{prompt_id}@{version}")

        return definition

    def get_by_scenario(
        self,
        scenario: PromptScenario,
        version: str = "v1",
    ) -> LangChainPromptDefinition:
        for definition in self._prompts.values():
            if definition.scenario == scenario and definition.version == version and definition.enabled:
                return definition

        raise KeyError(f"未找到场景 Prompt：{scenario}@{version}")

    def list(self) -> list[LangChainPromptDefinition]:
        return list(self._prompts.values())

    def _build_key(
        self,
        prompt_id: str,
        version: str,
    ) -> str:
        return f"{prompt_id}:{version}"


langchain_prompt_registry = LangChainPromptRegistry()


langchain_prompt_registry.register(
    LangChainPromptDefinition(
        prompt_id="general_chat",
        name="通用聊天 Prompt",
        scenario=PromptScenario.GENERAL_CHAT,
        version="v1",
        description="用于普通 AI Chat 问答。",
        prompt=GENERAL_CHAT_PROMPT,
    )
)

langchain_prompt_registry.register(
    LangChainPromptDefinition(
        prompt_id="ecommerce_customer_service",
        name="电商客服 Prompt",
        scenario=PromptScenario.ECOMMERCE_CUSTOMER_SERVICE,
        version="v1",
        description="用于跨境电商客服场景。",
        prompt=ECOMMERCE_CUSTOMER_SERVICE_PROMPT,
    )
)

langchain_prompt_registry.register(
    LangChainPromptDefinition(
        prompt_id="rag_qa",
        name="RAG 问答 Prompt",
        scenario=PromptScenario.RAG_QA,
        version="v1",
        description="用于企业知识库问答。",
        prompt=RAG_QA_PROMPT,
    )
)

langchain_prompt_registry.register(
    LangChainPromptDefinition(
        prompt_id="agent_planner",
        name="Agent 规划 Prompt",
        scenario=PromptScenario.AGENT_PLANNER,
        version="v1",
        description="用于 Agent 任务规划。",
        prompt=AGENT_PLANNER_PROMPT,
    )
)