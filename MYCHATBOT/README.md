# 🧠 MYCHATBOT

Obsidian(마크다운) 문서를 기반으로 대화하는 개인 RAG 챗봇입니다.

## 프로젝트 구조

```
MYCHATBOT/
├── app.py          ← Streamlit 챗봇 UI (메인)
├── rag.py          ← RAG 파이프라인 핵심 로직
├── ingest.py       ← 문서 → VectorDB 저장 CLI
├── config.py       ← 설정값
├── .env.example    ← 환경변수 템플릿
├── requirements.txt
└── docs/           ← 마크다운 문서 보관 폴더 (기본)
```

## 빠른 시작

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 OPENAI_API_KEY 입력
```

### 3. 문서 준비
```bash
# Obsidian 볼트 경로를 .env의 DOCS_PATH에 지정하거나
# docs/ 폴더에 .md 파일을 넣으세요
mkdir docs
```

### 4. 실행

#### 방법 A: Streamlit UI (추천)
```bash
streamlit run app.py
```
→ 브라우저에서 사이드바 > DB 구축 클릭 후 바로 사용

#### 방법 B: CLI로 먼저 DB 구축 후 UI 실행
```bash
python ingest.py --path /your/obsidian/vault
streamlit run app.py
```

## 보안 모드 (Ollama 사용)

회사 내부 문서나 기밀이 포함된 경우:

```bash
# 1. Ollama 설치: https://ollama.ai
# 2. 모델 다운로드
ollama pull llama3

# 3. .env 수정
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3
```
모든 처리가 로컬에서만 이루어집니다.

## DB 초기화
```bash
python ingest.py --reset --path /your/obsidian/vault
```
