@echo off
chcp 65001 >nul
echo ========================================
echo 윈도우용 JetBot 시뮬레이션 설치 스크립트
echo ========================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo Python 3.8 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 설치 확인됨
python --version

REM pip 업그레이드
echo.
echo 📦 pip 업그레이드 중...
python -m pip install --upgrade pip

REM 가상환경 생성 (선택사항)
echo.
set /p create_venv="가상환경을 생성하시겠습니까? (y/n): "
if /i "%create_venv%"=="y" (
    echo 🔧 가상환경 생성 중...
    python -m venv jetbot_env
    echo ✅ 가상환경 생성 완료
    echo.
    echo 가상환경을 활성화하려면 다음 명령어를 실행하세요:
    echo jetbot_env\Scripts\activate
    echo.
    set /p activate_venv="지금 가상환경을 활성화하시겠습니까? (y/n): "
    if /i "%activate_venv%"=="y" (
        call jetbot_env\Scripts\activate
    )
)

REM 패키지 설치
echo.
echo 📥 필요한 패키지 설치 중...
pip install -r requirements_windows.txt

if errorlevel 1 (
    echo ❌ 패키지 설치 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo ✅ 패키지 설치 완료

REM 카메라 테스트
echo.
echo 📷 카메라 테스트 중...
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅ 카메라 연결 성공' if cap.isOpened() else '⚠️ 카메라를 찾을 수 없습니다'); cap.release()"

echo.
echo ========================================
echo 설치 완료!
echo ========================================
echo.
echo 실행 방법:
echo python windows_jetbot.py
echo.
echo 키 조작:
echo - W: 전진
echo - S: 후진  
echo - A: 좌회전
echo - D: 우회전
echo - Space: 정지
echo.
set /p run_now="지금 JetBot 시뮬레이션을 실행하시겠습니까? (y/n): "
if /i "%run_now%"=="y" (
    python windows_jetbot.py
)

pause 