

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

