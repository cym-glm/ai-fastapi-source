from abc import ABC, abstractmethod

from app.deepagents_core.schemas import (
    DeepAgentContext,
    DeepAgentState,
)


class DeepAgentMiddleware(ABC):
    @abstractmethod
    def before_run(
        self,
        state: DeepAgentState,
        context: DeepAgentContext,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def after_run(
        self,
        state: DeepAgentState,
        context: DeepAgentContext,
    ) -> None:
        raise NotImplementedError


class TraceMiddleware(DeepAgentMiddleware):
    def before_run(
        self,
        state: DeepAgentState,
        context: DeepAgentContext,
    ) -> None:
        state.trace.append(
            f"[TraceMiddleware] 开始执行 thread_id={context.thread_id}"
        )

    def after_run(
        self,
        state: DeepAgentState,
        context: DeepAgentContext,
    ) -> None:
        state.trace.append(
            f"[TraceMiddleware] 执行结束 thread_id={context.thread_id}"
        )


class ContextGuardMiddleware(DeepAgentMiddleware):
    def before_run(
        self,
        state: DeepAgentState,
        context: DeepAgentContext,
    ) -> None:
        if not context.tenant_id:
            raise ValueError("tenant_id 不能为空")

        if not context.user_id:
            raise ValueError("user_id 不能为空")

        state.trace.append(
            "[ContextGuardMiddleware] 上下文校验通过"
        )

    def after_run(
        self,
        state: DeepAgentState,
        context: DeepAgentContext,
    ) -> None:
        state.trace.append(
            "[ContextGuardMiddleware] 无需后置处理"
        )