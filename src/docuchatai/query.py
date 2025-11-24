import os
from langchain_ollama import ChatOllama # 또는 langchain_community.chat_models
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

# [수정] 상대 경로 임포트
from .get_vector_db import get_vector_db

LLM_MODEL = os.getenv('LLM_MODEL', 'mistral')

def get_prompt():
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""당신은 AI 언어 모델 어시스턴트입니다... (생략) ... 원본 질문: {question}""",
    )
    template = """다음 컨텍스트(context)만을 기반으로 질문에 답하세요:
    {context}
    질문: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    return QUERY_PROMPT, prompt

# [수정] 함수명 변경: query2 -> generate_answer
def generate_answer(input_question):
    """사용자의 질문을 받아 답변을 생성합니다."""
    if not input_question:
        return None

    llm = ChatOllama(model=LLM_MODEL)
    db = get_vector_db()
    QUERY_PROMPT, prompt = get_prompt()
    
    retriever = MultiQueryRetriever.from_llm(
        db.as_retriever(), llm, prompt=QUERY_PROMPT
    )
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke(input_question)