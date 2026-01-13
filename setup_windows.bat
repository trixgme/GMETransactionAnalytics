@echo off
chcp 65001 > nul
REM =============================================================
REM 거래 내역 분석 대시보드 - Windows 최초 설치
REM Python이 설치되어 있어야 합니다!
REM =============================================================

cd /d "%~dp0"

echo ========================================
echo   대시보드 최초 설치
echo ========================================
echo.

REM Python 확인
echo [1/4] Python 확인 중...
python --version > nul 2>&1
if errorlevel 1 (
    echo [!] Python이 설치되어 있지 않습니다.
    echo     https://www.python.org/downloads/ 에서 설치하세요.
    echo     설치 시 "Add Python to PATH" 체크 필수!
    echo.
    pause
    exit /b 1
)
echo       Python 발견
python --version

REM 가상환경 생성
echo.
echo [2/4] 가상환경 생성 중...
if exist "myenv" (
    echo       기존 가상환경 발견, 건너뜀
) else (
    python -m venv myenv
    echo       가상환경 생성 완료
)

REM 가상환경 활성화
echo.
echo [3/4] 가상환경 활성화 중...
call myenv\Scripts\activate.bat

REM 패키지 설치
echo.
echo [4/4] 필요한 패키지 설치 중...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================
echo   설치 완료!
echo.
echo   실행하려면: run_dashboard.bat
echo   더블클릭하세요!
echo ========================================
echo.
pause
