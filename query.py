import os
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from get_vector_db import get_vector_db

# 사용할 LLM 모델을 환경 변수에서 가져옵니다. 기본값은 'mistral'입니다.
LLM_MODEL = os.getenv('LLM_MODEL', 'mistral')


# 1. 프롬프트 템플릿 생성 함수
def get_prompt():
    """질문 생성 및 답변을 위한 두 가지 프롬프트 템플릿을 반환합니다."""
    
    # 템플릿 1: MultiQueryRetriever가 사용할 프롬프트
    # 원본 질문을 받아 5개의 유사한 질문을 생성하도록 지시합니다.
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""당신은 AI 언어 모델 어시스턴트입니다. 벡터 데이터베이스에서 관련 문서를 효과적으로 검색하기 위해,
        주어진 사용자 질문의 5가지 다른 버전을 생성하는 것이 당신의 임무입니다.
        사용자 질문에 대한 다양한 관점을 생성함으로써, 거리 기반 유사도 검색의 한계를 극복하는 데 도움을 줄 수 있습니다.
        대체 질문들은 줄바꿈으로 구분하여 제공해 주세요.
        원본 질문: {question}""",
    )

    # 템플릿 2: 최종 답변 생성을 위한 프롬프트
    # 검색된 문서(context)를 기반으로만 질문(question)에 답하도록 지시합니다.
    template = """다음 컨텍스트(context)만을 기반으로 질문에 답하세요:
    
    {context}
    
    질문: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    return QUERY_PROMPT, prompt


# 2. 쿼리 처리 메인 함수
def query2(input_question):
    """사용자의 질문(input)을 받아 답변을 생성하는 전체 과정을 처리합니다."""
    if not input_question:
        return None

    # 1. LLM 초기화
    llm = ChatOllama(model=LLM_MODEL)
    
    # 2. Vector DB 인스턴스 가져오기
    db = get_vector_db()
    
    # 3. 프롬프트 템플릿 가져오기
    QUERY_PROMPT, prompt = get_prompt()
    
    # 4. MultiQueryRetriever 설정
    # LLM을 사용해 하나의 질문을 여러 개로 변환하여 문서를 검색합니다.
    retriever = MultiQueryRetriever.from_llm(
        db.as_retriever(), llm, prompt=QUERY_PROMPT
    )
    
    # 5. RAG(검색 증강 생성) 체인 구성
    # RunnablePassthrough()는 사용자의 입력을 그대로 전달하는 역할을 합니다.
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # 6. 체인 실행 및 결과 반환
    response = chain.invoke(input_question)
    return response