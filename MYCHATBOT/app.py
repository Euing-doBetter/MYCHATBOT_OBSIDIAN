"""
app.py - MYCHATBOT Streamlit UI
실행: streamlit run app.py
"""

import streamlit as st
from pathlib import Path
import shutil

from rag import (
    get_or_build_chain,
    load_documents,
    split_documents,
    build_vectordb,
    load_vectordb,
    build_qa_chain,
    is_vectordb_ready,
)
import config

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MYCHATBOT",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 커스텀 CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0f0f13; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }

    .source-card {
        background: #1a1a2e;
        border: 1px solid #2d2d4e;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 4px 0;
        font-size: 12px;
        color: #a0a0c0;
    }
    .source-card strong { color: #7c7cf8; }

    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-ready   { background: #1a3d2e; color: #4ade80; }
    .badge-missing { background: #3d1a1a; color: #f87171; }
</style>
""", unsafe_allow_html=True)


# ── 세션 초기화 ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []   # (role, content, sources) 리스트
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None


# ── 사이드바 ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 MYCHATBOT")
    st.markdown("Obsidian + RAG 기반 개인 지식 챗봇")
    st.divider()

    # VectorDB 상태
    db_ready = is_vectordb_ready()
    badge = '<span class="status-badge badge-ready">● DB 준비됨</span>' if db_ready \
            else '<span class="status-badge badge-missing">● DB 없음</span>'
    st.markdown(f"**VectorDB 상태:** {badge}", unsafe_allow_html=True)

    st.divider()

    # 문서 경로 설정
    st.markdown("### ⚙️ 설정")
    docs_path = st.text_input(
        "📁 문서 폴더 경로",
        value=config.DOCS_PATH,
        help="Obsidian 볼트 경로 또는 마크다운 파일이 있는 폴더"
    )
    provider = st.selectbox(
        "🤖 LLM 제공자",
        ["gemini"],
        index=0 if config.LLM_PROVIDER == "gemini" else (1 if config.LLM_PROVIDER == "openai" else 2),
        help="무료는 gemini, 보안이 중요하면 ollama(로컬)을 선택하세요"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔨 DB 구축", use_container_width=True, type="primary"):
            with st.spinner("문서를 불러오고 벡터화 중..."):
                try:
                    config.DOCS_PATH    = docs_path
                    config.LLM_PROVIDER = provider
                    docs   = load_documents(docs_path)
                    chunks = split_documents(docs)
                    vdb    = build_vectordb(chunks)
                    st.session_state.qa_chain = build_qa_chain(vdb)
                    st.success(f"{len(docs)}개 문서 완료!")
                    st.rerun()
                except Exception as e:
                    st.error(f"오류: {e}")

    with col2:
        if st.button("🗑️ DB 초기화", use_container_width=True):
            if Path(config.CHROMA_DIR).exists():
                shutil.rmtree(config.CHROMA_DIR)
            st.session_state.qa_chain = None
            st.session_state.chat_history = []
            st.success("초기화 완료")
            st.rerun()

    st.divider()

    # 대화 초기화
    if st.button("💬 대화 초기화", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.qa_chain = None
        st.rerun()

    st.divider()
    st.markdown("""
    **사용 방법**
    1. 문서 폴더 경로 입력
    2. `DB 구축` 클릭 (최초 1회)
    3. 질문 입력!

    > 💡 DB는 한번 구축하면 재사용됩니다
    """)


# ── 메인 영역 ────────────────────────────────────────────────────────────────
st.title("🧠 MYCHATBOT")
st.caption("내 문서를 기반으로 대답하는 개인 AI 어시스턴트")

# DB가 있는데 체인이 없으면 자동 로드
if db_ready and st.session_state.qa_chain is None:
    with st.spinner("VectorDB 로드 중..."):
        try:
            vdb = load_vectordb()
            st.session_state.qa_chain = build_qa_chain(vdb)
        except Exception as e:
            st.error(f"VectorDB 로드 실패: {e}")

# DB 없을 때 안내
if not db_ready:
    st.info("👈 사이드바에서 문서 경로를 입력하고 **DB 구축** 버튼을 눌러 시작하세요.")
    st.markdown("""
    #### 빠른 시작
    ```bash
    # 1. 패키지 설치
    pip install -r requirements.txt

    # 2. .env 파일 설정 (OpenAI 키 입력)
    cp .env.example .env

    # 3. 문서 폴더에 .md 파일 넣기
    mkdir docs && echo "# 테스트\\n이것은 테스트 문서입니다." > docs/test.md

    # 4. 사이드바에서 DB 구축 후 질문!
    ```
    """)

# 채팅 기록 출력
for role, content, sources in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)
        if sources and role == "assistant":
            with st.expander(f"📎 참고 문서 ({len(sources)}개)", expanded=False):
                for doc in sources:
                    src = doc.metadata.get("source", "알 수 없음")
                    filename = Path(src).name
                    preview = doc.page_content[:200].replace("\n", " ")
                    st.markdown(f"""
                    <div class="source-card">
                        <strong>📄 {filename}</strong><br>
                        {preview}...
                    </div>
                    """, unsafe_allow_html=True)

# 입력창
if prompt := st.chat_input("문서에 대해 무엇이든 질문하세요...", disabled=(st.session_state.qa_chain is None)):
    # 유저 메시지 표시
    st.session_state.chat_history.append(("user", prompt, []))
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            try:
                history_pairs = [(r, c) for r, c, _ in st.session_state.chat_history]
                result  = st.session_state.qa_chain({"question": prompt, "chat_history": history_pairs})
                answer  = result.get("answer", "")
                sources = result.get("source_documents", [])

                st.markdown(answer)

                if sources:
                    with st.expander(f"📎 참고 문서 ({len(sources)}개)", expanded=False):
                        for doc in sources:
                            src      = doc.metadata.get("source", "알 수 없음")
                            filename = Path(src).name
                            preview  = doc.page_content[:200].replace("\n", " ")
                            st.markdown(f"""
                            <div class="source-card">
                                <strong>📄 {filename}</strong><br>
                                {preview}...
                            </div>
                            """, unsafe_allow_html=True)

                st.session_state.chat_history.append(("assistant", answer, sources))

            except Exception as e:
                err_msg = f"오류가 발생했습니다: {e}"
                st.error(err_msg)
                st.session_state.chat_history.append(("assistant", err_msg, []))
