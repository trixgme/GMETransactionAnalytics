@echo off
chcp 65001 > nul
REM =============================================================
REM 거래 내역 분석 대시보드 - Windows 실행 파일
REM 더블클릭으로 실행하세요!
REM =============================================================

cd /d "%~dp0"

echo ========================================
echo   거래 내역 분석 대시보드 시작
echo ========================================
echo.

REM 가상환경 확인 및 활성화
if exist "myenv\Scripts\activate.bat" (
    echo [1/3] 가상환경 활성화 중...
    call myenv\Scripts\activate.bat
) else (
    echo [!] 가상환경이 없습니다. 설치 스크립트를 먼저 실행하세요.
    echo     실행: setup_windows.bat
    echo.
    pause
    exit /b 1
)

REM 패키지 확인
echo [2/3] 패키지 확인 중...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [!] 필요한 패키지가 없습니다. 설치 중...
    pip install -r requirements.txt
)

REM Streamlit 실행
echo [3/3] 대시보드 실행 중...
echo.
echo ========================================
echo   브라우저에서 자동으로 열립니다
echo   주소: http://localhost:8501
echo.
echo   종료하려면 이 창을 닫거나
echo   Ctrl+C를 누르세요
echo ========================================
echo.

streamlit run app.py --server.headless=false
