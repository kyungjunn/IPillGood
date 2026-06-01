import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json

# LangChain 및 OpenAI 관련 라이브러리 임포트
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb

# API Key 등록
OPENAI_API_KEY = "asd"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

app = FastAPI(title="I Pill Good OpenAI API Server")

# 💡 프론트엔드(Vite 등)와의 통신을 위한 CORS 예외 처리
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 로컬 테스트 시 모두 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 바디 모델 정의
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

# 글로벌 모델 및 DB 객체 초기화
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DB_DIR = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "health_supplements"

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
collection = chroma_client.get_collection(name=COLLECTION_NAME)

@app.post("/api/recommend", response_model=ChatResponse)
async def recommend_supplements(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="질문 내용을 입력해주세요.")
        
    try:
        # 1. 질문 임베딩 생성 및 ChromaDB 유사도 검색
        query_vector = embeddings_model.embed_query(request.query)
        search_results = collection.query(query_embeddings=[query_vector], n_results=3)
        
        # 2. 검색 결과 파싱 및 컨텍스트 매칭 (랭킹화)
        context_chunks = []
        if search_results and 'documents' in search_results and search_results['documents'][0]:
            documents = search_results['documents'][0]
            metadatas = search_results['metadatas'][0]
            distances = search_results['distances'][0]
            
            for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
                product_name = meta.get("product_name", "알 수 없는 제품")
                chunk_text = f"[{idx}순위 제품: {product_name} (유사도: {dist:.4f})]\n{doc}"
                context_chunks.append(chunk_text)
        
        final_context = "\n\n".join(context_chunks) if context_chunks else "관련 영양제 정보 없음"
        
        # 3. 프롬프트 템플릿 결합
        prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 영양제 추천 전문가 AI 'I Pill Good'입니다. "
                       "제공된 [영양제 데이터 컨텍스트]를 기반으로 유저의 질문에 친절하고 정중하게 답변하세요. "
                       "절대 없는 정보를 지어내지 마세요(할루시네이션 방지).\n\n"
                       "[영양제 데이터 컨텍스트]\n{context}"),
            ("human", "{question}")
        ])
        
        # 4. 체인 실행 및 답변 반환
        rag_chain = prompt | llm | StrOutputParser()
        answer = rag_chain.invoke({"context": final_context, "question": request.query})
        
        return ChatResponse(answer=answer)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다: {str(e)}")