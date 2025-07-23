#!/usr/bin/env python3
"""
JetBot C100 보드용 카메라 테스트 및 초기화 코드
Jetson Nano 4GB에서 CSI 카메라 테스트
"""

import cv2
import numpy as np
import time
import sys
import os

class JetBotCamera:
    def __init__(self, width=640, height=480, fps=30, camera_id=0):
        self.width = width
        self.height = height
        self.fps = fps
        self.camera_id = camera_id
        self.cap = None
        
    def initialize(self):
        """카메라 초기화"""
        try:
            # GStreamer 파이프라인으로 CSI 카메라 접근
            gst_pipeline = (
                f"nvarguscamerasrc sensor-id={self.camera_id} ! "
                f"video/x-raw(memory:NVMM), width=(int){self.width}, "
                f"height=(int){self.height}, framerate=(fraction){self.fps}/1 ! "
                f"nvvidconv flip-method=2 ! "
                f"video/x-raw, width=(int){self.width}, height=(int){self.height}, "
                f"format=(string)BGRx ! videoconvert ! "
                f"video/x-raw, format=(string)BGR ! appsink"
            )
            
            print(f"GStreamer 파이프라인으로 카메라 초기화 중... (ID: {self.camera_id})")
            self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
            
            if not self.cap.isOpened():
                print("GStreamer 실패, USB 카메라로 시도 중...")
                self.cap = cv2.VideoCapture(self.camera_id)
                
            if not self.cap.isOpened():
                raise Exception("카메라를 열 수 없습니다.")
                
            # 카메라 설정
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            print(f"카메라 초기화 성공! 해상도: {self.width}x{self.height}, FPS: {self.fps}")
            return True
            
        except Exception as e:
            print(f"카메라 초기화 실패: {e}")
            return False
            
    def read_frame(self):
        """프레임 읽기"""
        if self.cap is None:
            return None, None
            
        ret, frame = self.cap.read()
        if ret:
            return True, frame
        else:
            return False, None
            
    def release(self):
        """카메라 해제"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("카메라 해제됨")

def test_camera_basic():
    """기본 카메라 테스트"""
    print("=== 기본 카메라 테스트 시작 ===")
    
    camera = JetBotCamera()
    
    if not camera.initialize():
        print("카메라 초기화 실패!")
        return False
        
    print("5초간 카메라 피드 표시 (ESC 키로 종료)")
    
    start_time = time.time()
    frame_count = 0
    
    try:
        while True:
            ret, frame = camera.read_frame()
            
            if not ret:
                print("프레임 읽기 실패")
                break
                
            frame_count += 1
            
            # FPS 계산
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                fps = frame_count / elapsed_time
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 해상도 정보 표시
            cv2.putText(frame, f"Resolution: {frame.shape[1]}x{frame.shape[0]}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('JetBot Camera Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC 키
                break
                
            if elapsed_time > 5:  # 5초 후 자동 종료
                break
                
    except KeyboardInterrupt:
        print("사용자에 의해 종료됨")
        
    finally:
        camera.release()
        cv2.destroyAllWindows()
        
    print(f"테스트 완료! 총 {frame_count}프레임, 평균 FPS: {frame_count/elapsed_time:.1f}")
    return True

def test_image_processing():
    """이미지 처리 테스트"""
    print("=== 이미지 처리 테스트 시작 ===")
    
    camera = JetBotCamera()
    
    if not camera.initialize():
        print("카메라 초기화 실패!")
        return False
        
    print("이미지 처리 테스트 (ESC 키로 종료)")
    
    try:
        while True:
            ret, frame = camera.read_frame()
            
            if not ret:
                break
                
            # 그레이스케일 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 가우시안 블러
            blurred = cv2.GaussianBlur(gray, (15, 15), 0)
            
            # 엣지 검출
            edges = cv2.Canny(blurred, 50, 150)
            
            # 결과 합성
            result = np.hstack([
                cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
                cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR),
                frame
            ])
            
            # 라벨 추가
            cv2.putText(result, "Gray", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(result, "Edges", (gray.shape[1] + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(result, "Original", (gray.shape[1] * 2 + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Image Processing Test', result)
            
            if cv2.waitKey(1) & 0xFF == 27:  # ESC 키
                break
                
    except KeyboardInterrupt:
        print("사용자에 의해 종료됨")
        
    finally:
        camera.release()
        cv2.destroyAllWindows()
        
    print("이미지 처리 테스트 완료!")
    return True

def save_test_image():
    """테스트 이미지 저장"""
    print("=== 테스트 이미지 저장 ===")
    
    camera = JetBotCamera()
    
    if not camera.initialize():
        print("카메라 초기화 실패!")
        return False
        
    # 디렉토리 생성
    os.makedirs("test_images", exist_ok=True)
    
    print("3초 후 이미지 캡처...")
    time.sleep(3)
    
    ret, frame = camera.read_frame()
    
    if ret:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_images/jetbot_test_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"이미지 저장됨: {filename}")
        
        # 이미지 정보 출력
        print(f"이미지 크기: {frame.shape}")
        print(f"이미지 타입: {frame.dtype}")
        
    else:
        print("이미지 캡처 실패!")
        
    camera.release()
    return ret

def main():
    """메인 함수"""
    print("JetBot C100 카메라 테스트 프로그램")
    print("1. 기본 카메라 테스트")
    print("2. 이미지 처리 테스트")
    print("3. 테스트 이미지 저장")
    print("4. 모든 테스트 실행")
    
    try:
        choice = input("선택하세요 (1-4): ").strip()
        
        if choice == "1":
            test_camera_basic()
        elif choice == "2":
            test_image_processing()
        elif choice == "3":
            save_test_image()
        elif choice == "4":
            print("모든 테스트 실행 중...")
            test_camera_basic()
            time.sleep(1)
            test_image_processing()
            time.sleep(1)
            save_test_image()
        else:
            print("잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()