
 uvicorn app.main:app --reload 

 uv run uvicorn app.main:app --reload

 执行单个文件
 uv run python -m app.scripts.test_db

python -m app.scripts.llm_openai_responses_demo
python -m app.scripts.llm_openai_compatible_chat_demo
python -m app.scripts.llm_qwen_compatible_demo
python -m app.scripts.token_usage_demo



python -m app.scripts.llm_stream_demo


uvicorn == 启动服务器

app.main = python 模块路径

:app = main.py 中的 app 实例

--reload = 自动重载代码更改



/api/v1/chat 
/api/v2/chat


api==接口层  ---  接收请求 读取参数 校验参数 调用业务逻辑层
schemas==数据模型层 ,请求和响应模型 ： 参数校验  Swagger 文档
services==业务逻辑层： 调用lLM 调用向量数据库 调用外部服务 Agent 组合 repositories 
repostories==数据访问层 : 数据库操作 缓存操作 文件系统操作 redis 
------- db  redis llm tool vector db 
modles==数据模型
core==核心配置 日志 异常 常量  安全 初始化配置
denpendencies==依赖注入 fastapi 依赖


main.py ---   api/v1/api.py -  
    chat.py   会话相关的接口
    health.py   健康检查接口
    conversations.py   会话管理接口
    rag.py   检索增强生成接口



pgsql  向量数据库 
    pgvector
milvus
qdrant
elaticsearch
向量数据库

## 项目结构

```text
app/
├── api/              接口层
├── core/             核心配置
├── schemas/          请求响应模型
├── services/         业务逻辑
├── repositories/     数据访问
├── models/           数据库模型
└── dependencies/     依赖注入


dependencies
    setting.py 配置依赖
    auth.py 认证依赖 权限  api key token
    database.py 数据库依赖
    llm.py llm 依赖

fastapi  
    1. 分析接口函数参数
    2. 发现某个参数使用了 Depends
    3. 调用 Depends 里面的依赖函数
    4. 依赖函数返回的值 作为接口函数的参数
    5. 接口函数执行



    有些接口需要管理员才能访问
    查看系统的配置，
    查看系统的健康状态
    管理模型
    成本统计

    
agent_state.py == Agent 状态管理 
lock.py == 分布式锁 
rate_limit.py == 限流 
cache.py == 缓存
keys.py == 密钥管理 (统一的key命名)
client.py == 创建redis客户端管理



# llm原理

HTTP API
API Key
model
messages
role
prompt
token
temperature
max_tokens
stream
usage
error
retry
timeout



统一 LLM Provider
Prompt Engineering
Streaming 流式输出
Structured Output
Function Calling
Tool Calling
LangChain
LangGraph
Agent

大模型ai到底是是什么？
你的后端服务--- http请求---大模型服务商api --模型推理
返回 json 文本 流  


什么是 AI Agent？
后端请求参数是什么？

{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "user",
      "content": "什么是 AI Agent？"
    }
  ]
}

发给 模型api 

返回 = answer： {
  "answer": "AI Agent 是能够理解目标、规划任务并调用工具完成目标的智能体。"
}
# 简易流程
用户输入问题
前端发送到fastapi （spring-boot nestjs）
- 后端服务（认证，限流  读取历史的会话信息的  读取用户配置的 组装message ）
fastapi 调用 组装llm request
携带api key 请求模型服务商
模型推理生成回答
返回 response stream chunk
fastapi（spring-boot nestjs） 组装 response （解析结果）
保存信息 和useage  （用户信息，ai回复， token用量 trace_id 模型信息）

返回给前端
后端服务接口非常重要（fastapi spring-boot nestjs ）
- 安全的控制， 上下文组装， 成本统计  日志追踪， 缓存 错误处理 数据持久化（库 ）

# 正式的项目里面

前端 后端技术至上 叠加你的大模型的技术！

大模型调用api
- baseURL
- endpoint
- api key
- headers
- request body
- response body
- error handling

POST https://api.deepseek.com/chat/completions
Authorization: Bearer sk-xxxx
Content-Type: application/json

参数
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "user",
      "content": "什么是 AI Agent？"
    }
  ],
  "temperature": 0.7,
  "stream": false
}

openai   deepseek  `

