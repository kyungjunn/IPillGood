## 기본 라이브러리 임포트
from datetime import datetime
import json
import os
from langchain_openai import ChatOpenAI

## 추가 라이브러리
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb
from pathlib import Path

def programStart():
    print(getCurrentTimeStr(), "programStart() is started...")

    ## OpenAI LLM 및 임베딩 모델 로드
    llm = getOpenAILLM()
    # 임베딩 모델 생성
    embeddings_model = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.environ["OPENAI_API_KEY"]
    )

    ## 기존 빌드된 로컬 ChromaDB 연결
    # 데이터가 적재된 로컬 경로를 인식하여 영양제 정보 컬렉션을 호출
    BASE_DIR = Path(__file__).resolve().parent
    CHROMA_DB_DIR = str(BASE_DIR / "chroma_db")
    COLLECTION_NAME = "health_supplements"

    print(getCurrentTimeStr(), f"ChromaDB 연결 중... 경로: {CHROMA_DB_DIR}")
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(getCurrentTimeStr(), f"DB 로드 실패: {e}")
        print("주의 : 데이터가 OpenAI 임베딩 벡터로 빌드되어 있어야 정상 검색이 가능합니다.")
        return

    ## 테스트용 사용자 건강 고민 질문 설정
    user_query = "요즘 스마트폰을 많이 봐서 눈이 자주 피로하고 침침한데 영양제 추천해줘."
    print(getCurrentTimeStr(), f"유저 질문: '{user_query}'")

    ## 1. 유저 질문을 쿼리 변환
    query_vector = embeddings_model.embed_query(user_query)

    ## 2. OpenAI 벡터로 변환 및 유사도 검색
    search_results = collection.query(query_embeddings=[query_vector], n_results=3)

    ## 3. 검색 결과(문서, 메타데이터, 유사도 거리) 가공 및 랭킹 정렬
    context_chunks = []
    if search_results and 'documents' in search_results and search_results['documents'][0]:
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        distances = search_results['distances'][0] # 벡터 간의 거리

        for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
            product_name = meta.get("product_name", "알 수 없는 제품")
            # 1~3순위 구조화 데이터 빌드 (코사인 거리 명시)
            chunk_text = f"[추천 {idx}순위 제품: {product_name} (유사도 거리: {dist:.4f})]\n{doc}"
            context_chunks.append(chunk_text)

    final_context = "\n\n".join(context_chunks) if context_chunks else "관련 영양제 정보 없음"

    # LangChain 가이드라인을 따르는 전문 템플릿 정의 및 체인 구동
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 영양제 추천 전문가 AI 'I Pill Good'입니다. "
                   "제공된 [영양제 데이터 컨텍스트]를 기반으로 유저의 질문에 친절하고 정중하게 답변하세요. "
                   "절대 없는 정보를 지어내거나 가공하지 마세요(할루시네이션 방지).\n\n"
                   "[영양제 데이터 컨텍스트]\n{context}"),
        ("human", "{question}")
    ])

    ## 4. LCEL 체인 연결 (gpt-4o 전달)
    rag_chain = prompt | llm | StrOutputParser()


    print(getCurrentTimeStr(), "gpt-4o 모델 추론 시작...")
    
    ## 5. 최종 답변 생성
    answer = rag_chain.invoke({"context": final_context, "question": user_query})

    print("\n================== [I Pill Good LLM 추천 답변] ==================")
    print(answer)
    print("===============================================================\n")

    print(getCurrentTimeStr(), "programStart() is finished...")


## OpenAI LLM API 객체를 가져오기 위한 함수
def getOpenAILLM():
    # API 키 바인딩
    open_api_key = "asd"
    os.environ["OPENAI_API_KEY"] = open_api_key
    llm = ChatOpenAI(temperature=0,model_name="gpt-4o")
    return llm


## 시간 출력 함수
def getCurrentTimeStr():
    currentTimeStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return f"[{currentTimeStr}]"



if __name__ == "__main__":
    start_time = datetime.now()
    print(getCurrentTimeStr(), "main Start..")

    ## 메인 함수를 이용해서 실행할 함수
    programStart()

    finish_time = datetime.now()
    print(getCurrentTimeStr(), f"main Finish..({(finish_time - start_time).total_seconds()}s Elapsed)")