#!/usr/bin/env python3
"""
JetBot C100 보드용 하드웨어 추상화 레이어
모터 제어, GPIO 제어 등 하드웨어 인터페이스 통합
"""

import time
import sys
import os
try:
    import Jetson.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    print("Warning: Jetson.GPIO not available, using mock mode")
    GPIO_AVAILABLE = False

try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    from adafruit_motor import motor
    PCA9685_AVAILABLE = True
except ImportError:
    print("Warning: PCA9685 library not available, using GPIO mode")
    PCA9685_AVAILABLE = False

class MockGPIO:
    """GPIO Mock 클래스 (테스트용)"""
    BCM = "BCM"
    OUT = "OUT"
    PWM = "PWM"
    
    @staticmethod
    def setmode(mode):
        pass
    
    @staticmethod
    def setup(pin, mode):
        pass
    
    @staticmethod
    def PWM(pin, freq):
        return MockPWM()
    
    @staticmethod
    def cleanup():
        pass

class MockPWM:
    """PWM Mock 클래스 (테스트용)"""
    def start(self, duty):
        pass
    
    def ChangeDutyCycle(self, duty):
        pass
    
    def stop(self):
        pass

class JetBotMotor:
    """JetBot 모터 제어 클래스"""
    
    def __init__(self, use_pca9685=True):
        self.use_pca9685 = use_pca9685 and PCA9685_AVAILABLE
        self.pca = None
        self.motors = {}
        self.gpio_pins = {}
        self.pwm_objects = {}
        
        # C100 보드 핀 매핑 (필요시 수정)
        self.PIN_CONFIG = {
            'left_motor_pwm': 12,
            'left_motor_dir1': 16,
            'left_motor_dir2': 18,
            'right_motor_pwm': 13,
            'right_motor_dir1': 15,
            'right_motor_dir2': 19
        }
        
        self.initialize()
    
    def initialize(self):
        """하드웨어 초기화"""
        try:
            if self.use_pca9685:
                self._init_pca9685()
            else:
                self._init_gpio()
            print(f"모터 제어 초기화 완료 (모드: {'PCA9685' if self.use_pca9685 else 'GPIO'})")
            return True
        except Exception as e:
            print(f"모터 초기화 실패: {e}")
            return False
    
    def _init_pca9685(self):
        """PCA9685 초기화"""
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(i2c)
        self.pca.frequency = 1000
        
        # 모터 객체 생성
        self.motors['left'] = motor.DCMotor(self.pca.channels[0], self.pca.channels[1])
        self.motors['right'] = motor.DCMotor(self.pca.channels[2], self.pca.channels[3])
    
    def _init_gpio(self):
        """GPIO 초기화"""
        if GPIO_AVAILABLE:
            gpio_module = GPIO
        else:
            gpio_module = MockGPIO()
            
        gpio_module.setmode(gpio_module.BCM)
        
        # 핀 설정
        for pin_name, pin_num in self.PIN_CONFIG.items():
            if 'pwm' in pin_name:
                gpio_module.setup(pin_num, gpio_module.OUT)
                self.pwm_objects[pin_name] = gpio_module.PWM(pin_num, 1000)
                self.pwm_objects[pin_name].start(0)
            else:
                gpio_module.setup(pin_num, gpio_module.OUT)
                self.gpio_pins[pin_name] = pin_num
    
    def set_motor_speed(self, motor_name, speed):
        """
        모터 속도 설정
        motor_name: 'left' 또는 'right'
        speed: -1.0 ~ 1.0 (음수는 역방향)
        """
        if not -1.0 <= speed <= 1.0:
            raise ValueError("속도는 -1.0 ~ 1.0 사이여야 합니다.")
        
        if self.use_pca9685:
            self._set_pca9685_speed(motor_name, speed)
        else:
            self._set_gpio_speed(motor_name, speed)
    
    def _set_pca9685_speed(self, motor_name, speed):
        """PCA9685로 모터 속도 설정"""
        if motor_name in self.motors:
            self.motors[motor_name].throttle = speed
    
    def _set_gpio_speed(self, motor_name, speed):
        """GPIO로 모터 속도 설정"""
        if not GPIO_AVAILABLE:
            print(f"Mock mode: {motor_name} motor speed = {speed}")
            return
            
        pwm_pin = f"{motor_name}_motor_pwm"
        dir1_pin = f"{motor_name}_motor_dir1"
        dir2_pin = f"{motor_name}_motor_dir2"
        
        if all(pin in self.PIN_CONFIG for pin in [pwm_pin, dir1_pin, dir2_pin]):
            # 방향 설정
            if speed >= 0:
                GPIO.output(self.gpio_pins[dir1_pin], GPIO.HIGH)
                GPIO.output(self.gpio_pins[dir2_pin], GPIO.LOW)
            else:
                GPIO.output(self.gpio_pins[dir1_pin], GPIO.LOW)
                GPIO.output(self.gpio_pins[dir2_pin], GPIO.HIGH)
            
            # 속도 설정
            duty_cycle = abs(speed) * 100
            self.pwm_objects[pwm_pin].ChangeDutyCycle(duty_cycle)
    
    def move_forward(self, speed=0.5):
        """전진"""
        self.set_motor_speed('left', speed)
        self.set_motor_speed('right', speed)
    
    def move_backward(self, speed=0.5):
        """후진"""
        self.set_motor_speed('left', -speed)
        self.set_motor_speed('right', -speed)
    
    def turn_left(self, speed=0.5):
        """좌회전"""
        self.set_motor_speed('left', -speed)
        self.set_motor_speed('right', speed)
    
    def turn_right(self, speed=0.5):
        """우회전"""
        self.set_motor_speed('left', speed)
        self.set_motor_speed('right', -speed)
    
    def stop(self):
        """정지"""
        self.set_motor_speed('left', 0)
        self.set_motor_speed('right', 0)
    
    def cleanup(self):
        """리소스 정리"""
        self.stop()
        
        if self.use_pca9685 and self.pca:
            self.pca.deinit()
        
        if not self.use_pca9685:
            for pwm in self.pwm_objects.values():
                pwm.stop()
            
            if GPIO_AVAILABLE:
                GPIO.cleanup()
        
        print("모터 제어 정리 완료")

