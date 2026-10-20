# Research Notes

研究主题：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。

## 关键发现
- AI Agent 平台正在从单点 Chatbot 走向企业级可编排平台。
- Deep Research 类任务需要 Planning、Sub-Agent、Workspace 和 Context 管理。
- 企业落地重点不是模型本身，而是权限、数据、工具、安全、评估和可观测性。
- RAG 可以为 DeepAgent 提供企业内部知识，Sub-Agent 可以隔离复杂研究上下文。

## Sources

### AI Agent 平台趋势
- type：web
- score：0.9
- url：https://example.com/0
- file_path：

查询：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。
AI Agent 平台正在从单点 Chatbot 走向可编排、可观测、可评估的企业级 Agent 平台。

### Deep Research 场景
- type：web
- score：0.85
- url：https://example.com/1
- file_path：

查询：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。
Deep Research 类任务通常需要规划、资料检索、分析、写作、审查和来源追踪。

### 多 Agent 协作
- type：web
- score：0.8
- url：https://example.com/2
- file_path：

查询：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。
复杂任务可以通过 Research、Analysis、Writer、Reviewer 等 Sub-Agent 分工完成。

### 企业落地风险
- type：web
- score：0.75
- url：https://example.com/3
- file_path：

查询：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。
企业落地 AI Agent 需要关注权限、数据安全、成本、可观测性、评估和人工确认。

### RAG 与 Agent 结合
- type：web
- score：0.7
- url：https://example.com/4
- file_path：

查询：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。
RAG 可以为 Agent 提供企业内部知识来源，Agent 则负责围绕目标进行规划和执行。

### 企业知识库 RAG 架构
- type：enterprise_kb
- score：0.95
- url：
- file_path：/kb/0.md

查询：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。
企业知识库包含文档解析、Chunk、Embedding、Vector Store、高级 Retrieval 和 Evaluation。

### DeepAgents 内部规范
- type：enterprise_kb
- score：0.9099999999999999
- url：
- file_path：/kb/1.md

查询：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。
复杂任务应先 Planning，再通过 Sub-Agent 分工，长内容写入 Workspace。

### Agent 安全规范
- type：enterprise_kb
- score：0.87
- url：
- file_path：/kb/2.md

查询：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。
高风险工具调用需要权限校验、Human-in-the-loop、日志审计和 Trace 记录。

### Context 管理规范
- type：enterprise_kb
- score：0.83
- url：
- file_path：/kb/3.md

查询：调研 2026 年企业级 AI Agent 平台的发展趋势，重点分析产品能力、技术架构、目标用户、商业模式和落地风险。
messages 只放当前必要信息，长工具结果和 Sub-Agent 原始输出应写入 workspace。