Chat Completions 请求结构

比较典型

{
  "model": "deepseek-chat", 
  "messages": [
    {
      "role": "system",
      "content": "你是一个专业 AI 助手。"
    },
    {
      "role": "user",
      "content": "什么是 AI Agent？"
    }
  ],
  "temperature": 0.7,  
  "max_tokens": 1000,
  "stream": false
} 

大模型的api--- 参数 

messages是什么？
[
  {
    "role": "system",   告诉模型身份 规则！
    "content": "你是一个专业 AI 助手。"
  },
  {
    "role": "user",  表示用户的输入 
    "content": "什么是 AI Agent？"
  },
  {
    "role": "assistant",  模型之前的回答
    "content": "AI Agent 是..."
  },
  {
    "role": "user",
    "content": "它和 RAG 有什么区别？"
  }
  {
    "role": "tool", 模型调用工具 
    "content": "它和 RAG 有什么区别？" 
  }
]



system prompt 
{
  "role": "system",
  "content": "你是一个专业的企业 AI 助手。回答要准确、简洁，不要编造事实。"
}


定义模型规则
ai的角色--- 回答规则，  安全边界  输入格式 业务约束 

电商客服 Agent：
你是一个跨境电商客服助手。
只能回答订单、物流、售后相关问题。
如果不知道，请引导用户转人工。
不要编造物流单号。

比如企业知识库助手：
你是企业知识库助手。
回答必须基于提供的文档片段。
如果资料中没有答案，请回答“知识库中暂未找到相关信息”。


prompt --理解成一个字符串  

请介绍一下 AI Agent

mesages
[
  {
    "role": "user",
    "content": "什么是 AI Agent？"
  }
]
prompt :
你是客服助手。
用户问题：我的订单在哪？
订单数据：已发货。

[
  {
    "role": "system",
    "content": "你是客服助手。"
  },
  {
    "role": "user",
    "content": "我的订单在哪？"
  },
  {
    "role": "tool",
    "content": "订单数据：已发货。"
  }
]

temperature 
temperature 越低：
回答越稳定、越保守、越确定

temperature 越高：
回答越发散、越随机、越有创造性
temperature= 0.2
业务场景：
 客服 
 知识库回答
 代码生成
 结构化的输出 
0.7
创意写作
营销文案
标题生成
头脑风暴

max_tokens： 1000 ---- 1000 个 token 

英文：一个单词可能是一个或多个 token
中文：一个字或一个词可能被切成一个或多个 token

为什么要限制 max_tokens
    输出长度
    响应耗时
    调用成本
    前端展示

token 和 usage


{
  "usage": {
    "prompt_tokens": 120,
    "completion_tokens": 80,
    "total_tokens": 200
  }
} 
db

response
Chat Completions 风格

{
  "id": "chatcmpl_xxx",
  "object": "chat.completion",
  "created": 1720000000,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "AI Agent 是能够理解目标、规划任务并调用工具完成目标的智能体。"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 30,
    "completion_tokens": 40,
    "total_tokens": 70
  }
}


stream

 模型边生成边返回 token/chunk


 SSE 是什么
SSE = Server-Sent Events
服务端持续向客户端发送事件
适合大模型流式输出
data: {"choices":[{"delta":{"role":"assistant","content":""}}]}
data: {"choices":[{"delta":{"content":"AI"}}]}

data: {"choices":[{"delta":{"content":" Agent"}}]}

data: {"choices":[{"delta":{"content":" 是"}}]}

data: [DONE]

full_answer = ""
async for chunk in stream:
    delta = chunk["choices"][0]["delta"]
    content = delta.get("content")

    if content:
        full_answer += content
        yield content


OpenAI-compatible API 

client.chat.completions.create(
    model="xxx",
    messages=[...],
)

api_key === 
base_url --- 
model -- 

统一请求结构
统一响应结构
统一错误处理
统一流式接口

API Key
model
messages
role
temperature
stream
usage
error

LLM Provider



httpx-- 
搞清楚：
  请求地址
  header
  请求体
  响应体
  错误处理


POST /api/v1/chat
  chat router
  chatservice
  llm provider
  openai deepseek
  llmresponse
  保存message usage
  返回chatresponse
