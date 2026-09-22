python -m app.langchain_demo.01_basic_chat_model


python -m app.langchain_arch.01_package_check.py

chatModel
promptTemplate
outputparser
tool
runnaable
Agent
Retriever



messages
role
token usage
tool_calls
stream
agent
rag

langchain--- 



from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="deepseek-chat",  # 换成你想要的模型
    api_key="xxx",  #  换成你的 DeepSeek API Key
    base_url="https://api.deepseek.com",  #  换成你的 DeepSeek API 地址


)

OpenAI
DeepSeek
Qwen
Kimi
Claude
Gemini
Ollama
智谱
火山






LangChain 1.x 生态

langchain-core
  ↓
核心抽象：Message / Prompt / Runnable / OutputParser / Tool

langchain
  ↓
主入口：Agent、常用高级能力

langchain-openai
  ↓
OpenAI / OpenAI-compatible 模型集成

langchain-community
  ↓
社区集成：第三方工具、向量库、文档加载器等

langgraph
  ↓
复杂 Agent 状态图、持久化、多步骤、人类介入


核心抽象归 core
模型集成归 provider 包
社区生态归 community
复杂 Agent 编排归 LangGraph



python -m app.langchain_arch.01_package_check.py

python -m app.langchain_models.demo_messages_basic


python -m app.langchain_models.demo_chat_model_invoke

python -m app.scripts.test_lc22_message_adapter

python -m app.langchain_prompts.demo_chat_prompt_template

python -m app.langchain_tools.demo_ 

##  18章 工具
  用户问题
  ↓
  后端发送 messages + tools 给模型
  ↓
  模型判断需要调用 query_order
  ↓
  模型返回 tool_calls
  ↓
  后端解析 tool_calls
  ↓
  后端校验 arguments
  ↓
  后端执行 query_order
  ↓
  工具返回真实结果
  ↓
  后端把 tool result 追加到 messages
  ↓
  再次调用模型
  ↓
  模型生成最终回复