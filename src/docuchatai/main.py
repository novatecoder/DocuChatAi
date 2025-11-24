import os
import logging
from .server import app

def main():
    """서버를 실행하는 엔트리포인트"""
    # 환경 변수에서 설정 가져오기 (기본값 설정)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    print(f"🚀 DocuChatAi Server running on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()