"""
ingest.py - 문서를 VectorDB에 저장하는 전용 스크립트
새 문서를 추가하거나 DB를 초기화할 때 실행합니다.

사용법:
    python ingest.py                  # 기본 경로(./docs)에서 인제스트
    python ingest.py --path /your/obsidian/vault
    python ingest.py --reset          # DB 초기화 후 재구축
"""

import argparse
import shutil
from pathlib import Path

from rag import load_documents, split_documents, build_vectordb
import config


def main():
    parser = argparse.ArgumentParser(description="문서를 VectorDB에 저장합니다.")
    parser.add_argument("--path",  type=str, default=config.DOCS_PATH, help="문서 폴더 경로")
    parser.add_argument("--reset", action="store_true", help="기존 VectorDB를 삭제하고 재구축")
    args = parser.parse_args()

    if args.reset:
        chroma_path = Path(config.CHROMA_DIR)
        if chroma_path.exists():
            shutil.rmtree(chroma_path)
            print(f"🗑️  기존 VectorDB 삭제 완료: {config.CHROMA_DIR}")

    print(f"\n📂 문서 경로: {args.path}")
    print(f"📦 VectorDB 경로: {config.CHROMA_DIR}")
    print(f"🤖 LLM 제공자: {config.LLM_PROVIDER}\n")

    docs   = load_documents(args.path)
    if not docs:
        print("❌ 문서를 찾지 못했습니다. 경로와 .md 파일 여부를 확인하세요.")
        return

    chunks = split_documents(docs)
    build_vectordb(chunks)

    print(f"\n✅ 완료! {len(docs)}개 문서, {len(chunks)}개 청크가 VectorDB에 저장되었습니다.")
    print("이제 `streamlit run app.py`로 챗봇을 실행하세요.")


if __name__ == "__main__":
    main()
