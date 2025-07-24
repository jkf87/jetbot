@echo off
chcp 65001 >nul
echo ========================================
echo 윈도우용 JetBot 시뮬레이션 의존성 설치
echo ========================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo.
    echo Python 3.8 이상을 설치해주세요:
    echo https://www.python.org/downloads/
    echo.
    echo 설치 시 "Add Python to PATH" 옵션을 체크하세요.
    pause
    exit /b 1
)

echo ✅ Python 설치 확인됨
python --version
echo.

REM pip 업그레이드 (SSL 인증서 우회)
echo 📦 pip 업그레이드 중...
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
echo.

REM 가상환경 생성 여부 확인
set /p create_venv="가상환경을 생성하시겠습니까? (권장) (y/n): "
if /i "%create_venv%"=="y" (
    echo 🔧 가상환경 생성 중...
    python -m venv jetbot_env
    
    if errorlevel 1 (
        echo ❌ 가상환경 생성 실패
        pause
        exit /b 1
    )
    
    echo ✅ 가상환경 생성 완료
    echo.
    echo 가상환경을 활성화합니다...
    call jetbot_env\Scripts\activate
    
    if errorlevel 1 (
        echo ❌ 가상환경 활성화 실패
        pause
        exit /b 1
    )
    
    echo ✅ 가상환경 활성화 완료
    echo.
)

REM 기본 패키지 설치
echo 📥 기본 패키지 설치 중...
echo.

echo 1. OpenCV 설치 중...
pip install opencv-contrib-python==4.12.0.88 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

if errorlevel 1 (
    echo ❌ OpenCV 설치 실패
    echo SSL 인증서 문제일 수 있습니다. 수동으로 설치해주세요.
    pause
    exit /b 1
)

echo 2. NumPy 설치 중...
pip install numpy==2.2.6 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

echo 3. Pillow 설치 중...
pip install Pillow==10.2.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

echo 4. Tkinter Tooltip 설치 중...
pip install tkinter-tooltip==2.1.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

echo.
echo ✅ 기본 패키지 설치 완료
echo.

REM 추가 패키지 설치 여부 확인
set /p install_extra="추가 이미지 처리 패키지를 설치하시겠습니까? (scikit-image, matplotlib) (y/n): "
if /i "%install_extra%"=="y" (
    echo 📥 추가 패키지 설치 중...
    echo.
    
    echo 1. scikit-image 설치 중...
    pip install scikit-image==0.22.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    echo 2. matplotlib 설치 중...
    pip install matplotlib==3.8.2 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    echo ✅ 추가 패키지 설치 완료
    echo.
)

REM 개발 도구 설치 여부 확인
set /p install_dev="개발 도구를 설치하시겠습니까? (IPython, Jupyter) (y/n): "
if /i "%install_dev%"=="y" (
    echo 📥 개발 도구 설치 중...
    echo.
    
    echo 1. IPython 설치 중...
    pip install ipython==8.18.1 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    echo 2. Jupyter 설치 중...
    pip install jupyter==1.0.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    echo ✅ 개발 도구 설치 완료
    echo.
)

REM 설치 확인
echo 🔍 설치 확인 중...
echo.

python -c "import cv2; print('✅ OpenCV:', cv2.__version__)"
python -c "import numpy; print('✅ NumPy:', numpy.__version__)"
python -c "import PIL; print('✅ Pillow:', PIL.__version__)"

if /i "%install_extra%"=="y" (
    python -c "import skimage; print('✅ scikit-image:', skimage.__version__)"
    python -c "import matplotlib; print('✅ matplotlib:', matplotlib.__version__)"
)

echo.
echo ========================================
echo 설치 완료!
echo ========================================
echo.

REM 카메라 테스트
echo 📷 카메라 테스트 중...
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅ 카메라 연결 성공' if cap.isOpened() else '⚠️ 카메라를 찾을 수 없습니다'); cap.release()"

echo.
echo 🚀 실행 방법:
echo.
echo 1. 카메라 테스트:
echo    python camera_test_windows.py
echo.
echo 2. JetBot 시뮬레이션:
echo    python windows_jetbot.py
echo.
echo 3. 고급 카메라 테스트 (새로운 기능):
echo    python camera_test_windows.py
echo.

if /i "%create_venv%"=="y" (
    echo 💡 가상환경 사용 시:
    echo    jetbot_env\Scripts\activate
    echo    를 실행하여 가상환경을 활성화하세요.
    echo.
)

set /p run_test="지금 카메라 테스트를 실행하시겠습니까? (y/n): "
if /i "%run_test%"=="y" (
    echo.
    echo 🎬 카메라 테스트 시작...
    python camera_test_windows.py
)

echo.
echo 설치가 완료되었습니다! 즐거운 코딩 되세요! 🎉
pause 