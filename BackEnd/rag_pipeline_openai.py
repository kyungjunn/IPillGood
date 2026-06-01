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

##############################################################################
## 실행 함수
def programStart():
    print(getCurrentTimeStr(), "programStart() is started...")
    ############################################################################
    ## 1. OpenAI LLM 및 임베딩 모델 로드
    llm = getOpenAILLM()
    # 교수님 Key를 공유하여 임베딩 모델 생성 (text-embedding-3-small 사용)
    embeddings_model = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.environ["OPENAI_API_KEY"]
    )

    ## 2. 기존 빌드된 로컬 ChromaDB 연결
    BASE_DIR = Path(__file__).resolve().parent
    CHROMA_DB_DIR = str(BASE_DIR / "chroma_db")
    COLLECTION_NAME = "health_supplements"

    print(getCurrentTimeStr(), f"ChromaDB 연결 중... 경로: {CHROMA_DB_DIR}")
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(getCurrentTimeStr(), f"❌ DB 로드 실패: {e}")
        print("💡 주의: 데이터가 OpenAI 임베딩 벡터로 빌드되어 있어야 정상 검색이 가능합니다.")
        return

    ## 3. 테스트용 사용자 건강 고민 질문 설정
    user_query = "요즘 스마트폰을 많이 봐서 눈이 자주 피로하고 침침한데 영양제 추천해줘."
    print(getCurrentTimeStr(), f"유저 질문: '{user_query}'")

    ## 4. 유저 질문을 OpenAI 벡터로 변환 및 유사도 검색
    query_vector = embeddings_model.embed_query(user_query)
    search_results = collection.query(query_embeddings=[query_vector], n_results=3)

    ## 5. 검색된 데이터 가공 및 랭킹 컨텍스트 생성
    context_chunks = []
    if search_results and 'documents' in search_results and search_results['documents'][0]:
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        distances = search_results['distances'][0]

        for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
            product_name = meta.get("product_name", "알 수 없는 제품")
            chunk_text = f"[추천 {idx}순위 제품: {product_name} (유사도 거리: {dist:.4f})]\n{doc}"
            context_chunks.append(chunk_text)

    final_context = "\n\n".join(context_chunks) if context_chunks else "관련 영양제 정보 없음"

    ## 6. LangChain 가이드라인을 따르는 전문 템플릿 정의 및 체인 구동
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 영양제 추천 전문가 AI 'I Pill Good'입니다. "
                   "제공된 [영양제 데이터 컨텍스트]를 기반으로 유저의 질문에 친절하고 정중하게 답변하세요. "
                   "절대 없는 정보를 지어내거나 가공하지 마세요(할루시네이션 방지).\n\n"
                   "[영양제 데이터 컨텍스트]\n{context}"),
        ("human", "{question}")
    ])

    # LCEL (LangChain Expression Language) 체인 연결
    rag_chain = prompt | llm | StrOutputParser()

    print(getCurrentTimeStr(), "gpt-4o 모델 추론 시작...")
    answer = rag_chain.invoke({"context": final_context, "question": user_query})

    print("\n================== [I Pill Good LLM 추천 답변] ==================")
    print(answer)
    print("===============================================================\n")

    ############################################################################
    print(getCurrentTimeStr(), "programStart() is finished...")


##############################################################################
## OpenAI LLM API 객체를 가져오기 위한 함수
def getOpenAILLM():
    # API 키 바인딩
    open_api_key = "asd"
    os.environ["OPENAI_API_KEY"] = open_api_key
    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4o"
    )
    return llm

##############################################################################
## 시간 출력을 위한 함수
def getCurrentTimeStr():
    currentTimeStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return f"[{currentTimeStr}]"

##############################################################################
## 파이선 메인 함수
if __name__ == "__main__":
    start_time = datetime.now()
    print(getCurrentTimeStr(), "main Start..")
    ##############
    ## 파이선의 메인 함수를 이용해서 실행할 함수
    programStart()
    ##############
    finish_time = datetime.now()
    print(getCurrentTimeStr(), f"main Finish..({(finish_time - start_time).total_seconds()}s Elapsed)")