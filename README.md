# DocuChatAi
DocuChat AI는 Ollama와 Python을 활용한 RAG(Retrieval-Augmented Generation) 기반의 문서 질의응답 시스템

# 설치한 내용 메모
python
pip install --q unstructured langchain langchain-text-splitters 
pip install --q "unstructured[all-docs]"
pip install --q flask
pip install --q embed

ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
ollama pull nomic-embed-text
ollama serve


app 실행
python3 app.py

curl로 테스트
curl --request POST \
--url http://localhost:8080/embed \
--header 'Content-Type: multipart/form-data' \
--form file=@/home/kwh/workspace/git/DocuChatAi/Documents/test.pdf

curl --request POST --url 'http://localhost:8080/query' --header 'Content-Type: application/json' --data '{ "query": "What are the key points of the abstract?" }'

