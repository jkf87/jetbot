# 윈도우용 JetBot 시뮬레이션 설치 가이드

카메라가 있는 윈도우 환경에서 JetBot 시뮬레이션과 고급 카메라 테스트 시스템을 설치하는 완전한 가이드입니다.

## 📋 시스템 요구사항

### 하드웨어
- **카메라**: 웹캠 또는 USB 카메라
- **메모리**: 최소 4GB RAM (권장 8GB)
- **저장공간**: 2GB 이상의 여유 공간

### 소프트웨어
- **운영체제**: Windows 10/11
- **Python**: 3.8 이상
- **카메라 드라이버**: 최신 버전

## 🚀 빠른 설치 (권장)

### 방법 1: 자동 설치 스크립트 (가장 간단)

#### 명령 프롬프트(cmd) 사용
```cmd
# 프로젝트 폴더로 이동
cd D:\jetbot\jetbot

# 자동 설치 스크립트 실행
install_dependencies.bat
```

#### PowerShell 사용
```powershell
# 프로젝트 폴더로 이동
cd D:\jetbot\jetbot

# PowerShell 스크립트 실행
.\install_dependencies.ps1
```

### 방법 2: 수동 설치

#### 1단계: Python 설치
1. [Python 공식 사이트](https://www.python.org/downloads/)에서 Python 3.8 이상 다운로드
2. 설치 시 **"Add Python to PATH"** 옵션 체크
3. 설치 완료 후 확인:
   ```cmd
   python --version
   ```

#### 2단계: 가상환경 생성 (권장)
```cmd
# 가상환경 생성
python -m venv jetbot_env

# 가상환경 활성화 (cmd)
jetbot_env\Scripts\activate

# 가상환경 활성화 (PowerShell)
jetbot_env\Scripts\Activate.ps1
```

#### 3단계: 패키지 설치
```cmd
# pip 업그레이드
python -m pip install --upgrade pip

# 기본 패키지 설치
pip install opencv-contrib-python==4.12.0.88
pip install numpy==2.2.6
pip install Pillow==10.2.0
pip install tkinter-tooltip==2.1.0

# 추가 패키지 (선택사항)
pip install scikit-image==0.22.0
pip install matplotlib==3.8.2

# 개발 도구 (선택사항)
pip install ipython==8.18.1
pip install jupyter==1.0.0
```

## 🔧 SSL 인증서 문제 해결

회사 네트워크나 특정 환경에서 SSL 인증서 오류가 발생할 경우:

```cmd
# 신뢰할 수 있는 호스트로 설치
pip install opencv-contrib-python==4.12.0.88 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

## 📦 설치되는 패키지 목록

### 핵심 패키지 (필수)
- **opencv-contrib-python**: 컴퓨터 비전 라이브러리 (GUI 지원)
- **numpy**: 수치 계산 라이브러리
- **Pillow**: 이미지 처리 라이브러리
- **tkinter-tooltip**: GUI 툴팁 기능

### 추가 패키지 (선택사항)
- **scikit-image**: 고급 이미지 처리
- **matplotlib**: 그래프 및 시각화
- **ipython**: 향상된 Python 인터프리터
- **jupyter**: 노트북 환경

## ✅ 설치 확인

설치가 완료되면 다음 명령어로 확인:

```cmd
# 패키지 버전 확인
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import PIL; print('Pillow:', PIL.__version__)"

# 카메라 연결 확인
python -c "import cv2; cap = cv2.VideoCapture(0); print('카메라 연결 성공' if cap.isOpened() else '카메라를 찾을 수 없습니다'); cap.release()"
```

## 🎮 실행 방법

### 1. 기본 카메라 테스트
```cmd
python camera_test_windows.py
```

### 2. JetBot 시뮬레이션
```cmd
python windows_jetbot.py
```

### 3. 고급 카메라 테스트 (새로운 기능)
```cmd
python camera_test_windows.py
```

## 🔍 문제 해결

### Python이 인식되지 않는 경우
1. Python이 PATH에 추가되었는지 확인
2. 시스템 재시작
3. 명령 프롬프트를 관리자 권한으로 실행

### OpenCV 설치 실패
```cmd
# 기존 OpenCV 제거
pip uninstall opencv-python opencv-python-headless -y

# GUI 지원 OpenCV 설치
pip install opencv-contrib-python --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

### 카메라 연결 실패
1. 카메라가 다른 프로그램에서 사용 중인지 확인
2. 카메라 드라이버 업데이트
3. Windows 설정 > 개인정보 > 카메라 권한 확인

### 가상환경 활성화 실패 (PowerShell)
```powershell
# 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 가상환경 활성화
.\jetbot_env\Scripts\Activate.ps1
```

## 📁 프로젝트 구조

```
jetbot/
├── windows_jetbot.py              # JetBot 시뮬레이션 메인
├── camera_test_windows.py         # 고급 카메라 테스트
├── install_dependencies.bat       # 자동 설치 스크립트 (cmd)
├── install_dependencies.ps1       # 자동 설치 스크립트 (PowerShell)
├── requirements_windows.txt       # 패키지 목록
├── INSTALL_GUIDE.md              # 이 파일
└── README_WINDOWS.md             # 사용 가이드
```

## 🎯 설치 후 할 수 있는 것들

### JetBot 시뮬레이션
- **수동 제어**: WASD 키로 로봇 제어
- **차선 추종**: 자동 주행 기능
- **얼굴 추적**: AI 기반 추적

### 고급 카메라 테스트
- **실시간 회전**: 90°, 180°, 270° 회전
- **15가지 필터**: 그레이스케일, 블러, 엣지 검출 등
- **실시간 조정**: 밝기, 대비, 블러 강도
- **스냅샷 저장**: 결과 이미지 저장

## 💡 팁

1. **가상환경 사용**: 프로젝트별로 독립적인 환경 구성
2. **정기적 업데이트**: pip와 패키지 정기 업데이트
3. **백업**: 중요한 설정 파일 백업
4. **성능 최적화**: 충분한 메모리 확보

## 🆘 추가 도움

문제가 발생하면:
1. 이 가이드의 문제 해결 섹션 확인
2. Python과 OpenCV 공식 문서 참조
3. 프로젝트 이슈 등록

---

**🎉 설치가 완료되면 즐거운 JetBot 시뮬레이션을 시작하세요!** 