import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS  # CORS 추가
from werkzeug.utils import secure_filename # 파일 이름 보안

# 사용자 정의 모듈 임포트
from embed import embed2
from query import query2

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# 임시 파일을 저장할 폴더를 설정하고, 폴더가 없으면 생성합니다.
TEMP_FOLDER = os.getenv('TEMP_FOLDER', './_temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Flask 애플리케이션을 초기화합니다.
app = Flask(__name__)
CORS(app)  # CORS 설정 적용

# 허용할 파일 확장자 목록 (예시)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/embed', methods=['POST'])
def route_embed():
    """파일을 업로드받아 임베딩을 처리하는 라우트입니다."""
    if 'file' not in request.files:
        return jsonify({"error": "요청에 파일 파트가 없습니다."}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "파일이 선택되지 않았습니다."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "허용되지 않는 파일 형식입니다."}), 400

    filename = secure_filename(file.filename)

    try:
        is_success = embed2(file)
        if is_success:
            logging.info(f"파일 임베딩 성공: {filename}")
            return jsonify({"message": f"파일 '{filename}'이(가) 성공적으로 임베딩되었습니다."}), 200
        else:
            logging.warning(f"파일 임베딩 실패 (함수 반환값 False): {filename}")
            return jsonify({"error": "파일 임베딩 로직에서 실패했습니다."}), 400
    except Exception as e:
        logging.error(f"임베딩 중 예외 발생 ({filename}): {e}", exc_info=True)
        return jsonify({"error": "서버 내부 오류로 임베딩에 실패했습니다."}), 500


@app.route('/query', methods=['POST'])
def route_query():
    """JSON 형식의 쿼리를 받아 처리하고 결과를 반환하는 라우트입니다."""
    if not request.is_json:
        return jsonify({"error": "요청 형식이 JSON이 아닙니다."}), 400

    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "'query' 필드가 필요합니다."}), 400

    try:
        response = query2(user_query)

        print(user_query)
        if response:
            logging.info(f"쿼리 처리 성공: {user_query}")
            return jsonify({"message": response}), 200
        else:
            logging.warning(f"쿼리 결과 없음: {user_query}")
            return jsonify({"error": "쿼리에 대한 결과를 찾을 수 없습니다."}), 404
    except Exception as e:
        logging.error(f"쿼리 처리 중 예외 발생: {e}", exc_info=True)
        return jsonify({"error": "쿼리 처리 중 서버 내부 오류가 발생했습니다."}), 500

if __name__ == '__main__':
    # 실제 배포 시에는 debug=False 로 설정해야 합니다.
    app.run(host="0.0.0.0", port=8080, debug=True)