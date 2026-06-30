"""
rag.py - RAG 파이프라인 핵심 모듈
Load → Split → Embed → Store → Query
(최신 LangChain 1.x 완벽 호환)
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

import config


# ── 임베딩 모델 선택 ────────────────────────────────────────────────────────
def get_embeddings():
    if config.LLM_PROVIDER == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model=config.GEMINI_EMBED,
            google_api_key=config.GEMINI_API_KEY
        )
    elif config.LLM_PROVIDER == "ollama":
        from langchain_community.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL
        )
    else:  # openai
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            openai_api_key=config.OPENAI_API_KEY,
            model=config.EMBED_MODEL
        )


# ── LLM 선택 ────────────────────────────────────────────────────────────────
def get_llm():
    if config.LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.2,
            convert_system_message_to_human=True
        )
    elif config.LLM_PROVIDER == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL
        )
    else:  # openai
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            openai_api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            temperature=0.2
        )


# ── STEP 1: 문서 로드 ────────────────────────────────────────────────────────
def load_documents(docs_path: str) -> List[Document]:
    """마크다운(.md) 파일을 재귀적으로 모두 불러옵니다."""
    path = Path(docs_path)
    if not path.exists():
        raise FileNotFoundError(f"문서 경로를 찾을 수 없습니다: {docs_path}")

    loader = DirectoryLoader(
        str(path),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
        use_multithreading=True,
    )
    docs = loader.load()
    print(f"✅ 문서 {len(docs)}개 로드 완료 ({docs_path})")
    return docs


# ── STEP 2: 청크 분할 ────────────────────────────────────────────────────────
def split_documents(docs: List[Document]) -> List[Document]:
    """긴 문서를 AI가 처리하기 좋은 크기로 자릅니다."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ 총 {len(chunks)}개 청크로 분할 완료")
    return chunks


# ── STEP 3 & 4: 임베딩 + VectorDB 배치 저장 (Rate Limit 방어) ──────────────
def build_vectordb(chunks: List[Document]) -> Chroma:
    """청크를 배치 단위로 나누어 ChromaDB에 안전하게 저장합니다."""
    embeddings = get_embeddings()
    vectordb = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_DIR,
    )
    batch_size = 50  # 1분당 100회 한도 보호
    print(f"📦 총 {len(chunks)}개 청크를 {batch_size}개씩 나누어 DB에 저장합니다...")
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        try:
            vectordb.add_documents(batch)
            print(f"   [{min(i+batch_size, len(chunks))}/{len(chunks)}] 청크 저장 완료")
            time.sleep(2)  # API 속도 제한 방어
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("⏳ 1분 무료 요청 한도 도달! 55초 대기 후 재시도합니다...")
                time.sleep(55)
                vectordb.add_documents(batch)
                print(f"   [{min(i+batch_size, len(chunks))}/{len(chunks)}] 청크 저장 완료 (재시도 성공)")
            else:
                raise e

    print(f"✅ VectorDB 완벽 저장 완료 → {config.CHROMA_DIR}")
    return vectordb


# ── VectorDB 불러오기 ────────────────────────────────────────────────────────
def load_vectordb() -> Chroma:
    """저장된 VectorDB를 불러옵니다."""
    embeddings = get_embeddings()
    vectordb = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_DIR,
    )
    return vectordb


def is_vectordb_ready() -> bool:
    """VectorDB가 이미 구축되어 있는지 확인합니다."""
    chroma_path = Path(config.CHROMA_DIR)
    return chroma_path.exists() and any(chroma_path.iterdir())


# ── STEP 5: 직관적인 RAG 엔진 ───────────────────────────────────────────────
class RAGChatEngine:
    """어떤 LangChain 버전에서도 안정적으로 작동하는 맞춤형 RAG 엔진"""
    def __init__(self, vectordb: Chroma):
        self.retriever = vectordb.as_retriever(
            search_type="similarity",
            search_kwargs={"k": config.RETRIEVER_K}
        )
        self.llm = get_llm()

    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        question = inputs.get("question", "")
        chat_history = inputs.get("chat_history", [])

        # 1. 문서 검색
        source_docs = self.retriever.invoke(question)
        context_text = "\n\n---\n\n".join([doc.page_content for doc in source_docs])

        # 2. 최근 대화 요약 구성
        history_text = ""
        if chat_history:
            history_text = "이전 대화 내역:\n" + "\n".join([f"{role}: {msg}" for role, msg in chat_history[-4:]]) + "\n\n"

        # 3. 프롬프트 생성 및 질의
        prompt = f"""당신은 사용자의 개인 지식 관리(Obsidian 노트)를 돕는 AI 어시스턴트입니다.
아래 제공된 [참고 문서 내용]을 바탕으로 사용자의 질문에 정확하고 친절하게 답변해주세요.
참고 문서에 없는 내용은 추측하지 말고 문서에서 찾을 수 없다고 솔직하게 답변하세요.

{history_text}[참고 문서 내용]
{context_text}

[사용자 질문]
{question}

답변:"""
        response = self.llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)

        return {
            "answer": answer,
            "source_documents": source_docs
        }


def build_qa_chain(vectordb: Chroma) -> RAGChatEngine:
    return RAGChatEngine(vectordb)


def get_or_build_chain() -> RAGChatEngine:
    """VectorDB가 있으면 로드, 없으면 전체 파이프라인 실행."""
    if is_vectordb_ready():
        print("📂 기존 VectorDB 로드 중...")
        vectordb = load_vectordb()
    else:
        print("🔨 VectorDB 새로 구축 중...")
        docs   = load_documents(config.DOCS_PATH)
        chunks = split_documents(docs)
        vectordb = build_vectordb(chunks)
    return build_qa_chain(vectordb)
