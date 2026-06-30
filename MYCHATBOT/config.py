import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM 설정 ──────────────────────────────────────────
# "gemini" (무료) / "openai" / "ollama" 선택
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# Gemini (무료 티어 제공 - 추천)
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL    = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # 무료 모델
GEMINI_EMBED    = os.getenv("GEMINI_EMBED", "models/gemini-embedding-001")

# OpenAI (유료)
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL    = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBED_MODEL     = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# Ollama 사용 시 (로컬, 보안 필요한 경우)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3")

# ── 문서 설정 ──────────────────────────────────────────
# Obsidian 볼트 경로 (없으면 docs/ 폴더 사용)
DOCS_PATH = os.getenv("DOCS_PATH", "./docs")

# 청크 설정
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# ── VectorDB 설정 ──────────────────────────────────────
CHROMA_DIR        = os.getenv("CHROMA_DIR", "./chroma_db")
COLLECTION_NAME   = os.getenv("COLLECTION_NAME", "mychatbot")

# ── 검색 설정 ──────────────────────────────────────────
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "4"))  # 참고할 문서 조각 수
