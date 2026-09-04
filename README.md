
 uvicorn app.main:app --reload 


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