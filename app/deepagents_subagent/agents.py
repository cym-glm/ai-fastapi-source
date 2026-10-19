import uuid

from app.deepagents_subagent.schemas import (
    SubAgentResult,
    SubAgentRole,
    SubAgentSpec,
    SubAgentStatus,
    SubAgentTask,
)
from app.deepagents_subagent.tools import SubAgentToolExecutor


def build_default_subagent_specs() -> list[SubAgentSpec]:
    return [
        SubAgentSpec(
            name="research-agent",
            role=SubAgentRole.RESEARCH,
            description="负责资料收集、事实抽取和研究笔记整理。",
            system_prompt=(
                "你是 Research Sub-Agent。"
                "你只负责收集资料、提取事实、整理研究笔记。"
                "不要写最终报告，不要做最终判断。"
            ),
            allowed_tools=[
                "search_web",
                "search_enterprise_kb",
            ],
            output_format="markdown",
        ),
        SubAgentSpec(
            name="analysis-agent",
            role=SubAgentRole.ANALYSIS,
            description="负责结构化分析、归因、趋势判断和风险分析。",
            system_prompt=(
                "你是 Analysis Sub-Agent。"
                "你只负责基于资料做结构化分析，输出结论、依据和风险。"
            ),
            allowed_tools=[
                "analyze_text",
            ],
            output_format="markdown",
        ),
        SubAgentSpec(
            name="writer-agent",
            role=SubAgentRole.WRITER,
            description="负责把资料和分析结论组织成结构化报告草稿。",
            system_prompt=(
                "你是 Writer Sub-Agent。"
                "你只负责写报告草稿，不负责资料搜索和最终审查。"
            ),
            allowed_tools=[
                "write_markdown_report",
            ],
            output_format="markdown",
        ),
        SubAgentSpec(
            name="reviewer-agent",
            role=SubAgentRole.REVIEWER,
            description="负责审查报告结构、事实依据、风险和遗漏点。",
            system_prompt=(
                "你是 Reviewer Sub-Agent。"
                "你只负责发现问题和提出修改建议，不要重写全文。"
            ),
            allowed_tools=[
                "review_content",
            ],
            output_format="markdown",
        ),
        SubAgentSpec(
            name="code-agent",
            role=SubAgentRole.CODE,
            description="负责代码仓库结构分析、模块分析和技术风险识别。",
            system_prompt=(
                "你是 Code Sub-Agent。"
                "你只负责代码结构分析和技术风险识别。"
            ),
            allowed_tools=[
                "inspect_code_repo",
            ],
            output_format="markdown",
        ),
        SubAgentSpec(
            name="data-agent",
            role=SubAgentRole.DATA,
            description="负责数据指标分析、异常发现和业务解释。",
            system_prompt=(
                "你是 Data Sub-Agent。"
                "你只负责指标分析和业务解释。"
            ),
            allowed_tools=[
                "analyze_data",
            ],
            output_format="markdown",
        ),
    ]


