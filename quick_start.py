#!/usr/bin/env python3
"""
JetBot C100 보드 빠른 시작 가이드
Jetson Nano 4GB + C100 보드 환경에서 JetBot 시작하기
"""

import os
import sys
import subprocess
import time

def print_header(title):
    """헤더 출력"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step_num, title):
    """단계 출력"""
    print(f"\n[단계 {step_num}] {title}")
    print("-" * 40)

def run_command(command, description=""):
    """명령어 실행"""
    if description:
        print(f"실행 중: {description}")
    print(f"$ {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"오류: {e}")
        if e.stderr:
            print(f"에러 메시지: {e.stderr}")
        return False

def check_dependencies():
    """종속성 확인"""
    print_step(1, "시스템 종속성 확인")
    
    # Python 버전 확인
    python_version = sys.version
    print(f"Python 버전: {python_version}")
    
    # 필수 패키지 확인
    required_packages = ['cv2', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 설치됨")
        except ImportError:
            print(f"✗ {package} 누락")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n누락된 패키지: {', '.join(missing_packages)}")
        print("환경 설정 스크립트를 먼저 실행하세요.")
        return False
    
    return True

def setup_environment():
    """환경 설정"""
    print_step(2, "환경 설정 실행")
    
    setup_script = "./setup_jetbot_c100.sh"
    
    if not os.path.exists(setup_script):
        print(f"❌ 설정 스크립트를 찾을 수 없습니다: {setup_script}")
        return False
    
    print("환경 설정 스크립트를 실행하시겠습니까? (y/n)")
    choice = input().strip().lower()
    
    if choice == 'y':
        run_command(f"chmod +x {setup_script}", "실행 권한 부여")
        run_command(f"bash {setup_script}", "환경 설정 실행")
        
        print("\n⚠️  시스템 재부팅이 필요할 수 있습니다.")
        print("재부팅 후 다시 이 스크립트를 실행하세요.")
        
        reboot = input("지금 재부팅하시겠습니까? (y/n): ").strip().lower()
        if reboot == 'y':
            run_command("sudo reboot")
        
        return False  # 재부팅 필요
    
    return True

def test_camera():
    """카메라 테스트"""
    print_step(3, "카메라 테스트")
    
    print("카메라 테스트를 실행하시겠습니까? (y/n)")
    choice = input().strip().lower()
    
    if choice == 'y':
        print("카메라 테스트 실행 중...")
        print("ESC 키를 눌러 종료하세요.")
        time.sleep(2)
        
        return run_command("python3 camera_test.py", "카메라 테스트")
    
    return True

def test_hardware():
    """하드웨어 테스트"""
    print_step(4, "하드웨어 테스트")
    
    print("⚠️  모터가 연결되어 있고 안전한 곳에서 테스트하세요!")
    print("하드웨어 테스트를 실행하시겠습니까? (y/n)")
    choice = input().strip().lower()
    
    if choice == 'y':
        print("하드웨어 테스트 실행 중...")
        print("로봇이 움직일 수 있으니 주의하세요!")
        time.sleep(3)
        
        return run_command("python3 jetbot_hardware.py", "하드웨어 테스트")
    
    return True

def run_autonomous_driving():
    """자율주행 실행"""
    print_step(5, "자율주행 시스템 실행")
    
    print("자율주행을 시작하시겠습니까? (y/n)")
    choice = input().strip().lower()
    
    if choice == 'y':
        print("자율주행 시스템 시작 중...")
        print("ESC 키로 종료, 's' 키로 일시정지 가능합니다.")
        time.sleep(2)
        
        return run_command("python3 autonomous_driving.py", "자율주행 실행")
    
    return True

def show_advanced_options():
    """고급 옵션 표시"""
    print_step(6, "고급 기능")
    
    print("사용 가능한 고급 기능:")
    print("1. PTZ 카메라 제어 - python3 camera_ptz.py")
    print("2. AI 연동 시스템 - python3 slm_integration.py")
    print("3. 개별 컴포넌트 테스트")
    
    print("\n어떤 기능을 실행하시겠습니까? (1-3, 또는 skip)")
    choice = input().strip()
    
    if choice == "1":
        print("PTZ 카메라 제어 실행 중...")
        run_command("python3 camera_ptz.py", "PTZ 제어")
    elif choice == "2":
        print("AI 연동 시스템 실행 중...")
        run_command("python3 slm_integration.py", "AI 시스템")
    elif choice == "3":
        show_component_tests()

def show_component_tests():
    """컴포넌트 테스트 메뉴"""
    print("\n개별 컴포넌트 테스트:")
    print("1. 카메라만 테스트")
    print("2. 모터만 테스트") 
    print("3. 서보 모터 테스트")
    print("4. 종합 시스템 테스트")
    
    choice = input("선택하세요 (1-4): ").strip()
    
    if choice == "1":
        run_command("python3 -c \"from camera_test import test_camera_basic; test_camera_basic()\"")
    elif choice == "2":
        run_command("python3 -c \"from jetbot_hardware import test_hardware; test_hardware()\"")
    elif choice == "3":
        run_command("python3 -c \"from camera_ptz import servo_test; servo_test()\"")
    elif choice == "4":
        run_all_tests()

def run_all_tests():
    """모든 테스트 실행"""
    print("\n모든 테스트를 순차적으로 실행합니다...")
    
    tests = [
        ("카메라 테스트", "python3 camera_test.py"),
        ("하드웨어 테스트", "python3 jetbot_hardware.py"),
        ("PTZ 테스트", "python3 camera_ptz.py"),
    ]
    
    for test_name, command in tests:
        print(f"\n{test_name} 실행 중...")
        if not run_command(command):
            print(f"{test_name} 실패!")
            break
        time.sleep(2)

def show_troubleshooting():
    """문제 해결 가이드"""
    print_header("문제 해결 가이드")
    
    print("""
