from pydantic import BaseModel

from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider
from app.llm.errors import LLMProviderError
from app.llm.schemas import LLMRequest
from app.prompts.base import PromptScenario
from app.services.prompt_service import prompt_service
from app.structured_outputs.parser import (
    StructuredOutputParseError,
    parse_structured_output,
)
from app.structured_outputs.response_format import (
    build_json_object_response_format,
)
from app.structured_outputs.schemas import (
    AgentPlanOutput,
    IntentClassificationOutput,
    RAGStructuredAnswerOutput,
)
from app.structured_outputs.retry import  parse_or_repair_structured_output


logger = get_logger(__name__)


class StructuredOutputService:
    async def classify_intent(
        self,
        user_question: str,
        model: str,
        llm_provider: BaseLLMProvider,
    ) -> IntentClassificationOutput:
        messages = prompt_service.render_by_prompt_id(
            prompt_id="intent_classification_structured",
            variables={
                "user_question": user_question,
            },
        )

        request = LLMRequest(
            model=model,
            messages=messages,
            temperature=0.1,
            stream=False,
            response_format=build_json_object_response_format(),
        )

        return await self._call_and_parse(
            request=request,
            llm_provider=llm_provider,
            schema=IntentClassificationOutput,
            task_name="intent_classification",
        )

    async def generate_rag_answer(
        self,
        user_question: str,
        retrieved_context: str,
        model: str,
        llm_provider: BaseLLMProvider,
    ) -> RAGStructuredAnswerOutput:
        messages = prompt_service.render_by_prompt_id(
            prompt_id="rag_structured_answer",
            variables={
                "user_question": user_question,
                "retrieved_context": retrieved_context,
            },
        )

        request = LLMRequest(
            model=model,
            messages=messages,
            temperature=0.1,
            stream=False,
            response_format=build_json_object_response_format(),
        )

        return await self._call_and_parse(
            request=request,
            llm_provider=llm_provider,
            schema=RAGStructuredAnswerOutput,
            task_name="rag_structured_answer",
        )

    async def plan_agent_task(
        self,
        user_goal: str,
        available_tools: str,
        constraints: str,
        model: str,
        llm_provider: BaseLLMProvider,
    ) -> AgentPlanOutput:
        messages = prompt_service.render_by_prompt_id(
            prompt_id="agent_plan_structured",
            variables={
                "user_goal": user_goal,
                "available_tools": available_tools,
                "constraints": constraints,
            },
        )

        request = LLMRequest(
            model=model,
            messages=messages,
            temperature=0.1,
            stream=False,
            response_format=build_json_object_response_format(),
        )

        return await self._call_and_parse(
            request=request,
            llm_provider=llm_provider,
            schema=AgentPlanOutput,
            task_name="agent_plan",
        )

    async def _call_and_parse(
        self,
        request: LLMRequest,
        llm_provider: BaseLLMProvider,
        schema: type[BaseModel],
        task_name: str,
    ):
        logger.info(
            f"structured_output_start task={task_name} "
            f"model={request.model} schema={schema.__name__}"
        )

        try:
            response = await llm_provider.chat(request)

        except LLMProviderError as exc:
            logger.exception(
                f"structured_output_llm_error task={task_name} "
                f"provider={exc.provider} status_code={exc.status_code}"
            )

            raise AppException(
                message="结构化输出模型调用失败",
                code=ErrorCode.LLM_CALL_FAILED,
                status_code=500,
                data={
                    "task": task_name,
                    "provider": exc.provider,
                    "status_code": exc.status_code,
                },
            ) from exc

        try:
            # result = parse_structured_output(
            #     raw_text=response.content,
            #     schema=schema,
            # )
            result = await parse_or_repair_structured_output(
                raw_text=response.content,
                schema=schema,
                model=request.model,
                llm_provider=llm_provider,
            )

        except StructuredOutputParseError as exc:
            logger.warning(
                f"structured_output_parse_failed task={task_name} "
                f"detail={exc.detail}"
            )

            raise AppException(
                message="模型结构化输出解析失败",
                code=ErrorCode.LLM_RESPONSE_PARSE_FAILED,
                status_code=500,
                data={
                    "task": task_name,
                    "detail": exc.detail,
                },
            ) from exc

        logger.info(
            f"structured_output_success task={task_name} "
            f"schema={schema.__name__}"
        )

        return result


structured_output_service = StructuredOutputService()