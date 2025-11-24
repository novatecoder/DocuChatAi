import pytest
import subprocess
import time
import os
import sys
import signal

# 서버 포트 및 URL 설정
SERVER_PORT = 8080
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"

@pytest.fixture(scope="session")
def run_test_server():
    """
    테스트 세션 동안 백그라운드에서 Flask 서버를 실행하는 픽스처
    """
    # 모듈 실행 방식 (src 구조 반영)
    cmd = [sys.executable, "-m", "docuchatai.main"]
    
    env = os.environ.copy()
    env["FLASK_DEBUG"] = "False"  # 테스트 시에는 디버그 모드 끔
    env["PORT"] = str(SERVER_PORT)

    print(f"\n[Test] Starting server on port {SERVER_PORT}...")
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # 서버 구동 대기 (5초)
    time.sleep(5)

    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        raise RuntimeError(f"Server failed to start:\n{stderr.decode()}")

    yield SERVER_URL

    print("\n[Test] Stopping server...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()