주요 문제 해결 방법:

1. 카메라가 작동하지 않는 경우:
   - CSI 카메라 연결 확인
   - 카메라 모듈이 활성화되어 있는지 확인
   - 권한 문제: sudo usermod -a -G video $USER

2. 모터가 작동하지 않는 경우:
   - 전원 공급 확인 (충분한 전류)
   - GPIO 핀 연결 확인
   - I2C 연결 확인 (PCA9685 사용 시)

3. 권한 오류가 발생하는 경우:
   - sudo usermod -a -G gpio $USER
   - 재로그인 또는 재부팅

4. Python 패키지 오류:
   - pip3 install --upgrade pip
   - 필요한 패키지 재설치

5. C100 보드 특이사항:
   - 핀 매핑이 B01과 다를 수 있음
   - jetbot_hardware.py에서 PIN_CONFIG 확인
   
6. 성능 최적화:
   - 불필요한 서비스 종료
   - 스왑 메모리 설정
   - GPU 메모리 할당 조정
""")

def main():
    """메인 함수"""
    print_header("JetBot C100 보드 빠른 시작 가이드")
    print("Jetson Nano 4GB + C100 보드 환경용")
    
    try:
        # 1. 종속성 확인
        if not check_dependencies():
            # 2. 환경 설정
            if not setup_environment():
                return
        
        # 3. 카메라 테스트
        if not test_camera():
            print("카메라 테스트에서 문제가 발생했습니다.")
        
        # 4. 하드웨어 테스트
        if not test_hardware():
            print("하드웨어 테스트에서 문제가 발생했습니다.")
        
        # 5. 자율주행 실행
        run_autonomous_driving()
        
        # 6. 고급 옵션
        show_advanced_options()
        
        print_header("설정 완료!")
        print("JetBot이 성공적으로 설정되었습니다.")
        print("\n다음 명령어로 각 기능을 실행할 수 있습니다:")
        print("- 자율주행: python3 autonomous_driving.py")
        print("- PTZ 제어: python3 camera_ptz.py")
        print("- AI 연동: python3 slm_integration.py")
        print("- 카메라 테스트: python3 camera_test.py")
        print("- 하드웨어 테스트: python3 jetbot_hardware.py")
        
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 설정이 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        show_troubleshooting()

if __name__ == "__main__":
    main()