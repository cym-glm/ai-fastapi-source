from pydantic import BaseModel

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger
from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_structured_outputs.schemas import (
    AgentPlanResult,
    IntentClassificationResult,
    RAGAnswerResult,
)
from app.langchain_structured_outputs.retry import parse_with_repair


logger = get_logger(__name__)


class LangChainStructuredOutputService:
    async def classify_intent(
        self,
        user_question: str,
        provider: str = "deepseek",
        model_name: str = "deepseek-chat",
    ) -> IntentClassificationResult:
        return await self._run_pydantic_chain(
            schema=IntentClassificationResult,
            provider=provider,
            model_name=model_name,
            task_name="intent_classification",
            system_prompt=(
                "你是一个电商客服意图识别器。\n"
                "你需要识别用户问题属于哪一类意图。\n"
                "不要输出 Markdown，不要输出解释性文字。"
            ),
            human_template="用户问题：{user_question}",
            variables={
                "user_question": user_question,
            },
        )

    async def generate_rag_answer(
        self,
        user_question: str,
        retrieved_context: str,
        provider: str = "deepseek",
        model_name: str = "deepseek-chat",
    ) -> RAGAnswerResult:
        return await self._run_pydantic_chain(
            schema=RAGAnswerResult,
            provider=provider,
            model_name=model_name,
            task_name="rag_structured_answer",
            system_prompt=(
                "你是一个企业知识库问答助手。\n"
                "只能基于提供的知识库片段回答。\n"
                "如果知识库没有答案，is_answered 必须为 false。\n"
                "citations 只能包含知识库片段中出现的 document_id。\n"
                "不要编造引用。\n"
                "\n"
                "知识库片段：\n"
                "{retrieved_context}"
            ),
            human_template="用户问题：{user_question}",
            variables={
                "user_question": user_question,
                "retrieved_context": retrieved_context,
            },
        )

    async def plan_agent_task(
        self,
        user_goal: str,
        available_tools: str,
        constraints: str,
        provider: str = "deepseek",
        model_name: str = "deepseek-chat",
    ) -> AgentPlanResult:
        return await self._run_pydantic_chain(
            schema=AgentPlanResult,
            provider=provider,
            model_name=model_name,
            task_name="agent_plan",
            system_prompt=(
                "你是一个 AI Agent 任务规划器。\n"
                "只能使用 available_tools 中列出的工具。\n"
                "不要编造不存在的工具。\n"
                "如果信息不足，要规划 ask_user 步骤。\n"
                "如果需要高风险操作，need_human_confirm 必须为 true。\n"
                "\n"
                "可用工具：\n"
                "{available_tools}\n"
                "\n"
                "约束条件：\n"
                "{constraints}"
            ),
            human_template="用户目标：{user_goal}",
            variables={
                "user_goal": user_goal,
                "available_tools": available_tools,
                "constraints": constraints,
            },
        )

    async def _run_pydantic_chain(
        self,
        schema: type[BaseModel],
        provider: str,
        model_name: str,
        task_name: str,
        system_prompt: str,
        human_template: str,
        variables: dict,
    ):
        parser = PydanticOutputParser(
            pydantic_object=schema,
        )

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                (
                    system_prompt
                    + "\n\n"
                    + "你必须严格按照下面格式输出。\n"
                    + "不要输出 Markdown，不要输出额外解释。\n"
                    + "{format_instructions}"
                ),
            ),
            (
                "human",
                human_template,
            ),
        ]).partial(
            format_instructions=parser.get_format_instructions()
        )

        model = LangChainModelFactory.create(
            provider=provider,
            model=model_name,
            temperature=0,
        )

        chain = prompt | model | parser

        logger.info(
            f"langchain_structured_output_start task={task_name} "
            f"schema={schema.__name__} model={model_name}"
        )

        try:
            result = await chain.ainvoke(variables)

        except Exception as exc:
            logger.warning(
                f"langchain_structured_output_parse_failed "
                f"task={task_name} error={repr(exc)}"
            )

            raise AppException(
                message="LangChain 结构化输出解析失败",
                code=ErrorCode.STRUCTURED_OUTPUT_PARSE_FAILED,
                status_code=500,
                data={
                    "task": task_name,
                    "schema": schema.__name__,
                    "error": repr(exc),
                },
            ) from exc

        logger.info(
            f"langchain_structured_output_success task={task_name} "
            f"schema={schema.__name__}"
        )

        return result

    async def parse_or_repair(
        self,
        raw_text: str,
        schema: type[BaseModel],
        provider: str = "deepseek",
        model_name: str = "deepseek-chat",
    ):
        return await parse_with_repair(
            raw_text=raw_text,
            schema=schema,
            provider=provider,
            model_name=model_name,
        )


langchain_structured_output_service = LangChainStructuredOutputService()