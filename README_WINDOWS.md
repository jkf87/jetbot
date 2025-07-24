# 윈도우용 JetBot 시뮬레이션 시스템

카메라가 있는 윈도우 환경에서 JetBot의 자율주행 기능을 시뮬레이션할 수 있는 시스템입니다.

## 🚀 빠른 시작

### 1. 자동 설치 (권장)
```bash
# 설치 스크립트 실행
setup_windows.bat
```

### 2. 수동 설치
```bash
# Python 패키지 설치
pip install -r requirements_windows.txt

# 카메라 테스트
python camera_test_windows.py

# JetBot 시뮬레이션 실행
python windows_jetbot.py
```

## 📋 시스템 요구사항

### 하드웨어
- **카메라**: 웹캠 또는 USB 카메라
- **메모리**: 최소 4GB RAM (권장 8GB)
- **저장공간**: 1GB 이상의 여유 공간

### 소프트웨어
- **운영체제**: Windows 10/11
- **Python**: 3.8 이상
- **카메라 드라이버**: 최신 버전

## 🎮 조작 방법

### 키보드 조작
- **W**: 전진
- **S**: 후진
- **A**: 좌회전
- **D**: 우회전
- **Space**: 정지
- **ESC**: 종료

### GUI 조작
- **운행 모드 선택**: 수동/차선 추종/얼굴 추적
- **모터 속도 조절**: 슬라이더로 좌우 모터 속도 개별 제어
- **시작/정지 버튼**: 시뮬레이션 제어

## 🔧 주요 기능

### 1. 수동 제어 모드
- 키보드로 직접 로봇 제어
- 실시간 모터 속도 표시
- 부드러운 가속/감속

### 2. 차선 추종 모드
- OpenCV 기반 차선 검출
- PID 제어로 부드러운 주행
- 실시간 차선 표시

### 3. 얼굴 추적 모드
- Haar Cascade 얼굴 검출
- 자동 카메라 방향 조정
- 실시간 얼굴 위치 표시

## 📁 파일 구조

```
jetbot/
├── windows_jetbot.py          # 메인 시뮬레이션 프로그램
├── camera_test_windows.py     # 카메라 테스트 프로그램
├── setup_windows.bat          # 자동 설치 스크립트
├── requirements_windows.txt   # Python 패키지 목록
└── README_WINDOWS.md         # 이 파일
```

## 🛠️ 설치 가이드

### 1단계: Python 설치
1. [Python 공식 사이트](https://www.python.org/downloads/)에서 Python 3.8 이상 다운로드
2. 설치 시 "Add Python to PATH" 옵션 체크
3. 설치 완료 후 명령 프롬프트에서 확인:
   ```bash
   python --version
   ```

### 2단계: 프로젝트 다운로드
1. 이 프로젝트를 다운로드하거나 클론
2. 명령 프롬프트에서 프로젝트 폴더로 이동

### 3단계: 자동 설치
```bash
# 설치 스크립트 실행
setup_windows.bat
```

### 4단계: 카메라 테스트
```bash
# 카메라 연결 확인
python camera_test_windows.py
```

### 5단계: 시뮬레이션 실행
```bash
# JetBot 시뮬레이션 시작
python windows_jetbot.py
```

## 🔍 문제 해결

### 카메라 관련 문제
```bash
# 카메라 테스트 실행
python camera_test_windows.py
```

**일반적인 해결 방법:**
1. 카메라가 다른 프로그램에서 사용 중인지 확인
2. 카메라 드라이버 업데이트
3. 카메라 권한 확인 (Windows 설정 > 개인정보 > 카메라)

### 패키지 설치 오류
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 가상환경 사용 (권장)
python -m venv jetbot_env
jetbot_env\Scripts\activate
pip install -r requirements_windows.txt
```

### 성능 문제
1. **해상도 조정**: `windows_jetbot.py`에서 카메라 해상도 변경
2. **FPS 조정**: `update_video()` 함수에서 프레임 간격 조정
3. **이미지 처리 최적화**: 차선 검출 파라미터 조정

## ⚙️ 고급 설정

### 차선 검출 파라미터 조정
`windows_jetbot.py`의 `detect_lanes()` 함수에서:

```python
# 엣지 검출 임계값
edges = cv2.Canny(blurred, 50, 150)  # 50, 150 조정

# 직선 검출 파라미터
lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 50, 
                       minLineLength=100, maxLineGap=50)  # 값 조정
```

### PID 제어 게인 조정
```python
# PID 게인 값
kp = 0.01  # 비례 게인
ki = 0.001 # 적분 게인
kd = 0.005 # 미분 게인
```

### 모터 속도 제한
```python
# 속도 제한 (0-1 범위)
self.motor_speeds["left"] = np.clip(self.motor_speeds["left"], 0, 1)
self.motor_speeds["right"] = np.clip(self.motor_speeds["right"], 0, 1)
```

## 📊 성능 모니터링

### 실시간 정보 표시
- FPS (프레임률)
- 모터 속도 (좌/우)
- 카메라 위치 (Pan/Tilt)
- 현재 모드

### 로그 저장
```python
# 로그 파일 생성 (선택사항)
import logging
logging.basicConfig(filename='jetbot_simulation.log', level=logging.INFO)
```

## 🎯 사용 예제

### 기본 사용법
```python
from windows_jetbot import WindowsJetBot

# JetBot 인스턴스 생성
jetbot = WindowsJetBot()

# 시뮬레이션 실행
jetbot.run()
```

### 커스텀 설정
```python
# 카메라 해상도 변경
jetbot.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
jetbot.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# PID 게인 조정
jetbot.kp = 0.02
jetbot.ki = 0.002
jetbot.kd = 0.01
```

## 🔗 추가 자료

- [OpenCV 공식 문서](https://docs.opencv.org/)
- [Python Tkinter 가이드](https://docs.python.org/3/library/tkinter.html)
- [JetBot 프로젝트](https://github.com/NVIDIA-AI-IOT/jetbot)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해 주세요.

---

**⚠️ 주의사항**
- 시뮬레이션 중에는 실제 로봇이 움직이지 않습니다
- 카메라 권한을 허용해야 정상 작동합니다
- 안정적인 성능을 위해 충분한 메모리를 확보하세요 