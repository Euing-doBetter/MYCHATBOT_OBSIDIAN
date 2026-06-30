#!/bin/bash
# MYCHATBOT 원클릭 실행 스크립트

echo "====================================="
echo "🧠 MYCHATBOT 대시보드를 시작합니다..."
echo "====================================="

# 현재 스크립트가 있는 폴더로 이동
cd "$(dirname "$0")"

# 가상환경 활성화
source /Users/mac/Documents/vscode/.venv/bin/activate

# Streamlit 챗봇 실행
streamlit run app.py
