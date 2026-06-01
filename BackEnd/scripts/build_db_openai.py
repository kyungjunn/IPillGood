from datetime import datetime
import json
import os
import time
from pathlib import Path
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings
import chromadb

# API Key 세팅
OPENAI_API_KEY = "asd"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

BASE_DIR = Path(__file__).resolve().parent.parent
JSONL_PATH = BASE_DIR / "data" / "processed_data" / "rag_health_supplements_preprocessed.jsonl"
CHROMA_DB_DIR = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "health_supplements"

def getCurrentTimeStr():
    return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}]"

def load_jsonl(path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows

def build_openai_vector_db():
    print(getCurrentTimeStr(), "1. 전처리된 JSONL 데이터 로드 중...")
    rows = load_jsonl(JSONL_PATH)
    total = len(rows)
    print(getCurrentTimeStr(), f"총 {total}건의 영양제 데이터를 확인했습니다.")

    # 2. OpenAI 임베딩 모델 로드 (가장 강력한 text-embedding-3-large 설정)
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

    # 3. ChromaDB 연결 및 초기화
    print(getCurrentTimeStr(), f"2. ChromaDB 초기화 및 생성 중... 경로: {CHROMA_DB_DIR}")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    
    # 완전히 깨끗한 상태에서 새로 만들기 위해 기존 컬렉션이 있다면 삭제
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        print(getCurrentTimeStr(), "기존 구버전 컬렉션을 삭제했습니다.")
    except:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # 4. 배치 단위로 데이터 임베딩 및 적재 (유료 키라 대용량 분량도 500개씩 팍팍 넣습니다)
    batch_size = 500
    print(getCurrentTimeStr(), "3. OpenAI 임베딩 생성 및 DB 적재 시작...")
    
    for start_idx in tqdm(range(0, total, batch_size)):
        batch = rows[start_idx:start_idx + batch_size]
        
        ids = [row["id"] for row in batch]
        documents = [row["text"] for row in batch]
        
        # 메타데이터 가공 (딕셔너리/리스트 형태는 문자열로 저장해야 ChromaDB가 인식함)
        metadatas = []
        for row in batch:
            meta = row["metadata"].copy()
            if "nutrients" in meta:
                meta["nutrients"] = json.dumps(meta["nutrients"], ensure_ascii=False)
            metadatas.append(meta)
            
        try:
            # 텍스트 리스트를 한 번에 OpenAI 벡터로 변환
            vectors = embeddings_model.embed_documents(documents)
            
            # DB에 추가
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=vectors
            )
        except Exception as e:
            print(f"\n❌ 빌드 중 오류 발생: {e}")
            return

    print(getCurrentTimeStr(), "🎉 OpenAI 기반 고품질 Vector DB 구축 완료!")

if __name__ == "__main__":
    build_openai_vector_db()