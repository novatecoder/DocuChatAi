import pytest
import httpx

@pytest.mark.asyncio
async def test_chat_without_upload(run_test_server):
    """
    파일 업로드 없이 채팅 API(/query)가 정상 응답하는지 테스트
    """
    server_url = run_test_server
    query_endpoint = f"{server_url}/query"
    
    # 테스트용 질문
    payload = {
        "query": "안녕하세요, 이 시스템은 무엇인가요?"
    }
    
    print(f"\n[Action] Query 요청 전송: {query_endpoint}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(query_endpoint, json=payload)
        
        # 1. 응답 코드 확인 (200 OK)
        assert response.status_code == 200, f"서버 오류: {response.text}"
        
        # 2. JSON 응답 확인
        data = response.json()
        assert "message" in data, "응답에 'message' 필드가 없습니다."
        
        print(f"[Success] 서버 응답: {data['message']}")