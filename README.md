
 uvicorn app.main:app --reload 

 uv run uvicorn app.main:app --reload

 执行单个文件
 uv run python -m app.scripts.test_db


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