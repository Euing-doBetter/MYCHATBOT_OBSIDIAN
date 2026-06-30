# MYCHATBOT 원클릭 실행 스크립트 (PowerShell 전용)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🧠 MYCHATBOT 대시보드를 시작합니다..." -ForegroundColor Cyan
Write-Host "====================================="

Set-Location -Path $PSScriptRoot
& /Users/mac/Documents/vscode/.venv/bin/streamlit run app.py
