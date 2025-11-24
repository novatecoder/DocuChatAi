import os
from typing import Optional

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores.chroma import Chroma

# --- 설정 (Constants) ---
# 환경 변수 또는 기본값을 사용하여 설정을 정의합니다.
CHROMA_PATH = os.getenv('CHROMA_PATH', 'chroma')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'local-rag')
TEXT_EMBEDDING_MODEL = os.getenv('TEXT_EMBEDDING_MODEL', 'nomic-embed-text')

# --- DB 인스턴스 초기화 (싱글턴) ---
# 이 변수는 모듈이 처음 임포트될 때 단 한 번만 초기화됩니다.
db_instance: Optional[Chroma] = None

try:
    # 1. 임베딩 함수 정의
    embedding_function = OllamaEmbeddings(
        model=TEXT_EMBEDDING_MODEL,
        show_progress=True  # 진행 상황 표시
    )

    # 2. Chroma DB 클라이언트 생성 및 인스턴스 할당
    # 이 인스턴스는 애플리케이션 전체에서 재사용됩니다.
    db_instance = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function
    )
    print("✅ Chroma DB 인스턴스가 성공적으로 생성되었습니다.")

except Exception as e:
    print(f"❌ Chroma DB 초기화 중 오류가 발생했습니다: {e}")
    db_instance = None

# --- DB 인스턴스 접근 함수 ---

def get_vector_db() -> Chroma:
    """
    미리 생성된 Chroma DB의 싱글턴 인스턴스를 반환합니다.

    Returns:
        Chroma: 초기화된 Chroma DB 클라이언트 인스턴스.

    Raises:
        ConnectionError: DB 인스턴스 초기화에 실패했을 경우 발생하는 예외.
    """
    if db_instance is None:
        raise ConnectionError("Vector DB가 초기화되지 않았습니다. 시작 로그를 확인하세요.")
    
    return db_instance

# --- 사용 예시 ---
if __name__ == '__main__':
    print("\n--- DB 연결 테스트 ---")
    try:
        # 함수를 여러 번 호출해도 실제 DB 객체는 한 번만 생성됩니다.
        db1 = get_vector_db()
        print(f"첫 번째 호출: DB 객체 ID = {id(db1)}")

        db2 = get_vector_db()
        print(f"두 번째 호출: DB 객체 ID = {id(db2)}")

        if id(db1) == id(db2):
            print("\n결과: 두 객체의 ID가 동일합니다. 싱글턴 패턴이 올바르게 작동합니다.")
        else:
            print("\n결과: 두 객체의 ID가 다릅니다. 싱글턴 패턴이 작동하지 않습니다.")

        # 간단한 DB 정보 확인
        print(f"현재 Collection의 아이템 개수: {db1._collection.count()}")

    except ConnectionError as e:
        print(e)