class JetBotController:
    """JetBot 통합 제어 클래스"""
    
    def __init__(self, use_pca9685=True):
        self.motor = JetBotMotor(use_pca9685)
        self.is_running = False
    
    def initialize(self):
        """초기화"""
        return self.motor.initialize()
    
    def start(self):
        """제어 시작"""
        self.is_running = True
        print("JetBot 제어 시작")
    
    def stop(self):
        """제어 정지"""
        self.is_running = False
        self.motor.stop()
        print("JetBot 제어 정지")
    
    def move(self, linear_speed, angular_speed):
        """
        로봇 이동 제어
        linear_speed: 전진/후진 속도 (-1.0 ~ 1.0)
        angular_speed: 회전 속도 (-1.0 ~ 1.0, 음수는 좌회전)
        """
        if not self.is_running:
            return
        
        # 차동 구동 계산
        left_speed = linear_speed - angular_speed
        right_speed = linear_speed + angular_speed
        
        # 속도 제한
        left_speed = max(-1.0, min(1.0, left_speed))
        right_speed = max(-1.0, min(1.0, right_speed))
        
        self.motor.set_motor_speed('left', left_speed)
        self.motor.set_motor_speed('right', right_speed)
    
    def cleanup(self):
        """리소스 정리"""
        self.stop()
        self.motor.cleanup()

def test_hardware():
    """하드웨어 테스트"""
    print("=== JetBot 하드웨어 테스트 ===")
    
    # PCA9685 먼저 시도, 실패하면 GPIO 모드
    controller = JetBotController(use_pca9685=True)
    
    if not controller.initialize():
        print("PCA9685 모드 실패, GPIO 모드로 재시도...")
        controller = JetBotController(use_pca9685=False)
        if not controller.initialize():
            print("하드웨어 초기화 실패!")
            return False
    
    controller.start()
    
    try:
        # 기본 동작 테스트
        print("전진 테스트...")
        controller.motor.move_forward(0.3)
        time.sleep(2)
        
        print("후진 테스트...")
        controller.motor.move_backward(0.3)
        time.sleep(2)
        
        print("좌회전 테스트...")
        controller.motor.turn_left(0.3)
        time.sleep(1)
        
        print("우회전 테스트...")
        controller.motor.turn_right(0.3)
        time.sleep(1)
        
        print("정지...")
        controller.motor.stop()
        
        # 차동 구동 테스트
        print("차동 구동 테스트...")
        for i in range(10):
            linear = 0.2
            angular = 0.1 * (i - 5)  # -0.5 ~ 0.5
            controller.move(linear, angular)
            time.sleep(0.5)
        
        controller.stop()
        print("하드웨어 테스트 완료!")
        
    except KeyboardInterrupt:
        print("사용자에 의해 테스트 중단")
    
    finally:
        controller.cleanup()
    
    return True

if __name__ == "__main__":
    test_hardware()