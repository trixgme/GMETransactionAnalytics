#!/bin/bash
# =============================================================
# 거래 내역 분석 대시보드 - Mac 최초 설치
# Python이 설치되어 있어야 합니다!
# =============================================================

cd "$(dirname "$0")"

echo "========================================"
echo "  대시보드 최초 설치"
echo "========================================"
echo ""

# Python 확인
echo "[1/4] Python 확인 중..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "      Python3 발견: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "      Python 발견: $(python --version)"
else
    echo "[!] Python이 설치되어 있지 않습니다."
    echo "    https://www.python.org/downloads/ 에서 설치하세요."
    echo ""
    read -p "엔터를 누르면 종료됩니다..."
    exit 1
fi

# 가상환경 생성
echo ""
echo "[2/4] 가상환경 생성 중..."
if [ -d "myenv" ]; then
    echo "      기존 가상환경 발견, 건너뜀"
else
    $PYTHON_CMD -m venv myenv
    echo "      가상환경 생성 완료"
fi

# 가상환경 활성화
echo ""
echo "[3/4] 가상환경 활성화 중..."
source myenv/bin/activate

# 패키지 설치
echo ""
echo "[4/4] 필요한 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================"
echo "  설치 완료!"
echo ""
echo "  실행하려면: run_dashboard.command"
echo "  더블클릭하세요!"
echo "========================================"
echo ""
read -p "엔터를 누르면 종료됩니다..."
