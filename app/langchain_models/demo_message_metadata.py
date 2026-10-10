

from langchain_core.messages import HumanMessage, SystemMessage

from app.langchain_models.model_factory import LangChainModelFactory



def main():
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.7,
    )
    messages = [
        SystemMessage(content="我是一个AI助手，很高兴为你服务。"),
        HumanMessage(content="请用一句话解释什么是 response_metadata")
        
    ]
    response = model.invoke(messages)
    # response = model.invoke("请用一句话解释什么是 Langchain ChatModel")

    print('content: ',response.content)
    print("===================")
    print('response_metadata: ',response.response_metadata)
    print("===================")
    print('usage_metadata: ',response.usage_metadata)
    print("===================")


if __name__ == '__main__':
    main()


# response_metadata:  {'token_usage': {'completion_tokens': 61, 'prompt_tokens': 22, 'total_tokens': 83, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 0, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 0, 'prompt_cache_miss_tokens': 22}, 'model_provider': 'openai', 'model_name': 'deepseek-flash', 'system_fingerprint': 'aeb56401ca74e127821c4f9126dcb669', 'id': '60be0d08-8e80-4746-a7ed-97656e9e0f3d', 'finish_reason': 'stop', 'logprobs': None}
# usage_metadata:  {'input_tokens': 22, 'output_tokens': 61, 'total_tokens': 83, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}}
# (ai-fastapi-course) (base) 