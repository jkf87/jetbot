# 윈도우용 JetBot 시뮬레이션 의존성 설치 (PowerShell)
# PowerShell에서 실행: .\install_dependencies.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "윈도우용 JetBot 시뮬레이션 의존성 설치" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Python 설치 확인
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python 설치 확인됨: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python이 설치되지 않았습니다." -ForegroundColor Red
    Write-Host ""
    Write-Host "Python 3.8 이상을 설치해주세요:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Blue
    Write-Host ""
    Write-Host "설치 시 'Add Python to PATH' 옵션을 체크하세요." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host ""

# pip 업그레이드 (SSL 인증서 우회)
Write-Host "📦 pip 업그레이드 중..." -ForegroundColor Yellow
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
Write-Host ""

# 가상환경 생성 여부 확인
$createVenv = Read-Host "가상환경을 생성하시겠습니까? (권장) (y/n)"
if ($createVenv -eq "y" -or $createVenv -eq "Y") {
    Write-Host "🔧 가상환경 생성 중..." -ForegroundColor Yellow
    python -m venv jetbot_env
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 가상환경 생성 실패" -ForegroundColor Red
        Read-Host "계속하려면 Enter를 누르세요"
        exit 1
    }
    
    Write-Host "✅ 가상환경 생성 완료" -ForegroundColor Green
    Write-Host ""
    Write-Host "가상환경을 활성화합니다..." -ForegroundColor Yellow
    & "jetbot_env\Scripts\Activate.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 가상환경 활성화 실패" -ForegroundColor Red
        Read-Host "계속하려면 Enter를 누르세요"
        exit 1
    }
    
    Write-Host "✅ 가상환경 활성화 완료" -ForegroundColor Green
    Write-Host ""
}

# 기본 패키지 설치
Write-Host "📥 기본 패키지 설치 중..." -ForegroundColor Yellow
Write-Host ""

Write-Host "1. OpenCV 설치 중..." -ForegroundColor Cyan
pip install opencv-contrib-python==4.12.0.88 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ OpenCV 설치 실패" -ForegroundColor Red
    Write-Host "SSL 인증서 문제일 수 있습니다. 수동으로 설치해주세요." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host "2. NumPy 설치 중..." -ForegroundColor Cyan
pip install numpy==2.2.6 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

Write-Host "3. Pillow 설치 중..." -ForegroundColor Cyan
pip install Pillow==10.2.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

Write-Host "4. Tkinter Tooltip 설치 중..." -ForegroundColor Cyan
pip install tkinter-tooltip==2.1.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

Write-Host ""
Write-Host "✅ 기본 패키지 설치 완료" -ForegroundColor Green
Write-Host ""

# 추가 패키지 설치 여부 확인
$installExtra = Read-Host "추가 이미지 처리 패키지를 설치하시겠습니까? (scikit-image, matplotlib) (y/n)"
if ($installExtra -eq "y" -or $installExtra -eq "Y") {
    Write-Host "📥 추가 패키지 설치 중..." -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "1. scikit-image 설치 중..." -ForegroundColor Cyan
    pip install scikit-image==0.22.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    Write-Host "2. matplotlib 설치 중..." -ForegroundColor Cyan
    pip install matplotlib==3.8.2 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    Write-Host "✅ 추가 패키지 설치 완료" -ForegroundColor Green
    Write-Host ""
}

# 개발 도구 설치 여부 확인
$installDev = Read-Host "개발 도구를 설치하시겠습니까? (IPython, Jupyter) (y/n)"
if ($installDev -eq "y" -or $installDev -eq "Y") {
    Write-Host "📥 개발 도구 설치 중..." -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "1. IPython 설치 중..." -ForegroundColor Cyan
    pip install ipython==8.18.1 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    Write-Host "2. Jupyter 설치 중..." -ForegroundColor Cyan
    pip install jupyter==1.0.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    Write-Host "✅ 개발 도구 설치 완료" -ForegroundColor Green
    Write-Host ""
}

# 설치 확인
Write-Host "🔍 설치 확인 중..." -ForegroundColor Yellow
Write-Host ""

python -c "import cv2; print('✅ OpenCV:', cv2.__version__)"
python -c "import numpy; print('✅ NumPy:', numpy.__version__)"
python -c "import PIL; print('✅ Pillow:', PIL.__version__)"

if ($installExtra -eq "y" -or $installExtra -eq "Y") {
    python -c "import skimage; print('✅ scikit-image:', skimage.__version__)"
    python -c "import matplotlib; print('✅ matplotlib:', matplotlib.__version__)"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "설치 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 카메라 테스트
Write-Host "📷 카메라 테스트 중..." -ForegroundColor Yellow
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅ 카메라 연결 성공' if cap.isOpened() else '⚠️ 카메라를 찾을 수 없습니다'); cap.release()"

Write-Host ""
Write-Host "🚀 실행 방법:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 카메라 테스트:" -ForegroundColor White
Write-Host "   python camera_test_windows.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. JetBot 시뮬레이션:" -ForegroundColor White
Write-Host "   python windows_jetbot.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 고급 카메라 테스트 (새로운 기능):" -ForegroundColor White
Write-Host "   python camera_test_windows.py" -ForegroundColor Gray
Write-Host ""

if ($createVenv -eq "y" -or $createVenv -eq "Y") {
    Write-Host "💡 가상환경 사용 시:" -ForegroundColor Yellow
    Write-Host "   jetbot_env\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host "   를 실행하여 가상환경을 활성화하세요." -ForegroundColor Yellow
    Write-Host ""
}

$runTest = Read-Host "지금 카메라 테스트를 실행하시겠습니까? (y/n)"
if ($runTest -eq "y" -or $runTest -eq "Y") {
    Write-Host ""
    Write-Host "🎬 카메라 테스트 시작..." -ForegroundColor Green
    python camera_test_windows.py
}

Write-Host ""
Write-Host "설치가 완료되었습니다! 즐거운 코딩 되세요! 🎉" -ForegroundColor Green
Read-Host "계속하려면 Enter를 누르세요" 