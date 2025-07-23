#!/usr/bin/env python3
"""
JetBot C100 보드용 자율주행 시스템
카메라 기반 Lane Following 알고리즘
"""

import cv2
import numpy as np
import time
import sys
import os
import math
from camera_test import JetBotCamera
from jetbot_hardware import JetBotController

class PIDController:
    """PID 제어기"""
    
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, setpoint=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        
        self.prev_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
    
    def update(self, measurement):
        """PID 업데이트"""
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0.0:
            return 0.0
        
        error = self.setpoint - measurement
        
        # Proportional term
        proportional = self.kp * error
        
        # Integral term
        self.integral += error * dt
        integral = self.ki * self.integral
        
        # Derivative term
        derivative = self.kd * (error - self.prev_error) / dt
        
        # PID output
        output = proportional + integral + derivative
        
        # Update for next iteration
        self.prev_error = error
        self.last_time = current_time
        
        return output
    
    def reset(self):
        """PID 리셋"""
        self.prev_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()

class LaneDetector:
    """차선 검출 클래스"""
    
    def __init__(self, roi_height_ratio=0.6):
        self.roi_height_ratio = roi_height_ratio
        
        # HSV 색상 범위 (노란색과 흰색 차선)
        self.yellow_lower = np.array([15, 100, 100])
        self.yellow_upper = np.array([35, 255, 255])
        self.white_lower = np.array([0, 0, 200])
        self.white_upper = np.array([255, 30, 255])
        
        # 캐니 엣지 파라미터
        self.canny_low = 50
        self.canny_high = 150
        
        # 허프 변환 파라미터
        self.hough_rho = 1
        self.hough_theta = np.pi / 180
        self.hough_threshold = 50
        self.hough_min_line_length = 100
        self.hough_max_line_gap = 50
    
    def preprocess_frame(self, frame):
        """프레임 전처리"""
        height, width = frame.shape[:2]
        
        # ROI 설정 (관심 영역만 추출)
        roi_top = int(height * (1 - self.roi_height_ratio))
        roi = frame[roi_top:height, 0:width]
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 가우시안 블러
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return roi, gray, blurred, roi_top
    
    def detect_color_lanes(self, frame):
        """색상 기반 차선 검출"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 노란색과 흰색 차선 마스크
        yellow_mask = cv2.inRange(hsv, self.yellow_lower, self.yellow_upper)
        white_mask = cv2.inRange(hsv, self.white_lower, self.white_upper)
        
        # 마스크 결합
        combined_mask = cv2.bitwise_or(yellow_mask, white_mask)
        
        return combined_mask
    
    def detect_edge_lanes(self, gray):
        """엣지 기반 차선 검출"""
        edges = cv2.Canny(gray, self.canny_low, self.canny_high)
        return edges
    
    def find_lane_lines(self, binary_image):
        """허프 변환으로 차선 찾기"""
        lines = cv2.HoughLinesP(
            binary_image,
            self.hough_rho,
            self.hough_theta,
            self.hough_threshold,
            minLineLength=self.hough_min_line_length,
            maxLineGap=self.hough_max_line_gap
        )
        
        return lines
    
    def classify_lines(self, lines, image_width):
        """직선을 좌측/우측 차선으로 분류"""
        if lines is None:
            return [], []
        
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 기울기 계산
            if x2 - x1 == 0:
                continue
            
            slope = (y2 - y1) / (x2 - x1)
            
            # 기울기로 좌/우 분류
            if slope < -0.3:  # 좌측 차선 (음의 기울기)
                if x1 < image_width * 0.6 and x2 < image_width * 0.6:
                    left_lines.append(line[0])
            elif slope > 0.3:  # 우측 차선 (양의 기울기)
                if x1 > image_width * 0.4 and x2 > image_width * 0.4:
                    right_lines.append(line[0])
        
        return left_lines, right_lines
    
    def average_line(self, lines):
        """여러 직선의 평균 계산"""
        if not lines:
            return None
        
        x_coords = []
        y_coords = []
        
        for line in lines:
            x1, y1, x2, y2 = line
            x_coords.extend([x1, x2])
            y_coords.extend([y1, y2])
        
        if len(x_coords) < 2:
            return None
        
        # 최소자승법으로 직선 피팅
        poly = np.polyfit(y_coords, x_coords, 1)
        
        return poly
    
    def get_lane_center(self, frame):
        """차선 중앙 위치 계산"""
        roi, gray, blurred, roi_top = self.preprocess_frame(frame)
        height, width = roi.shape[:2]
        
        # 색상 기반 검출
        color_mask = self.detect_color_lanes(roi)
        
        # 엣지 기반 검출
        edge_mask = self.detect_edge_lanes(blurred)
        
        # 마스크 결합
        combined_mask = cv2.bitwise_or(color_mask, edge_mask)
        
        # 직선 검출
        lines = self.find_lane_lines(combined_mask)
        
        if lines is None:
            return None, None, roi, combined_mask
        
        # 좌/우 차선 분류
        left_lines, right_lines = self.classify_lines(lines, width)
        
        # 평균 직선 계산
        left_poly = self.average_line(left_lines)
        right_poly = self.average_line(right_lines)
        
        # 차선 중앙 계산
        lane_center = None
        y_eval = height - 1  # 화면 하단
        
        if left_poly is not None and right_poly is not None:
            # 양쪽 차선이 모두 검출된 경우
            left_x = left_poly[0] * y_eval + left_poly[1]
            right_x = right_poly[0] * y_eval + right_poly[1]
            lane_center = (left_x + right_x) / 2
        elif left_poly is not None:
            # 좌측 차선만 검출된 경우
            left_x = left_poly[0] * y_eval + left_poly[1]
            lane_center = left_x + width * 0.3  # 추정
        elif right_poly is not None:
            # 우측 차선만 검출된 경우
            right_x = right_poly[0] * y_eval + right_poly[1]
            lane_center = right_x - width * 0.3  # 추정
        
        return lane_center, (left_poly, right_poly), roi, combined_mask

class AutonomousDriving:
    """자율주행 시스템"""
    
    def __init__(self):
        self.camera = JetBotCamera(width=640, height=480, fps=30)
        self.controller = JetBotController()
        self.lane_detector = LaneDetector()
        
        # PID 제어기 (조향용)
        self.steering_pid = PIDController(kp=0.5, ki=0.1, kd=0.2, setpoint=0.0)
        
        # 주행 파라미터
        self.base_speed = 0.2
        self.max_steering = 0.8
        self.frame_center = 320  # 640/2
        
        # 상태 변수
        self.is_running = False
        self.debug_mode = True
        
        # 성능 모니터링
        self.frame_count = 0
        self.start_time = time.time()
    
    def initialize(self):
        """시스템 초기화"""
        print("자율주행 시스템 초기화 중...")
        
        if not self.camera.initialize():
            print("카메라 초기화 실패!")
            return False
        
        if not self.controller.initialize():
            print("하드웨어 초기화 실패!")
            return False
        
        print("자율주행 시스템 초기화 완료!")
        return True
    
    def process_frame(self, frame):
        """프레임 처리 및 제어 명령 생성"""
        # 차선 중앙 검출
        lane_center, lane_polys, roi, mask = self.lane_detector.get_lane_center(frame)
        
        if lane_center is None:
            # 차선을 찾지 못한 경우
            return 0.0, 0.0, roi, mask
        
        # 조향 오차 계산
        steering_error = lane_center - self.frame_center
        
        # PID 제어로 조향 각도 계산
        steering_output = self.steering_pid.update(steering_error)
        
        # 조향 제한
        steering_output = max(-self.max_steering, min(self.max_steering, steering_output))
        
        # 속도 조정 (급격한 조향 시 감속)
        speed_factor = 1.0 - abs(steering_output) * 0.5
        linear_speed = self.base_speed * speed_factor
        
        return linear_speed, -steering_output, roi, mask
    
    def run(self):
        """자율주행 실행"""
        if not self.initialize():
            return False
        
        self.controller.start()
        self.is_running = True
        
        print("자율주행 시작! (ESC 키로 종료)")
        print(f"기본 속도: {self.base_speed}, 최대 조향: {self.max_steering}")
        
        try:
            while self.is_running:
                ret, frame = self.camera.read_frame()
                
                if not ret:
                    print("프레임 읽기 실패")
                    break
                
                # 프레임 처리
                linear_speed, angular_speed, roi, mask = self.process_frame(frame)
                
                # 로봇 제어
                self.controller.move(linear_speed, angular_speed)
                
                # 디버그 정보 표시
                if self.debug_mode:
                    self._display_debug_info(frame, roi, mask, linear_speed, angular_speed)
                
                self.frame_count += 1
                
                # 키보드 입력 처리
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC 키
                    break
                elif key == ord('s'):  # 's' 키로 정지/재시작
                    if self.controller.is_running:
                        self.controller.stop()
                        print("일시 정지")
                    else:
                        self.controller.start()
                        print("재시작")
                elif key == ord('d'):  # 'd' 키로 디버그 모드 토글
                    self.debug_mode = not self.debug_mode
                    print(f"디버그 모드: {'ON' if self.debug_mode else 'OFF'}")
        
        except KeyboardInterrupt:
            print("사용자에 의해 중단됨")
        
        finally:
            self._cleanup()
        
        return True
    
    def _display_debug_info(self, frame, roi, mask, linear_speed, angular_speed):
        """디버그 정보 표시"""
        # ROI 및 마스크 표시
        debug_roi = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        # 중앙선 표시
        cv2.line(debug_roi, (self.frame_center, 0), (self.frame_center, roi.shape[0]), (0, 255, 0), 2)
        
        # 정보 텍스트
        info_text = [
            f"Speed: {linear_speed:.2f}",
            f"Steering: {angular_speed:.2f}",
            f"FPS: {self.frame_count / (time.time() - self.start_time):.1f}"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(debug_roi, text, (10, 30 + i * 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 결과 표시
        combined = np.hstack([cv2.resize(roi, (320, 240)), 
                             cv2.resize(debug_roi, (320, 240))])
        cv2.imshow('Autonomous Driving Debug', combined)
    
    def _cleanup(self):
        """리소스 정리"""
        self.is_running = False
        self.controller.cleanup()
        self.camera.release()
        cv2.destroyAllWindows()
        
        elapsed_time = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
        
        print(f"자율주행 종료")
        print(f"총 프레임: {self.frame_count}, 평균 FPS: {avg_fps:.1f}")

def manual_control_test():
    """수동 제어 테스트"""
    print("=== 수동 제어 테스트 ===")
    print("키 조작:")
    print("w: 전진, s: 후진, a: 좌회전, d: 우회전")
    print("q: 종료, space: 정지")
    
    controller = JetBotController()
    
    if not controller.initialize():
        print("하드웨어 초기화 실패!")
        return False
    
    controller.start()
    speed = 0.3
    
    try:
        while True:
            key = input("명령 입력 (w/s/a/d/space/q): ").strip().lower()
            
            if key == 'w':
                controller.motor.move_forward(speed)
                print("전진")
            elif key == 's':
                controller.motor.move_backward(speed)
                print("후진")
            elif key == 'a':
                controller.motor.turn_left(speed)
                print("좌회전")
            elif key == 'd':
                controller.motor.turn_right(speed)
                print("우회전")
            elif key == ' ':
                controller.motor.stop()
                print("정지")
            elif key == 'q':
                break
            else:
                print("잘못된 입력입니다.")
    
    except KeyboardInterrupt:
        print("사용자에 의해 중단됨")
    
    finally:
        controller.cleanup()
    
    return True

def main():
    """메인 함수"""
    print("JetBot C100 자율주행 시스템")
    print("1. 자율주행 시작")
    print("2. 수동 제어 테스트")
    print("3. 하드웨어 테스트")
    
    try:
        choice = input("선택하세요 (1-3): ").strip()
        
        if choice == "1":
            autonomous = AutonomousDriving()
            autonomous.run()
        elif choice == "2":
            manual_control_test()
        elif choice == "3":
            from jetbot_hardware import test_hardware
            test_hardware()
        else:
            print("잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()