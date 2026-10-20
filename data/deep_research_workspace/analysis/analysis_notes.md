# Analysis Notes

## Findings
- AI Agent 平台的竞争点正在从模型接入转向任务编排、工具生态、企业数据集成和评估闭环。
- Deep Research Agent 适合处理资料来源多、步骤长、需要反复分析和写作的任务。
- 企业级 Agent 项目必须把 Planning、Context 管理、权限、Trace、Evaluation 放进架构设计。

## Risks
- 上下文管理不当会导致成本高、速度慢、输出不稳定。
- Sub-Agent 权限过大可能带来数据泄露或误操作风险。
- 资料来源缺少引用会降低报告可信度。
- 没有 Evaluation 会导致系统只能靠主观感觉优化。

## Opportunities
- 企业知识库 + Deep Research 可以形成内部咨询助手。
- 结合 RAG 和 Sub-Agent 可以降低长任务上下文压力。
- 通过 Query Log、Trace 和 Review 可以形成持续优化闭环。

## Recommendations
- 先从企业内部知识库和研究报告生成场景落地。
- 把 Research、Analysis、Writer、Reviewer 拆成独立 Sub-Agent。
- 长内容写入 Workspace，只把摘要和文件指针放入主上下文。
- 高风险工具必须加入人工确认和审计。