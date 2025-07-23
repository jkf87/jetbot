#!/usr/bin/env python3
"""
JetBot C100 보드용 SLM(Small Language Model) 연동 예제
Jetson Nano에서 실행 가능한 경량 AI 모델을 활용한 로봇 제어
"""

import cv2
import numpy as np
import time
import json
import os
import sys
import base64
from io import BytesIO

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("Warning: requests not available, using mock mode")
    REQUESTS_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    print("Warning: PIL not available, using OpenCV only")
    PIL_AVAILABLE = False

from camera_test import JetBotCamera
from jetbot_hardware import JetBotController

class VisionLanguageModel:
    """비전-언어 모델 인터페이스"""
    
    def __init__(self, model_type="local"):
        self.model_type = model_type
        self.base_url = "http://localhost:11434"  # Ollama 기본 URL
        
        # 사전 정의된 명령어 매핑
        self.command_mapping = {
            "forward": "전진",
            "backward": "후진", 
            "left": "좌회전",
            "right": "우회전",
            "stop": "정지",
            "explore": "탐색",
            "patrol": "순찰"
        }
        
        # 객체 검출 라벨 (COCO 데이터셋 기반)
        self.coco_labels = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
            'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
            'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
            'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
            'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
            'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
    
    def encode_image_to_base64(self, image):
        """이미지를 base64로 인코딩"""
        if PIL_AVAILABLE:
            # PIL 사용
            if isinstance(image, np.ndarray):
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            buffer = BytesIO()
            pil_image.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode()
        else:
            # OpenCV 사용
            _, buffer = cv2.imencode('.jpg', image)
            return base64.b64encode(buffer).decode()
    
    def analyze_scene(self, image, prompt="이 이미지에서 무엇을 볼 수 있나요?"):
        """장면 분석"""
        if self.model_type == "local":
            return self._analyze_local(image, prompt)
        elif self.model_type == "mock":
            return self._analyze_mock(image, prompt)
        else:
            return {"error": "Unknown model type"}
    
    def _analyze_local(self, image, prompt):
        """로컬 모델 분석 (Ollama 사용)"""
        if not REQUESTS_AVAILABLE:
            return self._analyze_mock(image, prompt)
        
        try:
            # 이미지 인코딩
            image_b64 = self.encode_image_to_base64(image)
            
            # Ollama API 호출
            payload = {
                "model": "llava",  # 또는 다른 vision 모델
                "prompt": prompt,
                "images": [image_b64],
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "description": result.get("response", "분석 결과 없음"),
                    "model": "llava"
                }
            else:
                return {"error": f"API 오류: {response.status_code}"}
                
        except Exception as e:
            print(f"로컬 모델 분석 실패: {e}")
            return self._analyze_mock(image, prompt)
    
    def _analyze_mock(self, image, prompt):
        """Mock 분석 (오프라인 모드)"""
        # 간단한 컴퓨터 비전 기반 분석
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 엣지 검출
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # 밝기 분석
        brightness = np.mean(gray)
        
        # 색상 분석
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        dominant_hue = np.median(hsv[:,:,0])
        
        # 간단한 규칙 기반 분석
        description = []
        
        if brightness < 50:
            description.append("어두운 환경")
        elif brightness > 200:
            description.append("밝은 환경")
        else:
            description.append("보통 밝기")
        
        if edge_density > 0.1:
            description.append("복잡한 구조물")
        else:
            description.append("단순한 배경")
        
        # 색상 분석
        if dominant_hue < 30 or dominant_hue > 150:
            description.append("따뜻한 색조")
        else:
            description.append("차가운 색조")
        
        return {
            "success": True,
            "description": ", ".join(description),
            "model": "mock_cv",
            "metrics": {
                "brightness": float(brightness),
                "edge_density": float(edge_density),
                "dominant_hue": float(dominant_hue)
            }
        }
    
    def generate_command(self, scene_description):
        """장면 분석 결과를 기반으로 로봇 명령 생성"""
        description = scene_description.get("description", "").lower()
        
        # 간단한 규칙 기반 명령 생성
        if "사람" in description or "person" in description:
            return {"action": "stop", "reason": "사람 감지"}
        elif "어두운" in description:
            return {"action": "slow", "reason": "저조도 환경"}
        elif "복잡한" in description:
            return {"action": "careful", "reason": "복잡한 환경"}
        elif "장애물" in description or "obstacle" in description:
            return {"action": "avoid", "reason": "장애물 감지"}
        else:
            return {"action": "forward", "reason": "안전한 전진"}

