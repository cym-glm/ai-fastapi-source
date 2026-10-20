

为什么普通 Agent 不够？  --- 调用工具的助理！

为什么需要 DeepAgents？
    - 拆分  写计划 调用工具 管理文件 委派任务 推进复杂的任务@

DeepAgents 到底解决什么问题？
它和 LangChain、LangGraph、Multi-Agent、RAG 是什么关系？

## 为什么普通 Agent 不够？



用户问题      订单 1001 
 ↓
LLM 判断意图   
 ↓
选择工具  --- query order
 ↓
调用工具  
 ↓
拿到结果
 ↓
生成回答

订单
天气
物流
简单客服！


帮我调研一下 2026 年国内 AI Agent 平台的发展趋势，整理竞品，分析商业模式，再写一份报告。

1. 拆分任务
2. 查资料
3. 对比竞品 
4 总结商业模式
5. 写报告--写文件
6. 修改
7. 提交 output 


普通 Agent：
LLM + Tools + Messages

DeepAgents：
LLM + Tools + Planning + Todo + Filesystem + SubAgents + Context Management + Runtime




我做过一个 Deep Research Agent 项目，主要解决复杂调研任务中资料来源多、上下文长、步骤容易遗漏、输出不可追踪的问题。系统基于 DeepAgents 思路设计，
主 Agent 负责 Planning 和 Orchestration，Research、Analysis、Writer、Reviewer 等 Sub-Agent 分别处理资料收集、结构化分析、报告写作和质量审查。中间资料通过 Workspace 文件系统保存，通过 Context Manager 做上下文预算、摘要压缩和文件指针管理
最终输出带 sources、trace 和 review notes 的研究报告。



Deep Research Agent｜Python + FastAPI + DeepAgents + RAG

项目背景：
复杂研究任务通常需要收集多来源资料、分析趋势、整理结论、撰写报告和审查结果。传统 Chatbot 容易出现步骤遗漏、上下文膨胀、来源不可追踪和输出质量不稳定的问题。因此设计并实现 Deep Research Agent，用于支持企业内部竞品调研、行业分析、技术方案研究和报告生成。

核心职责：
1. 设计 Deep Research Agent 整体架构，将任务拆分为 Planning、Research、Analysis、Writing、Review 和 Finalize 多阶段流程。
2. 实现 ResearchPlan 和 ResearchPlanStep，支持步骤状态、owner、output_file、result_summary 和 trace 记录。
3. 设计 Research、Analysis、Writer、Reviewer 等 Sub-Agent 分工体系，主 Agent 负责任务规划和结果整合，子 Agent 负责专业任务执行。
4. 接入企业知识库和外部搜索双资料源，统一建模为 ResearchSource，记录 source_type、title、url、file_path、score 和 metadata。
5. 通过 Workspace 保存 research_notes、analysis_notes、draft_report、review_notes 和 final_report，避免长内容全部进入模型上下文。
6. 设计 Context Manager 构建 Writer Context Pack，只把研究要点、分析结论、风险和来源指针传给写作阶段，降低上下文膨胀。
7. 增加 Reviewer Sub-Agent，对报告结构、核心结论、风险分析和来源完整性进行审查，并把 review notes 合并到最终报告。
8. 通过 FastAPI 暴露 /deep-research/run、files、read、clear 等接口，支持前端触发研究任务、查看中间文件和最终报告。