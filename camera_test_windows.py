#!/usr/bin/env python3
"""
윈도우용 카메라 테스트 스크립트
카메라 연결, 로테이션, 이미지 처리 기능 테스트
"""

import cv2
import numpy as np
import time
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading

class CameraTestApp:
    """카메라 테스트 GUI 애플리케이션"""
    
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.rotation_angle = 0
        self.current_filter = "None"
        self.brightness = 0
        self.contrast = 1.0
        self.blur_level = 0
        self.edge_threshold = 50
        
        # GUI 변수
        self.root = None
        self.video_label = None
        self.status_label = None
        
        # 이미지 처리 옵션
        self.filters = {
            "None": self.no_filter,
            "Grayscale": self.grayscale_filter,
            "Blur": self.blur_filter,
            "Edge Detection": self.edge_detection_filter,
            "Canny Edge": self.canny_edge_filter,
            "Gaussian Blur": self.gaussian_blur_filter,
            "Median Blur": self.median_blur_filter,
            "Bilateral Filter": self.bilateral_filter,
            "Sharpen": self.sharpen_filter,
            "Emboss": self.emboss_filter,
            "Sepia": self.sepia_filter,
            "Negative": self.negative_filter,
            "Cartoon": self.cartoon_filter,
            "Oil Painting": self.oil_painting_filter,
            "Sketch": self.sketch_filter
        }
        
        print("📷 고급 카메라 테스트 시스템 초기화 완료")
    
    def initialize_camera(self):
        """카메라 초기화"""
        try:
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
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
    
    def no_filter(self, frame):
        """필터 없음"""
        return frame
    
    def grayscale_filter(self, frame):
        """그레이스케일 필터"""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    def blur_filter(self, frame):
        """블러 필터"""
        if self.blur_level > 0:
            kernel_size = self.blur_level * 2 + 1
            return cv2.blur(frame, (kernel_size, kernel_size))
        return frame
    
    def edge_detection_filter(self, frame):
        """엣지 검출 필터"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Laplacian(gray, cv2.CV_64F)
        edges = np.uint8(np.absolute(edges))
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    def canny_edge_filter(self, frame):
        """Canny 엣지 검출 필터"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, self.edge_threshold, self.edge_threshold * 2)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    def gaussian_blur_filter(self, frame):
        """가우시안 블러 필터"""
        if self.blur_level > 0:
            kernel_size = self.blur_level * 2 + 1
            return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        return frame
    
    def median_blur_filter(self, frame):
        """미디안 블러 필터"""
        if self.blur_level > 0:
            kernel_size = self.blur_level * 2 + 1
            return cv2.medianBlur(frame, kernel_size)
        return frame
    
    def bilateral_filter(self, frame):
        """양방향 필터"""
        if self.blur_level > 0:
            return cv2.bilateralFilter(frame, 9, 75, 75)
        return frame
    
    def sharpen_filter(self, frame):
        """샤프닝 필터"""
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        return cv2.filter2D(frame, -1, kernel)
    
    def emboss_filter(self, frame):
        """엠보스 필터"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kernel = np.array([[0,-1,-1], [1,0,-1], [1,1,0]])
        emboss = cv2.filter2D(gray, -1, kernel) + 128
        return cv2.cvtColor(emboss, cv2.COLOR_GRAY2BGR)
    
    def sepia_filter(self, frame):
        """세피아 필터"""
        sepia_matrix = np.array([[0.393, 0.769, 0.189],
                                [0.349, 0.686, 0.168],
                                [0.272, 0.534, 0.131]])
        sepia = cv2.transform(frame, sepia_matrix)
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)
        return sepia
    
    def negative_filter(self, frame):
        """네거티브 필터"""
        return 255 - frame
    
    def cartoon_filter(self, frame):
        """카툰 필터"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(frame, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        return cartoon
    
    def oil_painting_filter(self, frame):
        """유화 필터"""
        return cv2.xphoto.oilPainting(frame, 7, 1)
    
    def sketch_filter(self, frame):
        """스케치 필터"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    def apply_brightness_contrast(self, frame):
        """밝기와 대비 조정"""
        adjusted = cv2.convertScaleAbs(frame, alpha=self.contrast, beta=self.brightness)
        return adjusted
    
    def rotate_image(self, frame, angle):
        """이미지 회전"""
        if angle == 0:
            return frame
        
        height, width = frame.shape[:2]
        center = (width // 2, height // 2)
        
        # 회전 행렬 생성
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 회전된 이미지 크기 계산
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        
        # 이동 조정
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]
        
        # 이미지 회전
        rotated = cv2.warpAffine(frame, rotation_matrix, (new_width, new_height))
        
        # 원본 크기로 리사이즈
        resized = cv2.resize(rotated, (width, height))
        return resized
    
    def process_frame(self, frame):
        """프레임 처리"""
        # 밝기/대비 조정
        if self.brightness != 0 or self.contrast != 1.0:
            frame = self.apply_brightness_contrast(frame)
        
        # 필터 적용
        if self.current_filter in self.filters:
            frame = self.filters[self.current_filter](frame)
        
        # 회전 적용
        if self.rotation_angle != 0:
            frame = self.rotate_image(frame, self.rotation_angle)
        
        return frame
    
    def create_gui(self):
        """GUI 생성"""
        self.root = tk.Tk()
        self.root.title("고급 카메라 테스트 시스템")
        self.root.geometry("1200x800")
        
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
        
        # 카메라 제어
        camera_frame = ttk.LabelFrame(control_frame, text="카메라 제어", padding="5")
        camera_frame.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(camera_frame, text="카메라 시작", command=self.start_camera).grid(row=0, column=0, padx=5, pady=2)
        ttk.Button(camera_frame, text="카메라 정지", command=self.stop_camera).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(camera_frame, text="스냅샷 저장", command=self.save_snapshot).grid(row=0, column=2, padx=5, pady=2)
        
        # 회전 제어
        rotation_frame = ttk.LabelFrame(control_frame, text="회전 제어", padding="5")
        rotation_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(rotation_frame, text="90° 회전", command=lambda: self.set_rotation(90)).grid(row=0, column=0, padx=5, pady=2)
        ttk.Button(rotation_frame, text="180° 회전", command=lambda: self.set_rotation(180)).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(rotation_frame, text="270° 회전", command=lambda: self.set_rotation(270)).grid(row=0, column=2, padx=5, pady=2)
        ttk.Button(rotation_frame, text="원본", command=lambda: self.set_rotation(0)).grid(row=0, column=3, padx=5, pady=2)
        
        # 필터 선택
        filter_frame = ttk.LabelFrame(control_frame, text="이미지 필터", padding="5")
        filter_frame.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        filter_var = tk.StringVar(value="None")
        filter_combo = ttk.Combobox(filter_frame, textvariable=filter_var, values=list(self.filters.keys()), state="readonly")
        filter_combo.grid(row=0, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.set_filter(filter_var.get()))
        
        # 밝기/대비 제어
        brightness_frame = ttk.LabelFrame(control_frame, text="밝기/대비", padding="5")
        brightness_frame.grid(row=3, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(brightness_frame, text="밝기:").grid(row=0, column=0, sticky=tk.W)
        brightness_scale = ttk.Scale(brightness_frame, from_=-100, to=100, orient=tk.HORIZONTAL, length=150)
        brightness_scale.grid(row=0, column=1, padx=5)
        brightness_scale.configure(command=lambda x: self.set_brightness(int(x)))
        
        ttk.Label(brightness_frame, text="대비:").grid(row=1, column=0, sticky=tk.W)
        contrast_scale = ttk.Scale(brightness_frame, from_=0.1, to=3.0, orient=tk.HORIZONTAL, length=150)
        contrast_scale.grid(row=1, column=1, padx=5)
        contrast_scale.configure(command=lambda x: self.set_contrast(float(x)))
        
        # 블러 제어
        blur_frame = ttk.LabelFrame(control_frame, text="블러 강도", padding="5")
        blur_frame.grid(row=4, column=0, pady=5, sticky=(tk.W, tk.E))
        
        blur_scale = ttk.Scale(blur_frame, from_=0, to=10, orient=tk.HORIZONTAL, length=150)
        blur_scale.grid(row=0, column=0, padx=5)
        blur_scale.configure(command=lambda x: self.set_blur(int(x)))
        
        # 엣지 검출 임계값
        edge_frame = ttk.LabelFrame(control_frame, text="엣지 임계값", padding="5")
        edge_frame.grid(row=5, column=0, pady=5, sticky=(tk.W, tk.E))
        
        edge_scale = ttk.Scale(edge_frame, from_=10, to=200, orient=tk.HORIZONTAL, length=150)
        edge_scale.grid(row=0, column=0, padx=5)
        edge_scale.configure(command=lambda x: self.set_edge_threshold(int(x)))
        
        # 상태 표시
        status_frame = ttk.LabelFrame(control_frame, text="상태 정보", padding="5")
        status_frame.grid(row=6, column=0, pady=5, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="대기 중...")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=1)
        control_frame.columnconfigure(0, weight=1)
    
    def set_rotation(self, angle):
        """회전 각도 설정"""
        self.rotation_angle = angle
        self.update_status()
    
    def set_filter(self, filter_name):
        """필터 설정"""
        self.current_filter = filter_name
        self.update_status()
    
    def set_brightness(self, value):
        """밝기 설정"""
        self.brightness = value
        self.update_status()
    
    def set_contrast(self, value):
        """대비 설정"""
        self.contrast = value
        self.update_status()
    
    def set_blur(self, value):
        """블러 강도 설정"""
        self.blur_level = value
        self.update_status()
    
    def set_edge_threshold(self, value):
        """엣지 임계값 설정"""
        self.edge_threshold = value
        self.update_status()
    
    def update_status(self):
        """상태 업데이트"""
        status_text = f"필터: {self.current_filter}\n"
        status_text += f"회전: {self.rotation_angle}°\n"
        status_text += f"밝기: {self.brightness}\n"
        status_text += f"대비: {self.contrast:.1f}\n"
        status_text += f"블러: {self.blur_level}\n"
        status_text += f"엣지 임계값: {self.edge_threshold}"
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text)
    
    def start_camera(self):
        """카메라 시작"""
        if not self.is_running:
            self.is_running = True
            self.update_video()
            print("✅ 카메라 시작")
    
    def stop_camera(self):
        """카메라 정지"""
        self.is_running = False
        print("⏹️ 카메라 정지")
    
    def save_snapshot(self):
        """스냅샷 저장"""
        if self.current_frame is not None:
            filename = f"snapshot_{int(time.time())}.jpg"
            cv2.imwrite(filename, self.current_frame)
            print(f"📸 스냅샷 저장: {filename}")
            messagebox.showinfo("스냅샷", f"스냅샷이 저장되었습니다: {filename}")
    
    def update_video(self):
        """비디오 업데이트"""
        if self.camera is None or not self.is_running:
            return
        
        ret, frame = self.camera.read()
        if not ret:
            return
        
        # 프레임 처리
        processed_frame = self.process_frame(frame)
        self.current_frame = processed_frame
        
        # 정보 표시
        cv2.putText(processed_frame, f"Filter: {self.current_filter}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(processed_frame, f"Rotation: {self.rotation_angle}°", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(processed_frame, f"Brightness: {self.brightness}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # OpenCV 이미지를 Tkinter용으로 변환
        frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (640, 480))
        
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
    
    def run(self):
        """메인 실행 함수"""
        print("🚀 고급 카메라 테스트 시스템 시작")
        
        # 카메라 초기화
        if not self.initialize_camera():
            print("❌ 카메라 초기화 실패.")
            return
        
        # GUI 생성
        self.create_gui()
        
        # GUI 실행
        if self.root:
            self.root.mainloop()
        
        # 정리
        if self.camera:
            self.camera.release()

def main():
    """메인 함수"""
    print("=" * 60)
    print("고급 카메라 테스트 시스템")
    print("=" * 60)
    print("기능:")
    print("- 실시간 카메라 영상")
    print("- 이미지 회전 (90°, 180°, 270°)")
    print("- 다양한 이미지 필터 (15가지)")
    print("- 밝기/대비 조정")
    print("- 블러 효과")
    print("- 엣지 검출")
    print("- 스냅샷 저장")
    print("=" * 60)
    
    app = CameraTestApp()
    app.run()

if __name__ == "__main__":
    main() 