# JetBot C100 보드용 자율주행 시스템

Jetson Nano 4GB + C100 보드 환경에서 동작하는 카메라 기반 자율주행 로봇 시스템입니다.

## 🚀 빠른 시작

```bash
# 1. 빠른 시작 가이드 실행
python3 quick_start.py

# 2. 또는 수동 설정
bash setup_jetbot_c100.sh
source ~/.bashrc
```

## 📁 파일 구조

```
jetbot/
├── setup_jetbot_c100.sh      # 환경 설정 스크립트
├── quick_start.py             # 빠른 시작 가이드
├── camera_test.py             # 카메라 테스트 및 초기화
├── jetbot_hardware.py         # 하드웨어 추상화 레이어
├── autonomous_driving.py      # 자율주행 메인 시스템
├── camera_ptz.py             # PTZ 카메라 제어
├── slm_integration.py        # AI/SLM 연동 시스템
└── README.md                 # 이 파일
```

## 🔧 주요 기능

### 1. 자율주행 시스템
```bash
python3 autonomous_driving.py
```
- **Lane Following**: 차선 추종 알고리즘
- **PID 제어**: 부드러운 조향 제어
- **실시간 영상처리**: OpenCV 기반 차선 검출
- **안전 기능**: 장애물 감지 시 자동 정지

**키 조작:**
- `ESC`: 종료
- `s`: 일시정지/재개
- `d`: 디버그 모드 토글

### 2. PTZ 카메라 제어
```bash
python3 camera_ptz.py
```
- **수동 제어**: 키보드로 카메라 방향 조절
- **얼굴 추적**: 자동 얼굴 추적 기능
- **순찰 모드**: 자동 스캔 기능

**키 조작:**
- `w/s`: 상하 이동
- `a/d`: 좌우 이동
- `r`: 중앙 복귀
- `q`: 종료

### 3. AI 연동 시스템
```bash
python3 slm_integration.py
```
- **장면 분석**: 카메라 영상 AI 분석
- **자동 판단**: AI 기반 행동 결정
- **대화형 모드**: 음성/텍스트 명령 처리

## 🛠️ 하드웨어 요구사항

### 필수 구성품
- **Jetson Nano 4GB** 개발자 키트
- **C100 보드** (JetBot 호환)
- **CSI 카메라** (또는 USB 카메라)
- **DC 기어드 모터** x2
- **서보 모터** x2 (PTZ 기능용, 선택사항)
- **PCA9685 PWM 드라이버** (권장)

### 핀 연결 (C100 보드)
```
모터 제어:
- 좌측 모터: GPIO 12(PWM), 16(DIR1), 18(DIR2)
- 우측 모터: GPIO 13(PWM), 15(DIR1), 19(DIR2)

서보 모터 (PTZ):
- Pan 서보: GPIO 32 또는 PCA9685 CH14
- Tilt 서보: GPIO 33 또는 PCA9685 CH15

I2C (PCA9685):
- SDA: GPIO 2
- SCL: GPIO 3
```

## 📦 소프트웨어 요구사항

### 시스템 패키지
```bash
sudo apt update
sudo apt install -y python3-pip python3-opencv
sudo apt install -y i2c-tools libi2c-dev gpio
```

### Python 패키지
```bash
pip3 install opencv-python numpy matplotlib
pip3 install Jetson.GPIO
pip3 install adafruit-circuitpython-pca9685
pip3 install adafruit-circuitpython-motor
```

## 🔍 테스트 및 디버깅

### 1. 카메라 테스트
```bash
python3 camera_test.py
```
- 기본 카메라 동작 확인
- 이미지 처리 성능 테스트
- 테스트 이미지 캡처

### 2. 하드웨어 테스트
```bash
python3 jetbot_hardware.py
```
- 모터 동작 확인
- GPIO/I2C 통신 테스트
- 차동 구동 테스트

### 3. 종합 테스트
```bash
python3 quick_start.py
```
- 전체 시스템 순차 테스트
- 문제 진단 및 해결 가이드

## ⚙️ 설정 및 튜닝

### 자율주행 파라미터 조정
`autonomous_driving.py`에서 다음 값들을 조정:

```python
# 주행 속도
self.base_speed = 0.2  # 기본 속도 (0.1-0.5)

# PID 제어 게인
self.steering_pid = PIDController(
    kp=0.5,   # 비례 게인
    ki=0.1,   # 적분 게인  
    kd=0.2    # 미분 게인
)

# 차선 검출 파라미터
self.canny_low = 50    # 엣지 검출 임계값 (하한)
self.canny_high = 150  # 엣지 검출 임계값 (상한)
```

### 하드웨어 핀 매핑 수정
`jetbot_hardware.py`에서 C100 보드에 맞게 조정:

```python
self.PIN_CONFIG = {
    'left_motor_pwm': 12,   # 좌측 모터 PWM 핀
    'left_motor_dir1': 16,  # 좌측 모터 방향1 핀
    'left_motor_dir2': 18,  # 좌측 모터 방향2 핀
    'right_motor_pwm': 13,  # 우측 모터 PWM 핀
    'right_motor_dir1': 15, # 우측 모터 방향1 핀
    'right_motor_dir2': 19  # 우측 모터 방향2 핀
}
```

## 🚨 문제 해결

### 카메라 관련 문제
```bash
# 카메라 권한 확인
ls -l /dev/video*
sudo usermod -a -G video $USER

# CSI 카메라 확인
dmesg | grep -i camera
```

### GPIO 권한 문제
```bash
# GPIO 그룹 추가
sudo usermod -a -G gpio $USER

# 재로그인 또는 재부팅
sudo reboot
```

### I2C 통신 문제
```bash
# I2C 장치 스캔
sudo i2cdetect -y -r 1

# I2C 속도 확인
sudo cat /sys/bus/i2c/drivers/i2c-tegra/1-0040/clock-frequency
```

### 성능 최적화
```bash
# GPU 메모리 설정 (부팅 시)
sudo vim /boot/extlinux/extlinux.conf
# 추가: mem=3G@2G nvdumper_reserved=2G@0x800000000

# 스왑 설정
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📚 사용 예제

### 기본 자율주행
```python
from autonomous_driving import AutonomousDriving

# 자율주행 시스템 생성
autonomous = AutonomousDriving()

# 실행
if autonomous.initialize():
    autonomous.run()
```

### PTZ 카메라 제어
```python
from camera_ptz import PTZCamera

# PTZ 카메라 생성
ptz = PTZCamera()

if ptz.initialize():
    # 수동 제어
    ptz.manual_control()
    
    # 또는 얼굴 추적
    ptz.face_tracking()
```

### AI 연동
```python
from slm_integration import IntelligentJetBot

# AI JetBot 생성
ai_jetbot = IntelligentJetBot(model_type="mock")

if ai_jetbot.initialize():
    # 자율 모드
    ai_jetbot.run_autonomous_mode()
    
    # 또는 대화형 모드
    ai_jetbot.interactive_mode()
```

## 🔗 추가 자료

- [Jetson Nano 개발자 가이드](https://developer.nvidia.com/embedded/jetson-nano-developer-kit)
- [OpenCV 문서](https://docs.opencv.org/)
- [JetBot 프로젝트](https://github.com/NVIDIA-AI-IOT/jetbot)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해 주세요.

---

**⚠️ 안전 주의사항**
- 테스트 시 로봇이 떨어지지 않도록 안전한 환경에서 실행하세요
- 배터리 전압을 정기적으로 확인하세요
- 모터 과부하를 방지하기 위해 적절한 속도로 운영하세요