class IntelligentJetBot:
    """AI 기반 JetBot 제어 시스템"""
    
    def __init__(self, model_type="mock"):
        self.camera = JetBotCamera()
        self.controller = JetBotController()
        self.vlm = VisionLanguageModel(model_type)
        
        self.is_running = False
        self.analysis_interval = 2.0  # 2초마다 분석
        self.last_analysis_time = 0
        
        # 행동 이력
        self.action_history = []
        self.max_history = 10
    
    def initialize(self):
        """시스템 초기화"""
        print("AI JetBot 초기화 중...")
        
        if not self.camera.initialize():
            print("카메라 초기화 실패!")
            return False
        
        if not self.controller.initialize():
            print("하드웨어 초기화 실패!")
            return False
        
        print("AI JetBot 초기화 완료!")
        return True
    
    def analyze_and_act(self, frame):
        """프레임 분석 및 행동 결정"""
        current_time = time.time()
        
        # 분석 주기 확인
        if current_time - self.last_analysis_time < self.analysis_interval:
            return None
        
        # 장면 분석
        scene_analysis = self.vlm.analyze_scene(frame)
        
        if scene_analysis.get("success"):
            # 명령 생성
            command = self.vlm.generate_command(scene_analysis)
            
            # 행동 실행
            self.execute_command(command)
            
            # 이력 업데이트
            self.action_history.append({
                "time": current_time,
                "analysis": scene_analysis,
                "command": command
            })
            
            # 이력 크기 제한
            if len(self.action_history) > self.max_history:
                self.action_history.pop(0)
            
            self.last_analysis_time = current_time
            
            return {
                "analysis": scene_analysis,
                "command": command
            }
        
        return None
    
    def execute_command(self, command):
        """명령 실행"""
        action = command.get("action", "stop")
        
        if action == "forward":
            self.controller.move(0.3, 0)
        elif action == "backward":
            self.controller.move(-0.3, 0)
        elif action == "left":
            self.controller.move(0, -0.5)
        elif action == "right":
            self.controller.move(0, 0.5)
        elif action == "stop":
            self.controller.move(0, 0)
        elif action == "slow":
            self.controller.move(0.1, 0)
        elif action == "careful":
            self.controller.move(0.2, 0)
        elif action == "avoid":
            # 간단한 회피 행동
            self.controller.move(-0.2, 0.3)
        
        print(f"실행: {action} - {command.get('reason', '이유 없음')}")
    
    def run_autonomous_mode(self):
        """자율 주행 모드"""
        print("=== AI 자율 주행 모드 ===")
        print("ESC 키로 종료, 's' 키로 일시정지")
        
        self.controller.start()
        self.is_running = True
        
        try:
            while self.is_running:
                ret, frame = self.camera.read_frame()
                
                if not ret:
                    continue
                
                # AI 분석 및 행동
                result = self.analyze_and_act(frame)
                
                # 디버그 정보 표시
                self._display_ai_info(frame, result)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                elif key == ord('s'):  # 일시정지
                    self.controller.move(0, 0)
                    print("일시 정지 - 아무 키나 누르면 재개")
                    cv2.waitKey(0)
        
        except KeyboardInterrupt:
            print("사용자에 의해 중단됨")
        
        finally:
            self.cleanup()
    
    def interactive_mode(self):
        """대화형 모드"""
        print("=== AI 대화형 모드 ===")
        print("카메라 이미지를 보고 질문하세요")
        
        try:
            while True:
                ret, frame = self.camera.read_frame()
                
                if ret:
                    cv2.imshow('AI JetBot Camera', frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord(' '):  # 스페이스바로 분석
                        prompt = input("질문을 입력하세요 (또는 Enter로 기본 분석): ")
                        if not prompt.strip():
                            prompt = "이 이미지에서 무엇을 볼 수 있나요?"
                        
                        print("분석 중...")
                        result = self.vlm.analyze_scene(frame, prompt)
                        
                        print(f"분석 결과: {result.get('description', '분석 실패')}")
                        
                        if result.get("success"):
                            command = self.vlm.generate_command(result)
                            print(f"추천 행동: {command.get('action')} - {command.get('reason')}")
                            
                            execute = input("이 행동을 실행하시겠습니까? (y/n): ")
                            if execute.lower() == 'y':
                                self.execute_command(command)
                                time.sleep(2)
                                self.controller.move(0, 0)  # 정지
        
        except KeyboardInterrupt:
            print("사용자에 의해 중단됨")
        
        finally:
            cv2.destroyAllWindows()
    
    def _display_ai_info(self, frame, result):
        """AI 정보 표시"""
        info_frame = frame.copy()
        
        # 기본 정보
        cv2.putText(info_frame, "AI JetBot", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if result:
            analysis = result.get("analysis", {})
            command = result.get("command", {})
            
            # 분석 결과
            description = analysis.get("description", "분석 중...")
            if len(description) > 50:
                description = description[:50] + "..."
            
            cv2.putText(info_frame, f"Scene: {description}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # 현재 행동
            action = command.get("action", "대기")
            reason = command.get("reason", "")
            cv2.putText(info_frame, f"Action: {action}", (10, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(info_frame, f"Reason: {reason}", (10, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # 행동 이력
        if self.action_history:
            cv2.putText(info_frame, f"History: {len(self.action_history)} actions", 
                       (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        cv2.imshow('AI JetBot Control', info_frame)
    
    def cleanup(self):
        """리소스 정리"""
        self.is_running = False
        self.controller.cleanup()
        self.camera.release()
        cv2.destroyAllWindows()
        
        # 행동 이력 저장
        if self.action_history:
            self.save_history()
    
    def save_history(self):
        """행동 이력 저장"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"ai_history_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.action_history, f, ensure_ascii=False, indent=2)
            
            print(f"행동 이력 저장됨: {filename}")
        except Exception as e:
            print(f"이력 저장 실패: {e}")

def setup_ollama():
    """Ollama 설정 가이드"""
    print("=== Ollama 설정 가이드 ===")
    print("1. Ollama 설치:")
    print("   curl -fsSL https://ollama.ai/install.sh | sh")
    print("")
    print("2. Vision 모델 다운로드:")
    print("   ollama pull llava")
    print("")
    print("3. 서버 시작:")
    print("   ollama serve")
    print("")
    print("4. 모델 확인:")
    print("   ollama list")

def main():
    """메인 함수"""
    print("JetBot AI 통합 시스템")
    print("1. AI 자율 주행")
    print("2. AI 대화형 모드")
    print("3. Ollama 설정 가이드")
    print("4. Mock 모드 테스트")
    
    try:
        choice = input("선택하세요 (1-4): ").strip()
        
        if choice == "1":
            model_type = input("모델 타입 (local/mock) [mock]: ").strip() or "mock"
            jetbot = IntelligentJetBot(model_type)
            if jetbot.initialize():
                jetbot.run_autonomous_mode()
        
        elif choice == "2":
            model_type = input("모델 타입 (local/mock) [mock]: ").strip() or "mock"
            jetbot = IntelligentJetBot(model_type)
            if jetbot.initialize():
                jetbot.interactive_mode()
        
        elif choice == "3":
            setup_ollama()
        
        elif choice == "4":
            print("Mock 모드로 테스트 실행 중...")
            jetbot = IntelligentJetBot("mock")
            if jetbot.initialize():
                # 간단한 이미지로 테스트
                test_image = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.rectangle(test_image, (100, 100), (500, 300), (0, 255, 0), -1)
                
                result = jetbot.vlm.analyze_scene(test_image)
                print(f"테스트 분석 결과: {result}")
                
                command = jetbot.vlm.generate_command(result)
                print(f"생성된 명령: {command}")
        
        else:
            print("잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()