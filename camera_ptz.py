#!/usr/bin/env python3
"""
JetBot C100 보드용 카메라 PTZ(Pan-Tilt-Zoom) 제어
서보 모터를 사용한 카메라 방향 제어
"""

import time
import math
import sys
import cv2
import numpy as np

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
    from adafruit_motor import servo
    PCA9685_AVAILABLE = True
except ImportError:
    print("Warning: PCA9685 library not available, using GPIO PWM mode")
    PCA9685_AVAILABLE = False

from camera_test import JetBotCamera

class MockServo:
    """서보 Mock 클래스 (테스트용)"""
    def __init__(self, name):
        self.name = name
        self._angle = 90
    
    @property
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, value):
        self._angle = max(0, min(180, value))
        print(f"Mock {self.name} servo angle: {self._angle}")

class ServoController:
    """서보 모터 제어 클래스"""
    
    def __init__(self, use_pca9685=True):
        self.use_pca9685 = use_pca9685 and PCA9685_AVAILABLE
        self.pca = None
        self.servos = {}
        
        # 서보 채널 설정 (PCA9685 사용 시)
        self.SERVO_CHANNELS = {
            'pan': 14,   # 좌우 회전
            'tilt': 15   # 상하 회전
        }
        
        # GPIO 핀 설정 (GPIO PWM 사용 시)
        self.SERVO_PINS = {
            'pan': 32,   # GPIO 핀 32
            'tilt': 33   # GPIO 핀 33
        }
        
        # 서보 각도 제한
        self.ANGLE_LIMITS = {
            'pan': (0, 180),    # 좌우 0-180도
            'tilt': (30, 150)   # 상하 30-150도 (카메라 보호)
        }
        
        # 현재 각도
        self.current_angles = {
            'pan': 90,   # 중앙
            'tilt': 90   # 중앙
        }
        
        self.pwm_objects = {}
        
    def initialize(self):
        """서보 제어 초기화"""
        try:
            if self.use_pca9685:
                self._init_pca9685()
            else:
                self._init_gpio_pwm()
            
            # 초기 위치로 이동
            self.move_to_center()
            
            print(f"서보 제어 초기화 완료 (모드: {'PCA9685' if self.use_pca9685 else 'GPIO PWM'})")
            return True
        except Exception as e:
            print(f"서보 초기화 실패: {e}")
            # Mock 모드로 폴백
            self._init_mock()
            return True
    
    def _init_pca9685(self):
        """PCA9685 초기화"""
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(i2c)
        self.pca.frequency = 50  # 서보용 50Hz
        
        # 서보 객체 생성
        for name, channel in self.SERVO_CHANNELS.items():
            self.servos[name] = servo.Servo(self.pca.channels[channel])
    
    def _init_gpio_pwm(self):
        """GPIO PWM 초기화"""
        if not GPIO_AVAILABLE:
            raise Exception("GPIO not available")
        
        GPIO.setmode(GPIO.BOARD)
        
        for name, pin in self.SERVO_PINS.items():
            GPIO.setup(pin, GPIO.OUT)
            pwm = GPIO.PWM(pin, 50)  # 50Hz
            pwm.start(7.5)  # 중앙 위치 (1.5ms pulse)
            self.pwm_objects[name] = pwm
    
    def _init_mock(self):
        """Mock 모드 초기화"""
        for name in ['pan', 'tilt']:
            self.servos[name] = MockServo(name)
    
    def _angle_to_duty_cycle(self, angle):
        """각도를 PWM duty cycle로 변환"""
        # 서보 모터: 0도 = 1ms, 90도 = 1.5ms, 180도 = 2ms
        pulse_width = 1.0 + (angle / 180.0) * 1.0  # 1.0 ~ 2.0ms
        duty_cycle = (pulse_width / 20.0) * 100  # 20ms 주기에서의 duty cycle
        return duty_cycle
    
    def set_angle(self, servo_name, angle):
        """서보 각도 설정"""
        if servo_name not in self.ANGLE_LIMITS:
            raise ValueError(f"Unknown servo: {servo_name}")
        
        # 각도 제한 확인
        min_angle, max_angle = self.ANGLE_LIMITS[servo_name]
        angle = max(min_angle, min(max_angle, angle))
        
        try:
            if self.use_pca9685:
                self.servos[servo_name].angle = angle
            elif GPIO_AVAILABLE and servo_name in self.pwm_objects:
                duty_cycle = self._angle_to_duty_cycle(angle)
                self.pwm_objects[servo_name].ChangeDutyCycle(duty_cycle)
            else:
                # Mock 모드
                if servo_name in self.servos:
                    self.servos[servo_name].angle = angle
            
            self.current_angles[servo_name] = angle
            
        except Exception as e:
            print(f"서보 각도 설정 실패 ({servo_name}): {e}")
    
    def get_angle(self, servo_name):
        """현재 서보 각도 반환"""
        return self.current_angles.get(servo_name, 90)
    
    def move_to_center(self):
        """중앙 위치로 이동"""
        self.set_angle('pan', 90)
        self.set_angle('tilt', 90)
        time.sleep(1)  # 이동 시간 대기
    
    def pan(self, angle):
        """좌우 회전"""
        self.set_angle('pan', angle)
    
    def tilt(self, angle):
        """상하 회전"""
        self.set_angle('tilt', angle)
    
    def relative_move(self, pan_delta, tilt_delta):
        """상대 이동"""
        new_pan = self.current_angles['pan'] + pan_delta
        new_tilt = self.current_angles['tilt'] + tilt_delta
        
        self.set_angle('pan', new_pan)
        self.set_angle('tilt', new_tilt)
    
    def cleanup(self):
        """리소스 정리"""
        # 중앙 위치로 복귀
        self.move_to_center()
        
        if self.pca:
            self.pca.deinit()
        
        if GPIO_AVAILABLE:
            for pwm in self.pwm_objects.values():
                pwm.stop()
            GPIO.cleanup()
        
        print("서보 제어 정리 완료")

