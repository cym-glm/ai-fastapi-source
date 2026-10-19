import uuid

from app.deepagents_intro.schemas import (
    AgentTask,
    ToolResult,
    TodoItem,
    TodoStatus,
    SubAgentResult,
    DeepAgentRunResult
)


from app.deepagents_intro.tools import (
    MockAnalysisTool,
    MockResearchTool,
)

from app.deepagents_intro.workspace import SimpleWorkspace


class ResearchSubAgent:
    def __init__(self):
        self.search_tool = MockResearchTool()

    def run(
        self,
        task: str,
    ) -> SubAgentResult:
        result = self.search_tool.search(task)

        return SubAgentResult(
            agent_name="ResearchSubAgent",
            task=task,
            result=result.output,
        )



class AnalysisSubAgent:
    def __init__(self):
        self.analysis_tool = MockAnalysisTool()

    def run(
        self,
        task: str,
        content: str,
    ) -> SubAgentResult:
        result = self.analysis_tool.analyze(content)

        return SubAgentResult(
            agent_name="AnalysisSubAgent",
            task=task,
            result=result.output,
        )

class WriterSubAgent:
    def run(
        self,
        task: str,
        research_notes: str,
        analysis_notes: str,
    ) -> SubAgentResult:
        report = f"""
            # AI Agent 平台调研报告
            ## 一、调研目标
            {task}
            ## 二、资料整理
            {research_notes}
            ## 三、分析结论
            {analysis_notes}
            ## 四、总结
            AI Agent 平台正在从简单问答工具，演进为集成 RAG、工具调用、工作流编排、多 Agent 协作、权限控制、日志观测和评估体系的企业级智能应用平台。
            """
        return SubAgentResult(
            agent_name="WriterSubAgent",
            task=task,
            result=report.strip(),
        )


