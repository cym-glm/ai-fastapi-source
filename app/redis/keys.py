
# chat:response:hash_xxx
def chat_response_cache_key(question_hash: str) -> str:
    return f"chat:response:{question_hash}"


# rate_limit:chat:u_10001
def rate_limit_key(user_id: str, api_name: str) -> str:
    return f"rate_limit:{api_name}:{user_id}"


def api_key_cache_key(api_key_hash: str) -> str:
    return f"api_key:{api_key_hash}"

# conversation:c_10001:recent_messages
def conversation_recent_messages_key(conversation_id: str) -> str:
    return f"conversation:{conversation_id}:recent_messages"


def agent_run_state_key(run_id: str) -> str:
    return f"agent:run:{run_id}:state"

# lock:knowledge_base:kb_001
def lock_key(resource: str, resource_id: str) -> str:
    return f"lock:{resource}:{resource_id}"

# user1   data  chache 

# 业务模块：资源类型：资源id：字段