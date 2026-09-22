from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_structured_outputs.schemas import RAGAnswerResult


def build_rag_answer_chain():
    parser = PydanticOutputParser(
        pydantic_object=RAGAnswerResult,
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个企业知识库问答助手。\n"
                "\n"
                "回答规则：\n"
                "1. 只能基于提供的知识库片段回答。\n"
                "2. 如果知识库片段没有答案，is_answered 必须为 false。\n"
                "3. citations 只能包含知识库片段中出现的 document_id。\n"
                "4. 不要编造引用。\n"
                "5. 不要输出 Markdown，不要输出额外解释。\n"
                "\n"
                "{format_instructions}\n"
                "\n"
                "知识库片段：\n"
                "{retrieved_context}"
            ),
        ),
        (
            "human",
            "用户问题：{user_question}",
        ),
    ]).partial(
        format_instructions=parser.get_format_instructions()
    )

    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0,
    )

    return prompt | model | parser


def main():
    chain = build_rag_answer_chain()

    result = chain.invoke({
        "user_question": "员工年假有几天？",
        "retrieved_context": (
            "[doc_001] 员工入职满一年后，每年享有 5 天带薪年假。\n"
            "[doc_002] 年假申请需要提前 3 个工作日提交。"
        ),
    })

    print(result.model_dump())


if __name__ == "__main__":
    main()