class TeachingDeepAgent:
    """
    教学版 DeepAgent。
    模拟 DeepAgents 的几个核心思想：
    1. Planning
    2. Todo
    3. Workspace
    4. Sub-Agent
    5. Review
    6. Final Answer
    """

    def __init__(
        self,
        workspace_dir: str = "data/deep_agent_workspace",
    ):
        self.workspace = SimpleWorkspace(workspace_dir)
        self.research_agent = ResearchSubAgent()
        self.analysis_agent = AnalysisSubAgent()
        self.writer_agent = WriterSubAgent()

    def create_task(
        self,
        user_request: str,
    ) -> AgentTask:
        return AgentTask(
            task_id=f"deep_task_{uuid.uuid4().hex[:12]}",
            goal="完成复杂调研任务，并输出结构化报告。",
            user_request=user_request,
            workspace_dir=str(self.workspace.root_dir),
        )

    def plan(
        self,
        task: AgentTask,
    ) -> list[TodoItem]:
        return [
            TodoItem(
                todo_id="todo_001",
                title="明确用户调研目标",
            ),
            TodoItem(
                todo_id="todo_002",
                title="收集 AI Agent 平台竞品资料",
            ),
            TodoItem(
                todo_id="todo_003",
                title="分析竞品能力和趋势",
            ),
            TodoItem(
                todo_id="todo_004",
                title="生成调研报告初稿",
            ),
            TodoItem(
                todo_id="todo_005",
                title="检查报告结构和遗漏点",
            ),
            TodoItem(
                todo_id="todo_006",
                title="输出最终报告",
            ),
        ]

    def run(
        self,
        user_request: str,
    ) -> DeepAgentRunResult:
        trace: list[str] = []

        task = self.create_task(user_request)
        trace.append(f"创建任务：{task.task_id}")

        task.todos = self.plan(task)
        trace.append("生成 Todo List")

        self.workspace.write_file(
            "todos.md",
            self._format_todos(task.todos),
        )
        trace.append("写入 todos.md")

        self._mark_doing(task.todos, "todo_001")
        self.workspace.write_file(
            "task_goal.md",
            f"# 任务目标\n\n{task.user_request}",
        )
        self._mark_done(
            task.todos,
            "todo_001",
            "已明确用户目标。",
        )
        trace.append("完成目标确认")

        self._mark_doing(task.todos, "todo_002")
        research_result = self.research_agent.run(
            "AI Agent 平台 竞品 调研"
        )
        self.workspace.write_file(
            "research_notes.md",
            research_result.result,
        )
        self._mark_done(
            task.todos,
            "todo_002",
            "已完成竞品资料收集。",
        )
        trace.append("ResearchSubAgent 完成资料收集")

        self._mark_doing(task.todos, "todo_003")
        analysis_result = self.analysis_agent.run(
            task="分析 AI Agent 平台趋势",
            content=research_result.result,
        )
        self.workspace.write_file(
            "analysis_notes.md",
            analysis_result.result,
        )
        self._mark_done(
            task.todos,
            "todo_003",
            "已完成趋势分析。",
        )
        trace.append("AnalysisSubAgent 完成分析")

        self._mark_doing(task.todos, "todo_004")
        writer_result = self.writer_agent.run(
            task=task.user_request,
            research_notes=research_result.result,
            analysis_notes=analysis_result.result,
        )
        self.workspace.write_file(
            "draft_report.md",
            writer_result.result,
        )
        self._mark_done(
            task.todos,
            "todo_004",
            "已生成报告初稿。",
        )
        trace.append("WriterSubAgent 完成报告初稿")


        self._mark_doing(task.todos, "todo_005")
        review_notes = self._review_report(
            writer_result.result
        )
        self.workspace.write_file(
            "review_notes.md",
            review_notes,
        )
        self._mark_done(
            task.todos,
            "todo_005",
            "已完成报告检查。",
        )
        trace.append("完成报告检查")

        self._mark_doing(task.todos, "todo_006")
        final_report = writer_result.result + "\n\n## 五、自检结果\n\n" + review_notes
        self.workspace.write_file(
            "final_report.md",
            final_report,
        )
        self._mark_done(
            task.todos,
            "todo_006",
            "已输出最终报告。",
        )
        trace.append("输出 final_report.md")

        self.workspace.write_file(
            "todos.md",
            self._format_todos(task.todos),
        )

        return DeepAgentRunResult(
            task_id=task.task_id,
            goal=task.goal,
            todos=task.todos,
            workspace_files=self.workspace.list_files(),
            final_answer=final_report,
            trace=trace,
        )

    def _mark_doing(
        self,
        todos: list[TodoItem],
        todo_id: str,
    ) -> None:
        for todo in todos:
            if todo.todo_id == todo_id:
                todo.status = TodoStatus.DOING
                return

    def _mark_done(
        self,
        todos: list[TodoItem],
        todo_id: str,
        result: str,
    ) -> None:
        for todo in todos:
            if todo.todo_id == todo_id:
                todo.status = TodoStatus.DONE
                todo.result = result
                return

    def _format_todos(
        self,
        todos: list[TodoItem],
    ) -> str:
        lines = ["# Todo List", ""]

        for todo in todos:
            lines.append(
                f"- [{todo.status.value}] {todo.todo_id}：{todo.title}"
            )

            if todo.result:
                lines.append(
                    f"  - 结果：{todo.result}"
                )

        return "\n".join(lines)

    def _review_report(
        self,
        report: str,
    ) -> str:
        checks = []

        if "# AI Agent 平台调研报告" in report:
            checks.append("报告标题完整。")
        else:
            checks.append("缺少报告标题。")

        if "竞品" in report or "Dify" in report or "Coze" in report:
            checks.append("包含竞品分析内容。")
        else:
            checks.append("竞品分析内容不足。")

        if "趋势" in report or "总结" in report:
            checks.append("包含趋势总结。")
        else:
            checks.append("缺少趋势总结。")

        return "\n".join(
            f"- {item}"
            for item in checks
        )



# 创建任务：task_001
# 生成 todo 
# 写入 workspace  todos.md
# 调用 ReseachSubAgent 完成目标确认
# 调用 AnaylsisSubAgent 完成竞品分析
# 调用 WriterSubAgent 完成报告初稿
# 调用 ReviewSubAgent 完成报告检查
# 输出 final_report.md