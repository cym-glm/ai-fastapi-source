
from langchain_core.messages import HumanMessage, SystemMessage

from app.langchain_models.model_factory import LangChainModelFactory




def main():
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.7,
    )
    questions = [
        "什么是 LangChain？",
        "什么是 LangGraph？",
        "什么是 RAG？",
        
    ]
    responses = model.batch(questions)
    # response = model.invoke("请用一句话解释什么是 Langchain ChatModel")

    for  question, response in zip(questions, responses):
        print('question: ', question)
        print('response: ', response.content)
        print('===========')

if __name__ == "__main__":
    main()

