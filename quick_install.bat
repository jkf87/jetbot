@echo off
chcp 65001 >nul
echo ========================================
echo 빠른 설치 - SSL 인증서 우회
echo ========================================
echo.

echo 🔧 pip 설정 파일 생성 중...
if not exist "%USERPROFILE%\pip" mkdir "%USERPROFILE%\pip"
echo [global] > "%USERPROFILE%\pip\pip.conf"
echo trusted-host = pypi.org >> "%USERPROFILE%\pip\pip.conf"
echo trusted-host = pypi.python.org >> "%USERPROFILE%\pip\pip.conf"
echo trusted-host = files.pythonhosted.org >> "%USERPROFILE%\pip\pip.conf"
echo index-url = https://pypi.org/simple/ >> "%USERPROFILE%\pip\pip.conf"
echo.

echo 📥 필수 패키지 설치 중...
echo.

pip install opencv-contrib-python --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --disable-pip-version-check
pip install numpy --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --disable-pip-version-check
pip install Pillow --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --disable-pip-version-check
pip install tkinter-tooltip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --disable-pip-version-check

echo.
echo ✅ 설치 완료!
echo.
echo 🚀 실행 방법:
echo python camera_test_windows.py
echo python windows_jetbot.py
echo.
pause 