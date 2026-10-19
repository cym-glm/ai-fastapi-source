from app.deepagents_core.backend import (
    InMemoryDeepAgentBackend,
)
from app.deepagents_core.middleware import (
    ContextGuardMiddleware,
    DeepAgentMiddleware,
    TraceMiddleware,
)
from app.deepagents_core.model import TeachingChatModel
from app.deepagents_core.schemas import (
    DeepAgentConfig,
    DeepAgentContext,
    DeepAgentMessage,
    DeepAgentRunInput,
    DeepAgentRunOutput,
    DeepAgentState,
    DeepTodoStatus,
    DeepTool,
)
from app.deepagents_core.subagents import (
    TeachingSubAgentRunner,
)


class TeachingDeepAgentGraph:
    """
    教学版 DeepAgent Graph。

    对标真实 create_deep_agent 返回的可执行 Agent / Graph。
    """

    def __init__(
        self,
        config: DeepAgentConfig,
        backend=None,
        middleware: list[DeepAgentMiddleware] | None = None,
    ):
        self.config = config
        self.model = TeachingChatModel(config.model)
        self.backend = backend or InMemoryDeepAgentBackend()
        self.middleware = middleware or [
            ContextGuardMiddleware(),
            TraceMiddleware(),
        ]
        self.subagent_runner = TeachingSubAgentRunner(
            config.subagents
        )

    def invoke(
        self,
        input_data: dict,
        config: dict | None = None,
    ) -> dict:
        context = self._build_context(config)
        messages = self._build_messages(input_data)

        run_input = DeepAgentRunInput(
            messages=messages,
            context=context,
        )

        output = self.run(run_input)

        return {
            "thread_id": output.thread_id,
            "task_id": output.task_id,
            "final_answer": output.final_answer,
            "todos": [
                {
                    "todo_id": todo.todo_id,
                    "title": todo.title,
                    "status": todo.status.value,
                    "result": todo.result,
                }
                for todo in output.todos
            ],
            "files": output.files,
            "trace": output.trace,
        }

    def run(
        self,
        run_input: DeepAgentRunInput,
    ) -> DeepAgentRunOutput:
        context = run_input.context
        state = self.backend.get_state(context.thread_id)

        state.messages.extend(run_input.messages)

        for item in self.middleware:
            item.before_run(state, context)

        user_request = self._latest_user_message(state)

        state.trace.append(
            f"使用模型：{self.config.model}"
        )
        state.trace.append(
            f"Agent 名称：{self.config.name}"
        )

        state.todos = self.model.make_plan(
            user_request
        )
        state.trace.append("生成 Todo List")

        self._write_todos(context, state)

        self._mark_todo(
            state,
            "todo_001",
            DeepTodoStatus.DOING,
        )
        self._mark_todo(
            state,
            "todo_001",
            DeepTodoStatus.DONE,
            "已明确任务目标。",
        )

        self._mark_todo(
            state,
            "todo_002",
            DeepTodoStatus.DOING,
        )
        research_notes = self._run_tool(
            "search_enterprise_knowledge_base",
            {
                "query": user_request,
            },
            state,
        )
        self.backend.write_file(
            context.thread_id,
            "/research_notes.md",
            research_notes,
        )
        state.trace.append("写入 /research_notes.md")
        self._mark_todo(
            state,
            "todo_002",
            DeepTodoStatus.DONE,
            "已完成资料收集。",
        )

        self._mark_todo(
            state,
            "todo_003",
            DeepTodoStatus.DOING,
        )
        subagent_result = self.subagent_runner.run(
            "research-agent",
            "整理 DeepAgents 核心架构资料",
        )
        analysis_notes = (
            "分析结果：DeepAgents 核心架构包括 model、tools、system_prompt、"
            "backend、filesystem、subagents、middleware、checkpointer 和 store。\n\n"
            f"SubAgent 补充：{subagent_result.result}"
        )
        self.backend.write_file(
            context.thread_id,
            "/analysis_notes.md",
            analysis_notes,
        )
        state.trace.append("写入 /analysis_notes.md")
        self._mark_todo(
            state,
            "todo_003",
            DeepTodoStatus.DONE,
            "已完成资料分析。",
        )

        self._mark_todo(
            state,
            "todo_004",
            DeepTodoStatus.DOING,
        )
        final_answer = self.model.generate_final_answer(
            user_request=user_request,
            research_notes=research_notes,
            analysis_notes=analysis_notes,
        )
        self.backend.write_file(
            context.thread_id,
            "/draft_report.md",
            final_answer,
        )
        self._mark_todo(
            state,
            "todo_004",
            DeepTodoStatus.DONE,
            "已生成报告草稿。",
        )

        self._mark_todo(
            state,
            "todo_005",
            DeepTodoStatus.DOING,
        )
        review_result = self.subagent_runner.run(
            "reviewer-agent",
            "检查 DeepAgents 架构报告是否完整",
        )
        self.backend.write_file(
            context.thread_id,
            "/review_notes.md",
            review_result.result,
        )
        self._mark_todo(
            state,
            "todo_005",
            DeepTodoStatus.DONE,
            "已完成报告检查。",
        )

        self._mark_todo(
            state,
            "todo_006",
            DeepTodoStatus.DOING,
        )
        final_answer = (
            final_answer
            + "\n\n## 五、Review 结果\n\n"
            + review_result.result
        )
        state.final_answer = final_answer
        self.backend.write_file(
            context.thread_id,
            "/final_report.md",
            final_answer,
        )
        self._mark_todo(
            state,
            "todo_006",
            DeepTodoStatus.DONE,
            "已输出最终结果。",
        )

        self._write_todos(context, state)

        for item in self.middleware:
            item.after_run(state, context)

        self.backend.save_state(
            context.thread_id,
            state,
        )

        return DeepAgentRunOutput(
            thread_id=context.thread_id,
            task_id=context.task_id,
            final_answer=final_answer,
            todos=state.todos,
            files=self.backend.list_files(context.thread_id),
            trace=state.trace,
        )

    def _run_tool(
        self,
        tool_name: str,
        arguments: dict,
        state: DeepAgentState,
    ) -> str:
        tool_map: dict[str, DeepTool] = {
            tool.name: tool
            for tool in self.config.tools
        }

        tool = tool_map.get(tool_name)

        if not tool:
            state.trace.append(
                f"工具不存在：{tool_name}"
            )
            return ""

        state.trace.append(
            f"调用工具：{tool_name} args={arguments}"
        )

        return tool.func(**arguments)

    def _write_todos(
        self,
        context: DeepAgentContext,
        state: DeepAgentState,
    ) -> None:
        content = "# Todo List\n\n"

        for todo in state.todos:
            content += f"- [{todo.status.value}] {todo.todo_id}：{todo.title}\n"

            if todo.result:
                content += f"  - 结果：{todo.result}\n"

        self.backend.write_file(
            context.thread_id,
            "/todos.md",
            content,
        )

    def _mark_todo(
        self,
        state: DeepAgentState,
        todo_id: str,
        status: DeepTodoStatus,
        result: str | None = None,
    ) -> None:
        for todo in state.todos:
            if todo.todo_id == todo_id:
                todo.status = status

                if result:
                    todo.result = result

                return

    def _latest_user_message(
        self,
        state: DeepAgentState,
    ) -> str:
        for message in reversed(state.messages):
            if message.role == "user":
                return message.content

        return ""

    def _build_context(
        self,
        config: dict | None,
    ) -> DeepAgentContext:
        configurable = {}

        if config:
            configurable = config.get(
                "configurable",
                {},
            )

        return DeepAgentContext(
            tenant_id=configurable.get(
                "tenant_id",
                "tenant_001",
            ),
            user_id=configurable.get(
                "user_id",
                "anonymous",
            ),
            thread_id=configurable.get(
                "thread_id",
                "default_thread",
            ),
            task_id=configurable.get(
                "task_id",
                "default_task",
            ),
        )

    def _build_messages(
        self,
        input_data: dict,
    ) -> list[DeepAgentMessage]:
        raw_messages = input_data.get(
            "messages",
            [],
        )

        messages: list[DeepAgentMessage] = []

        for item in raw_messages:
            if isinstance(item, DeepAgentMessage):
                messages.append(item)
                continue

            messages.append(
                DeepAgentMessage(
                    role=item.get("role", "user"),
                    content=item.get("content", ""),
                )
            )

        return messages


def create_teaching_deep_agent(
    model: str,
    tools: list[DeepTool],
    system_prompt: str,
    name: str = "teaching-deep-agent",
    subagents=None,
    backend=None,
    middleware=None,
    debug: bool = False,
) -> TeachingDeepAgentGraph:
    config = DeepAgentConfig(
        name=name,
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        subagents=subagents or [],
        debug=debug,
    )

    return TeachingDeepAgentGraph(
        config=config,
        backend=backend,
        middleware=middleware,
    )