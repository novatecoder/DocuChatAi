import os
from datetime import datetime
from werkzeug.utils import secure_filename

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from get_vector_db import get_vector_db

# 임시 파일을 저장할 폴더를 지정합니다.
TEMP_FOLDER = os.getenv('TEMP_FOLDER', './_temp')


# 1. 파일 유효성 검사 함수
def allowed_file(filename):
    """업로드된 파일이 허용된 형식(PDF)인지 확인합니다."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}


# 2. 파일 저장 함수
def save_file(file):
    """업로드된 파일을 안전한 파일명으로 임시 폴더에 저장하고, 파일 경로를 반환합니다."""
    ct = datetime.now()
    ts = ct.timestamp()
    # 파일명이 중복되지 않도록 현재 시간을 파일명 앞에 추가합니다.
    filename = str(ts) + "_" + secure_filename(file.filename)
    file_path = os.path.join(TEMP_FOLDER, filename)
    file.save(file_path)
    return file_path


# 3. 데이터 로드 및 분할 함수
def load_and_split_data(file_path):
    """PDF 파일 경로를 받아 텍스트를 로드하고, 적절한 크기의 청크(chunk)로 분할합니다."""
    # UnstructuredPDFLoader를 사용해 PDF 파일의 내용을 로드합니다.
    loader = UnstructuredPDFLoader(file_path=file_path)
    data = loader.load()
    
    # RecursiveCharacterTextSplitter를 사용해 텍스트를 청크 단위로 나눕니다.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)
    return chunks


# 4. 임베딩 처리 메인 함수
def embed2(file):
    """파일을 받아 임베딩의 모든 과정을 처리합니다."""
    # 파일이 유효한지 확인합니다.
    if file.filename != '' and file and allowed_file(file.filename):
        # 1. 파일 저장
        file_path = save_file(file)
        # 2. 데이터 로드 및 분할
        chunks = load_and_split_data(file_path)
        # 3. Vector DB 인스턴스 가져오기
        db = get_vector_db()
        # 4. 분할된 텍스트 청크를 DB에 추가하고 변경사항을 저장
        db.add_documents(chunks)
        db.persist()
        # 5. 처리 완료된 임시 파일 삭제
        os.remove(file_path)
        return True # 성공 시 True 반환
        
    return False # 실패 시 False 반환