class TeachingSubAgent:
    def __init__(
        self,
        spec: SubAgentSpec,
        tool_executor: SubAgentToolExecutor,
    ):
        self.spec = spec
        self.tool_executor = tool_executor

    def run(
        self,
        task: SubAgentTask,
        write_file,
    ) -> SubAgentResult:
        try:
            if self.spec.role == SubAgentRole.RESEARCH:
                return self._run_research(task, write_file)

            if self.spec.role == SubAgentRole.ANALYSIS:
                return self._run_analysis(task, write_file)

            if self.spec.role == SubAgentRole.WRITER:
                return self._run_writer(task, write_file)

            if self.spec.role == SubAgentRole.REVIEWER:
                return self._run_reviewer(task, write_file)

            if self.spec.role == SubAgentRole.CODE:
                return self._run_code(task, write_file)

            if self.spec.role == SubAgentRole.DATA:
                return self._run_data(task, write_file)

            return self._run_general(task, write_file)

        except Exception as exc:
            return SubAgentResult(
                task_id=task.task_id,
                agent_name=self.spec.name,
                role=self.spec.role,
                status=SubAgentStatus.FAILED,
                summary="子任务执行失败。",
                output="",
                error_message=str(exc),
            )

    def _run_research(
        self,
        task: SubAgentTask,
        write_file,
    ) -> SubAgentResult:
        web_result = self.tool_executor.execute(
            tool_name="search_web",
            arguments={
                "query": task.instruction,
            },
            allowed_tools=self.spec.allowed_tools,
        )

        kb_result = self.tool_executor.execute(
            tool_name="search_enterprise_kb",
            arguments={
                "query": task.instruction,
            },
            allowed_tools=self.spec.allowed_tools,
        )

        output = f"""
# Research Notes

## 子任务

{task.instruction}

## 外部资料

{web_result}

## 企业知识库资料

{kb_result}

## 研究结论

1. Agent 平台的核心能力正在从单点 Chatbot 走向可编排平台。
2. 企业落地更关注 RAG、权限、工具调用、观测和评估。
3. Dify、Coze 更偏应用搭建；LangGraph 更偏开发者编排；CrewAI 和 AutoGen 更偏多智能体协作。
""".strip()

        output_file = f"/subagents/{task.task_id}_research.md"
        write_file(output_file, output)

        return SubAgentResult(
            task_id=task.task_id,
            agent_name=self.spec.name,
            role=self.spec.role,
            status=SubAgentStatus.SUCCESS,
            summary="已完成资料收集和研究笔记整理。",
            output=output,
            output_file=output_file,
            warnings=[
                "教学版使用模拟搜索结果，生产环境需要真实检索和来源引用。"
            ],
        )

    def _run_analysis(
        self,
        task: SubAgentTask,
        write_file,
    ) -> SubAgentResult:
        analysis = self.tool_executor.execute(
            tool_name="analyze_text",
            arguments={
                "content": task.input_context or task.instruction,
            },
            allowed_tools=self.spec.allowed_tools,
        )

        output = f"""
# Analysis Notes

## 分析任务

{task.instruction}

## 输入资料摘要

{task.input_context[:1000]}

## 分析结果

{analysis}

## 风险点

1. 平台能力容易同质化。
2. 企业落地需要处理权限、日志、成本和评估。
3. Sub-Agent 过多会增加延迟和系统复杂度。
""".strip()

        output_file = f"/subagents/{task.task_id}_analysis.md"
        write_file(output_file, output)

        return SubAgentResult(
            task_id=task.task_id,
            agent_name=self.spec.name,
            role=self.spec.role,
            status=SubAgentStatus.SUCCESS,
            summary="已完成结构化分析。",
            output=output,
            output_file=output_file,
        )

    def _run_writer(
        self,
        task: SubAgentTask,
        write_file,
    ) -> SubAgentResult:
        content = f"""
## 一、任务背景

{task.instruction}

## 二、资料和分析依据

{task.input_context}

## 三、核心结论

AI Agent 平台正在从简单问答工具，升级为具备 RAG、工具调用、工作流编排、多 Agent 协作、权限、日志、评估和部署能力的企业级智能应用平台。

## 四、落地建议

1. 先做 RAG 知识库和工具调用。
2. 再引入 LangGraph 编排复杂业务流程。
3. 对长任务引入 DeepAgents。
4. 对复杂研究、写作、代码分析任务引入 Sub-Agent 分工。
"""

        report = self.tool_executor.execute(
            tool_name="write_markdown_report",
            arguments={
                "title": "AI Agent 平台调研报告草稿",
                "content": content,
            },
            allowed_tools=self.spec.allowed_tools,
        )

        output_file = f"/subagents/{task.task_id}_draft_report.md"
        write_file(output_file, report)

        return SubAgentResult(
            task_id=task.task_id,
            agent_name=self.spec.name,
            role=self.spec.role,
            status=SubAgentStatus.SUCCESS,
            summary="已生成报告草稿。",
            output=report,
            output_file=output_file,
        )

    def _run_reviewer(
        self,
        task: SubAgentTask,
        write_file,
    ) -> SubAgentResult:
        review = self.tool_executor.execute(
            tool_name="review_content",
            arguments={
                "content": task.input_context,
            },
            allowed_tools=self.spec.allowed_tools,
        )

        output = f"""
# Review Notes

## 审查任务

{task.instruction}

## 审查结果

{review}

## 修改建议

1. 补充来源说明。
2. 补充企业落地风险。
3. 补充 Sub-Agent 使用边界。
4. 避免把简单工具调用过度拆成 Sub-Agent。
""".strip()

        output_file = f"/subagents/{task.task_id}_review.md"
        write_file(output_file, output)

        return SubAgentResult(
            task_id=task.task_id,
            agent_name=self.spec.name,
            role=self.spec.role,
            status=SubAgentStatus.SUCCESS,
            summary="已完成报告审查。",
            output=output,
            output_file=output_file,
        )

    def _run_code(
        self,
        task: SubAgentTask,
        write_file,
    ) -> SubAgentResult:
        result = self.tool_executor.execute(
            tool_name="inspect_code_repo",
            arguments={
                "query": task.instruction,
            },
            allowed_tools=self.spec.allowed_tools,
        )

        output = f"""
# Code Analysis Notes

{result}

## 建议

1. 先梳理项目入口。
2. 再看 Agent graph / tools / state / memory。
3. 最后检查权限、日志和异常处理。
""".strip()

        output_file = f"/subagents/{task.task_id}_code_analysis.md"
        write_file(output_file, output)

        return SubAgentResult(
            task_id=task.task_id,
            agent_name=self.spec.name,
            role=self.spec.role,
            status=SubAgentStatus.SUCCESS,
            summary="已完成代码分析。",
            output=output,
            output_file=output_file,
        )

    def _run_data(
        self,
        task: SubAgentTask,
        write_file,
    ) -> SubAgentResult:
        result = self.tool_executor.execute(
            tool_name="analyze_data",
            arguments={
                "query": task.instruction,
            },
            allowed_tools=self.spec.allowed_tools,
        )

        output = f"""
# Data Analysis Notes

{result}

## 建议

1. 补充指标定义。
2. 补充趋势图。
3. 补充异常原因解释。
""".strip()

        output_file = f"/subagents/{task.task_id}_data_analysis.md"
        write_file(output_file, output)

        return SubAgentResult(
            task_id=task.task_id,
            agent_name=self.spec.name,
            role=self.spec.role,
            status=SubAgentStatus.SUCCESS,
            summary="已完成数据分析。",
            output=output,
            output_file=output_file,
        )

    def _run_general(
        self,
        task: SubAgentTask,
        write_file,
    ) -> SubAgentResult:
        output = f"通用子任务已完成：{task.instruction}"

        output_file = f"/subagents/{task.task_id}_general.md"
        write_file(output_file, output)

        return SubAgentResult(
            task_id=task.task_id,
            agent_name=self.spec.name,
            role=self.spec.role,
            status=SubAgentStatus.SUCCESS,
            summary="已完成通用子任务。",
            output=output,
            output_file=output_file,
        )


class SubAgentRegistry:
    def __init__(
        self,
        specs: list[SubAgentSpec],
        tool_executor: SubAgentToolExecutor,
    ):
        self.specs = {
            spec.name: spec
            for spec in specs
        }
        self.agents = {
            spec.name: TeachingSubAgent(
                spec=spec,
                tool_executor=tool_executor,
            )
            for spec in specs
        }

    def list_specs(self) -> list[SubAgentSpec]:
        return list(self.specs.values())

    def get_spec(
        self,
        name: str,
    ) -> SubAgentSpec | None:
        return self.specs.get(name)

    def run(
        self,
        agent_name: str,
        instruction: str,
        input_context: str,
        expected_output: str,
        write_file,
    ) -> SubAgentResult:
        agent = self.agents.get(agent_name)

        if not agent:
            raise ValueError(
                f"Sub-Agent 不存在：{agent_name}"
            )

        task = SubAgentTask(
            task_id=f"subtask_{uuid.uuid4().hex[:10]}",
            agent_name=agent_name,
            instruction=instruction,
            input_context=input_context,
            expected_output=expected_output,
        )

        return agent.run(
            task=task,
            write_file=write_file,
        )