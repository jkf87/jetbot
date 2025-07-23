#!/bin/bash

echo "=== JetBot C100 보드 환경 설정 스크립트 ==="
echo "Jetson Nano 4GB에서 C100 보드를 사용한 JetBot 설정을 진행합니다."

# 시스템 업데이트
echo "1. 시스템 업데이트 중..."
sudo apt update && sudo apt upgrade -y

# 필수 라이브러리 설치
echo "2. 필수 라이브러리 설치 중..."
sudo apt install -y python3-pip python3-dev python3-opencv
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y python3-numpy python3-matplotlib
sudo apt install -y i2c-tools libi2c-dev
sudo apt install -y gpio

# Python 패키지 설치
echo "3. Python 패키지 설치 중..."
pip3 install --upgrade pip
pip3 install opencv-python==4.5.3.56
pip3 install numpy
pip3 install matplotlib
pip3 install Jetson.GPIO
pip3 install adafruit-circuitpython-motor
pip3 install adafruit-circuitpython-pca9685

# I2C 활성화
echo "4. I2C 인터페이스 활성화 중..."
if ! grep -q "i2c-dev" /etc/modules; then
    echo "i2c-dev" | sudo tee -a /etc/modules
fi

# 카메라 권한 설정
echo "5. 카메라 권한 설정 중..."
sudo usermod -a -G video $USER

# GPIO 권한 설정
echo "6. GPIO 권한 설정 중..."
sudo groupadd -f -r gpio
sudo usermod -a -G gpio $USER

# udev 규칙 설정 (C100 보드용)
echo "7. C100 보드 udev 규칙 설정 중..."
sudo tee /etc/udev/rules.d/99-jetbot-c100.rules > /dev/null <<EOF
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'"
EOF

sudo udevadm control --reload-rules && sudo udevctl trigger

# 작업 디렉토리 생성
echo "8. 작업 디렉토리 구조 생성 중..."
mkdir -p ~/jetbot/src
mkdir -p ~/jetbot/models
mkdir -p ~/jetbot/data
mkdir -p ~/jetbot/logs

# 환경 변수 설정
echo "9. 환경 변수 설정 중..."
if ! grep -q "JETBOT_C100" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# JetBot C100 환경 변수" >> ~/.bashrc
    echo "export JETBOT_C100=1" >> ~/.bashrc
    echo "export PYTHONPATH=$PYTHONPATH:~/jetbot/src" >> ~/.bashrc
fi

echo "=== 설정 완료! ==="
echo "다음 명령어로 설정을 적용하세요:"
echo "source ~/.bashrc"
echo ""
echo "재부팅 후 카메라 테스트를 진행하세요:"
echo "python3 ~/jetbot/camera_test.py"