class PTZCamera:
    """PTZ 카메라 제어 클래스"""
    
    def __init__(self):
        self.camera = JetBotCamera()
        self.servo_controller = ServoController()
        self.is_tracking = False
        
        # 객체 추적용 변수
        self.tracker = None
        self.tracking_bbox = None
        
        # 얼굴 검출기
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.face_detection_available = True
        except:
            print("Warning: Face detection not available")
            self.face_detection_available = False
    
    def initialize(self):
        """PTZ 카메라 초기화"""
        if not self.camera.initialize():
            print("카메라 초기화 실패!")
            return False
        
        if not self.servo_controller.initialize():
            print("서보 초기화 실패!")
            return False
        
        print("PTZ 카메라 초기화 완료!")
        return True
    
    def manual_control(self):
        """수동 PTZ 제어"""
        print("=== PTZ 수동 제어 ===")
        print("키 조작:")
        print("w/s: 상하 이동, a/d: 좌우 이동")
        print("r: 중앙 복귀, q: 종료")
        
        pan_step = 5
        tilt_step = 5
        
        try:
            while True:
                ret, frame = self.camera.read_frame()
                
                if ret:
                    # 현재 각도 표시
                    pan_angle = self.servo_controller.get_angle('pan')
                    tilt_angle = self.servo_controller.get_angle('tilt')
                    
                    cv2.putText(frame, f"Pan: {pan_angle:.0f}deg", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Tilt: {tilt_angle:.0f}deg", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # 중앙 십자선 표시
                    h, w = frame.shape[:2]
                    cv2.line(frame, (w//2-20, h//2), (w//2+20, h//2), (0, 255, 0), 2)
                    cv2.line(frame, (w//2, h//2-20), (w//2, h//2+20), (0, 255, 0), 2)
                    
                    cv2.imshow('PTZ Camera Control', frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('w'):  # 위로
                    self.servo_controller.relative_move(0, -tilt_step)
                elif key == ord('s'):  # 아래로
                    self.servo_controller.relative_move(0, tilt_step)
                elif key == ord('a'):  # 왼쪽으로
                    self.servo_controller.relative_move(-pan_step, 0)
                elif key == ord('d'):  # 오른쪽으로
                    self.servo_controller.relative_move(pan_step, 0)
                elif key == ord('r'):  # 중앙 복귀
                    self.servo_controller.move_to_center()
                elif key == ord('q'):  # 종료
                    break
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("사용자에 의해 중단됨")
        
        finally:
            cv2.destroyAllWindows()
    
    def face_tracking(self):
        """얼굴 추적 모드"""
        if not self.face_detection_available:
            print("얼굴 검출 기능을 사용할 수 없습니다.")
            return
        
        print("=== 얼굴 추적 모드 ===")
        print("ESC 키로 종료")
        
        # PID 제어기 (추적용)
        pan_pid = PIDController(kp=0.1, ki=0.01, kd=0.05)
        tilt_pid = PIDController(kp=0.1, ki=0.01, kd=0.05)
        
        try:
            while True:
                ret, frame = self.camera.read_frame()
                
                if not ret:
                    continue
                
                h, w = frame.shape[:2]
                center_x, center_y = w // 2, h // 2
                
                # 얼굴 검출
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 0:
                    # 가장 큰 얼굴 선택
                    largest_face = max(faces, key=lambda f: f[2] * f[3])
                    x, y, face_w, face_h = largest_face
                    
                    # 얼굴 중심 계산
                    face_center_x = x + face_w // 2
                    face_center_y = y + face_h // 2
                    
                    # 오차 계산
                    error_x = face_center_x - center_x
                    error_y = face_center_y - center_y
                    
                    # PID 제어로 서보 각도 조정
                    pan_correction = pan_pid.update(error_x)
                    tilt_correction = tilt_pid.update(error_y)
                    
                    # 서보 이동 (작은 움직임)
                    self.servo_controller.relative_move(-pan_correction * 0.1, tilt_correction * 0.1)
                    
                    # 얼굴 표시
                    cv2.rectangle(frame, (x, y), (x + face_w, y + face_h), (255, 0, 0), 2)
                    cv2.circle(frame, (face_center_x, face_center_y), 5, (0, 255, 0), -1)
                    
                    # 오차 표시
                    cv2.putText(frame, f"Error X: {error_x:.0f}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    cv2.putText(frame, f"Error Y: {error_y:.0f}", (10, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # 중앙 십자선 표시
                cv2.line(frame, (center_x-20, center_y), (center_x+20, center_y), (0, 255, 0), 2)
                cv2.line(frame, (center_x, center_y-20), (center_x, center_y+20), (0, 255, 0), 2)
                
                cv2.imshow('Face Tracking', frame)
                
                if cv2.waitKey(1) & 0xFF == 27:  # ESC 키
                    break
        
        except KeyboardInterrupt:
            print("사용자에 의해 중단됨")
        
        finally:
            cv2.destroyAllWindows()
    
    def patrol_mode(self):
        """순찰 모드 (자동 스캔)"""
        print("=== 순찰 모드 ===")
        print("ESC 키로 종료")
        
        # 순찰 경로 설정
        patrol_points = [
            (45, 90),   # 좌측
            (90, 60),   # 중앙 위
            (135, 90),  # 우측
            (90, 120),  # 중앙 아래
            (90, 90)    # 중앙
        ]
        
        point_index = 0
        move_start_time = time.time()
        move_duration = 3.0  # 각 포인트에서 3초 대기
        
        try:
            while True:
                ret, frame = self.camera.read_frame()
                
                if ret:
                    # 현재 위치 및 목표 표시
                    current_pan = self.servo_controller.get_angle('pan')
                    current_tilt = self.servo_controller.get_angle('tilt')
                    target_pan, target_tilt = patrol_points[point_index]
                    
                    cv2.putText(frame, f"Current: ({current_pan:.0f}, {current_tilt:.0f})", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Target: ({target_pan}, {target_tilt})", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(frame, f"Point: {point_index + 1}/{len(patrol_points)}", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    
                    cv2.imshow('Patrol Mode', frame)
                
                # 다음 포인트로 이동할 시간인지 확인
                if time.time() - move_start_time > move_duration:
                    target_pan, target_tilt = patrol_points[point_index]
                    self.servo_controller.pan(target_pan)
                    self.servo_controller.tilt(target_tilt)
                    
                    point_index = (point_index + 1) % len(patrol_points)
                    move_start_time = time.time()
                    
                    print(f"Moving to point {point_index + 1}: ({target_pan}, {target_tilt})")
                
                if cv2.waitKey(1) & 0xFF == 27:  # ESC 키
                    break
        
        except KeyboardInterrupt:
            print("사용자에 의해 중단됨")
        
        finally:
            cv2.destroyAllWindows()
    
    def cleanup(self):
        """리소스 정리"""
        self.camera.release()
        self.servo_controller.cleanup()

class PIDController:
    """PID 제어기 (추적용)"""
    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
    
    def update(self, error):
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output

def main():
    """메인 함수"""
    print("JetBot PTZ 카메라 제어 시스템")
    print("1. 수동 제어")
    print("2. 얼굴 추적")
    print("3. 순찰 모드")
    print("4. 서보 테스트")
    
    ptz_camera = PTZCamera()
    
    if not ptz_camera.initialize():
        print("PTZ 카메라 초기화 실패!")
        return
    
    try:
        choice = input("선택하세요 (1-4): ").strip()
        
        if choice == "1":
            ptz_camera.manual_control()
        elif choice == "2":
            ptz_camera.face_tracking()
        elif choice == "3":
            ptz_camera.patrol_mode()
        elif choice == "4":
            servo_test()
        else:
            print("잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        ptz_camera.cleanup()

def servo_test():
    """서보 모터 단독 테스트"""
    print("=== 서보 모터 테스트 ===")
    
    servo_controller = ServoController()
    
    if not servo_controller.initialize():
        print("서보 초기화 실패!")
        return
    
    try:
        print("중앙 위치로 이동...")
        servo_controller.move_to_center()
        time.sleep(2)
        
        print("Pan 서보 테스트...")
        for angle in [45, 135, 90]:
            print(f"Pan {angle}도로 이동...")
            servo_controller.pan(angle)
            time.sleep(2)
        
        print("Tilt 서보 테스트...")
        for angle in [60, 120, 90]:
            print(f"Tilt {angle}도로 이동...")
            servo_controller.tilt(angle)
            time.sleep(2)
        
        print("서보 테스트 완료!")
        
    finally:
        servo_controller.cleanup()

if __name__ == "__main__":
    main()