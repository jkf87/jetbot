#!/usr/bin/env python3
"""
윈도우용 JetBot 시뮬레이션 시스템
카메라가 있는 윈도우 환경에서 JetBot 기능을 시뮬레이션
"""

import cv2
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WindowsJetBot:
    """윈도우용 JetBot 시뮬레이션 클래스"""
    
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.current_mode = "idle"
        self.motor_speeds = {"left": 0, "right": 0}
        self.camera_position = {"pan": 0, "tilt": 0}
        self.lane_detection_active = False
        self.face_detection_active = False
        
        # PID 제어 변수
        self.pid_error = 0
        self.pid_integral = 0
        self.pid_derivative = 0
        self.last_error = 0
        
        # GUI 변수
        self.root = None
        self.video_label = None
        self.status_label = None
        
        print("윈도우용 JetBot 시뮬레이션 초기화 완료")
    
    def initialize_camera(self):
        """카메라 초기화"""
        try:
            # 기본 카메라 (0번) 또는 USB 카메라 시도
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                # 0번 카메라가 실패하면 1번 시도
                self.camera = cv2.VideoCapture(1)
            
            if not self.camera.isOpened():
                print("❌ 카메라를 찾을 수 없습니다.")
                return False
            
            # 카메라 설정
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            print("✅ 카메라 초기화 성공")
            return True
            
        except Exception as e:
            print(f"❌ 카메라 초기화 실패: {e}")
            return False
    
    def detect_lanes(self, frame):
        """차선 검출"""
        # 그레이스케일 변환
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 가우시안 블러
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 엣지 검출
        edges = cv2.Canny(blurred, 50, 150)
        
        # 관심 영역 설정 (하단 절반)
        height, width = edges.shape
        roi_vertices = np.array([
            [(0, height), (width//2, height//2), (width, height)]
        ], dtype=np.int32)
        
        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, roi_vertices, 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # 직선 검출
        lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 50, 
                               minLineLength=100, maxLineGap=50)
        
        if lines is not None:
            # 차선 그리기
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 중앙선 계산
            center_x = width // 2
            lane_center = np.mean([line[0][0] for line in lines])
            self.pid_error = center_x - lane_center
            
            # PID 제어
            steering = self.calculate_pid()
            self.motor_speeds["left"] = 0.5 + steering
            self.motor_speeds["right"] = 0.5 - steering
            
            # 속도 제한
            self.motor_speeds["left"] = np.clip(self.motor_speeds["left"], 0, 1)
            self.motor_speeds["right"] = np.clip(self.motor_speeds["right"], 0, 1)
        
        return frame
    
    def detect_faces(self, frame):
        """얼굴 검출"""
        # 얼굴 검출기 로드
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # 얼굴 중앙 계산
            face_center_x = x + w // 2
            frame_center_x = frame.shape[1] // 2
            
            # 카메라 위치 조정
            if abs(face_center_x - frame_center_x) > 50:
                if face_center_x < frame_center_x:
                    self.camera_position["pan"] -= 2
                else:
                    self.camera_position["pan"] += 2
        
        return frame
    
    def calculate_pid(self):
        """PID 제어 계산"""
        kp = 0.01
        ki = 0.001
        kd = 0.005
        
        self.pid_integral += self.pid_error
        self.pid_derivative = self.pid_error - self.last_error
        
        output = kp * self.pid_error + ki * self.pid_integral + kd * self.pid_derivative
        self.last_error = self.pid_error
        
        return output
    
    def create_gui(self):
        """GUI 생성"""
        self.root = tk.Tk()
        self.root.title("윈도우용 JetBot 시뮬레이션")
        self.root.geometry("800x600")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 비디오 프레임
        video_frame = ttk.LabelFrame(main_frame, text="카메라 영상", padding="5")
        video_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.grid(row=0, column=0)
        
        # 제어 패널
        control_frame = ttk.LabelFrame(main_frame, text="제어 패널", padding="5")
        control_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 모드 선택
        ttk.Label(control_frame, text="운행 모드:").grid(row=0, column=0, sticky=tk.W)
        mode_var = tk.StringVar(value="manual")
        
        def change_mode():
            self.current_mode = mode_var.get()
            self.update_status()
        
        ttk.Radiobutton(control_frame, text="수동", variable=mode_var, 
                       value="manual", command=change_mode).grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(control_frame, text="차선 추종", variable=mode_var, 
                       value="lane", command=change_mode).grid(row=2, column=0, sticky=tk.W)
        ttk.Radiobutton(control_frame, text="얼굴 추적", variable=mode_var, 
                       value="face", command=change_mode).grid(row=3, column=0, sticky=tk.W)
        
        # 모터 제어
        motor_frame = ttk.LabelFrame(control_frame, text="모터 제어", padding="5")
        motor_frame.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # 좌측 모터
        ttk.Label(motor_frame, text="좌측 모터:").grid(row=0, column=0, sticky=tk.W)
        left_speed_var = tk.DoubleVar(value=0)
        left_speed_scale = ttk.Scale(motor_frame, from_=0, to=1, variable=left_speed_var, 
                                   orient=tk.HORIZONTAL, length=150)
        left_speed_scale.grid(row=0, column=1, padx=5)
        
        def update_left_speed():
            self.motor_speeds["left"] = left_speed_var.get()
        
        left_speed_scale.configure(command=lambda x: update_left_speed())
        
        # 우측 모터
        ttk.Label(motor_frame, text="우측 모터:").grid(row=1, column=0, sticky=tk.W)
        right_speed_var = tk.DoubleVar(value=0)
        right_speed_scale = ttk.Scale(motor_frame, from_=0, to=1, variable=right_speed_var, 
                                    orient=tk.HORIZONTAL, length=150)
        right_speed_scale.grid(row=1, column=1, padx=5)
        
        def update_right_speed():
            self.motor_speeds["right"] = right_speed_var.get()
        
        right_speed_scale.configure(command=lambda x: update_right_speed())
        
        # 상태 표시
        status_frame = ttk.LabelFrame(control_frame, text="상태 정보", padding="5")
        status_frame.grid(row=5, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="대기 중...")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 버튼들
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=6, column=0, pady=10)
        
        ttk.Button(button_frame, text="시작", command=self.start_simulation).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="정지", command=self.stop_simulation).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="종료", command=self.quit_simulation).grid(row=0, column=2, padx=5)
        
        # 키보드 이벤트 바인딩
        self.root.bind('<KeyPress>', self.handle_keypress)
        self.root.bind('<KeyRelease>', self.handle_keyrelease)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=1)
    
    def handle_keypress(self, event):
        """키보드 입력 처리"""
        key = event.keysym.lower()
        
        if key == 'w':
            self.motor_speeds["left"] = 0.5
            self.motor_speeds["right"] = 0.5
        elif key == 's':
            self.motor_speeds["left"] = -0.5
            self.motor_speeds["right"] = -0.5
        elif key == 'a':
            self.motor_speeds["left"] = -0.3
            self.motor_speeds["right"] = 0.3
        elif key == 'd':
            self.motor_speeds["left"] = 0.3
            self.motor_speeds["right"] = -0.3
        elif key == 'space':
            self.motor_speeds["left"] = 0
            self.motor_speeds["right"] = 0
    
    def handle_keyrelease(self, event):
        """키보드 해제 처리"""
        key = event.keysym.lower()
        
        if key in ['w', 's', 'a', 'd']:
            self.motor_speeds["left"] = 0
            self.motor_speeds["right"] = 0
    
    def update_status(self):
        """상태 업데이트"""
        status_text = f"모드: {self.current_mode}\n"
        status_text += f"좌측 모터: {self.motor_speeds['left']:.2f}\n"
        status_text += f"우측 모터: {self.motor_speeds['right']:.2f}\n"
        status_text += f"카메라 Pan: {self.camera_position['pan']}\n"
        status_text += f"카메라 Tilt: {self.camera_position['tilt']}"
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text)
    
    def update_video(self):
        """비디오 업데이트"""
        if self.camera is None or not self.is_running:
            return
        
        ret, frame = self.camera.read()
        if not ret:
            return
        
        # 모드에 따른 처리
        if self.current_mode == "lane":
            frame = self.detect_lanes(frame)
        elif self.current_mode == "face":
            frame = self.detect_faces(frame)
        
        # 모터 상태 표시
        cv2.putText(frame, f"Left: {self.motor_speeds['left']:.2f}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Right: {self.motor_speeds['right']:.2f}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Mode: {self.current_mode}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # OpenCV 이미지를 Tkinter용으로 변환
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (640, 480))
        
        # PIL 이미지로 변환
        from PIL import Image, ImageTk
        image = Image.fromarray(frame_resized)
        photo = ImageTk.PhotoImage(image)
        
        if hasattr(self, 'video_label'):
            self.video_label.configure(image=photo)
            self.video_label.image = photo
        
        # 상태 업데이트
        self.update_status()
        
        # 다음 프레임 예약
        if self.is_running:
            self.root.after(30, self.update_video)  # 약 30 FPS
    
    def start_simulation(self):
        """시뮬레이션 시작"""
        if not self.is_running:
            self.is_running = True
            self.update_video()
            print("✅ 시뮬레이션 시작")
    
    def stop_simulation(self):
        """시뮬레이션 정지"""
        self.is_running = False
        self.motor_speeds["left"] = 0
        self.motor_speeds["right"] = 0
        print("⏹️ 시뮬레이션 정지")
    
    def quit_simulation(self):
        """시뮬레이션 종료"""
        self.stop_simulation()
        if self.camera:
            self.camera.release()
        if self.root:
            self.root.quit()
        print("👋 시뮬레이션 종료")
    
    def run(self):
        """메인 실행 함수"""
        print("🚀 윈도우용 JetBot 시뮬레이션 시작")
        
        # 카메라 초기화
        if not self.initialize_camera():
            print("❌ 카메라 초기화 실패. 시뮬레이션 모드로 실행합니다.")
        
        # GUI 생성
        self.create_gui()
        
        # GUI 실행
        if self.root:
            self.root.mainloop()

def main():
    """메인 함수"""
    print("=" * 60)
    print("윈도우용 JetBot 시뮬레이션 시스템")
    print("=" * 60)
    print("키 조작:")
    print("W: 전진, S: 후진, A: 좌회전, D: 우회전")
    print("Space: 정지")
    print("=" * 60)
    
    jetbot = WindowsJetBot()
    jetbot.run()

if __name__ == "__main__":
    main() 