#!/usr/bin/env python3
"""
제스처 보안 시스템 데모

RTSP 카메라를 통해 제스처 인식으로 잠금을 해제하는 데모 프로그램입니다.
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import argparse
import sys
from collections import deque

# 프로젝트 모듈
from gesture_security import GestureSecurity, SecurityState, AuthResult
import config


class SecurityDemo:
    """보안 시스템 데모 클래스"""

    def __init__(self, rtsp_url=None, simulation_mode=False):
        """
        초기화

        Args:
            rtsp_url: RTSP 스트림 URL (None이면 config 사용)
            simulation_mode: 시뮬레이션 모드
        """
        print("🔐 제스처 보안 시스템 데모 초기화 중...\n")

        self.rtsp_url = rtsp_url or config.RTSP_URL
        self.simulation_mode = simulation_mode

        # 설정 로드
        device_config = config.DEVICE_PRESETS.get(config.CURRENT_DEVICE, config.DEVICE_PRESETS['raspberry_pi_4'])
        self.frame_width = device_config['frame_width']
        self.frame_height = device_config['frame_height']
        self.target_fps = device_config['fps']

        # MediaPipe 초기화
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # 보안을 위해 한 손만
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
            model_complexity=device_config['model_complexity']
        )

        # 보안 시스템 초기화
        security_config = config.SECURITY_SETTINGS if hasattr(config, 'SECURITY_SETTINGS') else {}
        self.security = GestureSecurity(
            password_length=security_config.get('password_length', 4),
            max_attempts=security_config.get('max_attempts', 3),
            timeout_seconds=security_config.get('timeout_seconds', 10),
            lockout_duration=security_config.get('lockout_duration', 30)
        )

        # 비디오 캡처 초기화
        self.cap = self._initialize_capture()

        # FPS 계산
        self.fps_queue = deque(maxlen=30)
        self.last_time = time.time()

        # 제스처 히스토리 (중복 방지)
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # 초

        # 모드
        self.mode = "auth"  # "setup" 또는 "auth"
        self.setup_gestures = []

        print("✅ 초기화 완료!\n")

    def _initialize_capture(self):
        """비디오 캡처 초기화"""
        print(f"📹 RTSP 연결 시도: {self.rtsp_url}")

        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, config.BUFFER_SIZE)

        if not cap.isOpened():
            print("❌ RTSP 스트림 연결 실패!")
            raise ConnectionError("RTSP 연결 실패")

        print("✅ RTSP 스트림 연결 성공!")
        return cap

    def count_fingers(self, hand_landmarks, handedness="Right"):
        """손가락 개수 세기"""
        fingers = []

        # 엄지
        if handedness == 'Right':
            if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
                fingers.append(1)
            else:
                fingers.append(0)

        # 나머지 손가락
        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]

        for tip, pip in zip(tip_ids, pip_ids):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return sum(fingers)

    def recognize_gesture(self, hand_landmarks, finger_count):
        """제스처 인식"""
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.append([lm.x, lm.y, lm.z])

        landmarks = np.array(landmarks)

        # 손가락 끝 위치
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        wrist = landmarks[0]
        index_mcp = landmarks[5]

        # 제스처 분류
        if finger_count == 0:
            return "FIST", 0.95
        elif finger_count == 5:
            return "OPEN_PALM", 0.95
        elif finger_count == 1:
            if thumb_tip[1] < wrist[1]:
                return "THUMBS_UP", 0.90
            elif index_tip[1] < wrist[1]:
                return "POINTING", 0.85
            return "ONE_FINGER", 0.80
        elif finger_count == 2:
            if (index_tip[1] < wrist[1] and middle_tip[1] < wrist[1] and ring_tip[1] > index_mcp[1]):
                return "V_SIGN", 0.90
            return "TWO_FINGERS", 0.85
        elif finger_count == 3:
            thumb_index_dist = np.linalg.norm(thumb_tip[:2] - index_tip[:2])
            if thumb_index_dist < 0.05:
                return "OK_SIGN", 0.85
            return "THREE_FINGERS", 0.80
        elif finger_count == 4:
            return "FOUR_FINGERS", 0.80

        return "UNKNOWN", 0.0

    def calculate_fps(self):
        """FPS 계산"""
        current_time = time.time()
        fps = 1.0 / (current_time - self.last_time)
        self.last_time = current_time
        self.fps_queue.append(fps)
        return np.mean(self.fps_queue)

    def draw_ui(self, frame, gesture_info):
        """UI 그리기"""
        h, w, _ = frame.shape

        status = self.security.get_status()
        state = status['state']

        # 배경색 결정
        if state == 'unlocked':
            bg_color = (0, 100, 0)  # 초록색
        elif state == 'auth_mode':
            bg_color = (100, 100, 0)  # 노란색
        else:
            bg_color = (0, 0, 100)  # 빨간색

        # 반투명 배경 (상단)
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 200), bg_color, -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # 상태 아이콘
        state_icon = "🔓" if state == 'unlocked' else "🔒" if state == 'locked' else "🔐"
        state_text = state_icon + " " + state.upper().replace('_', ' ')

        cv2.putText(frame, state_text, (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

        # FPS
        fps = self.calculate_fps()
        cv2.putText(frame, f"FPS: {fps:.1f}", (w - 150, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # 모드 표시
        mode_text = "SETUP MODE" if self.mode == "setup" else "AUTH MODE"
        cv2.putText(frame, mode_text, (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # 제스처 정보
        if gesture_info:
            cv2.putText(frame, f"Gesture: {gesture_info['gesture']}", (10, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Fingers: {gesture_info['finger_count']}", (10, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # 진행 상황
        if state == 'auth_mode':
            progress = f"{status['input_progress']}/{status['password_length']}"
            timeout = status.get('timeout_remaining', 0)

            cv2.putText(frame, f"Progress: {progress}", (w - 250, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Timeout: {timeout}s", (w - 250, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # 실패 횟수
        if status['failed_attempts'] > 0:
            remaining = status['max_attempts'] - status['failed_attempts']
            cv2.putText(frame, f"Attempts: {remaining}/{status['max_attempts']}", (w - 250, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # 잠금 상태
        if status.get('is_locked_out'):
            lockout = status.get('lockout_remaining', 0)
            cv2.putText(frame, f"LOCKED: {lockout}s", (w // 2 - 100, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)

        # 설정 모드
        if self.mode == "setup":
            setup_progress = f"{len(self.setup_gestures)}/{self.security.password_length}"
            cv2.putText(frame, f"Setup: {setup_progress}", (10, h - 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            # 입력된 제스처 표시
            if self.setup_gestures:
                gestures_str = " → ".join(self.setup_gestures)
                cv2.putText(frame, gestures_str, (10, h - 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # 도움말
        help_text = "[A]uth | [S]etup | [R]eset | [L]ogs | [Q]uit"
        cv2.putText(frame, help_text, (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    def process_gesture(self, gesture):
        """
        제스처 처리

        Args:
            gesture: 인식된 제스처
        """
        # 쿨다운 체크
        current_time = time.time()
        if gesture == self.last_gesture:
            if current_time - self.last_gesture_time < self.gesture_cooldown:
                return

        self.last_gesture = gesture
        self.last_gesture_time = current_time

        # 모드에 따라 처리
        if self.mode == "setup":
            self._handle_setup_gesture(gesture)
        elif self.mode == "auth":
            self._handle_auth_gesture(gesture)

    def _handle_setup_gesture(self, gesture):
        """설정 모드에서 제스처 처리"""
        if gesture in self.security.valid_gestures:
            self.setup_gestures.append(gesture)
            print(f"   제스처 추가: {gesture} ({len(self.setup_gestures)}/{self.security.password_length})")

            # 비밀번호 길이에 도달하면 저장
            if len(self.setup_gestures) >= self.security.password_length:
                if self.security.setup_password(self.setup_gestures):
                    print("\n✅ 비밀번호 설정 완료!")
                    self.mode = "auth"
                    self.setup_gestures = []
                else:
                    print("\n❌ 비밀번호 설정 실패!")
                    self.setup_gestures = []

    def _handle_auth_gesture(self, gesture):
        """인증 모드에서 제스처 처리"""
        if self.security.state == SecurityState.AUTH_MODE:
            result = self.security.add_gesture(gesture)

            if result == AuthResult.SUCCESS:
                print("\n🎉 잠금 해제 성공!")
                print("   5초 후 자동으로 다시 잠깁니다.")
                time.sleep(5)
                self.security.lock()

            elif result == AuthResult.FAILED:
                print("\n❌ 인증 실패!")

            elif result == AuthResult.TIMEOUT:
                print("\n⏱️  시간 초과!")

    def run(self):
        """메인 루프"""
        print("\n" + "=" * 60)
        print("🔐 제스처 보안 시스템 데모 시작!")
        print("=" * 60)

        if not self.security.password_hash:
            print("\n⚠️  비밀번호가 설정되지 않았습니다.")
            print("   [S] 키를 눌러 설정 모드로 진입하세요.\n")

        print("키보드 단축키:")
        print("  [A] - 인증 시작")
        print("  [S] - 비밀번호 설정 모드")
        print("  [R] - 비밀번호 초기화")
        print("  [L] - 로그 보기")
        print("  [Q] - 종료\n")

        frame_duration = 1.0 / self.target_fps

        try:
            while True:
                start_time = time.time()

                # 프레임 읽기
                ret, frame = self.cap.read()

                if not ret:
                    print("프레임 수신 실패. 재연결 시도...")
                    self.cap.release()
                    time.sleep(1)
                    self.cap = self._initialize_capture()
                    continue

                # 리사이징
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))

                # RGB 변환
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # 손 검출
                results = self.hands.process(rgb_frame)

                gesture_info = None

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # 랜드마크 그리기
                        self.mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                            self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                        )

                        # 손가락 개수
                        finger_count = self.count_fingers(hand_landmarks)

                        # 제스처 인식
                        gesture, confidence = self.recognize_gesture(hand_landmarks, finger_count)

                        gesture_info = {
                            'gesture': gesture,
                            'finger_count': finger_count,
                            'confidence': confidence
                        }

                        # 제스처 처리
                        if gesture != "UNKNOWN":
                            self.process_gesture(gesture)

                # UI 그리기
                self.draw_ui(frame, gesture_info)

                # 화면 표시
                cv2.imshow('Gesture Security Demo', frame)

                # 키보드 입력 처리
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    break

                elif key == ord('a'):
                    # 인증 시작
                    self.mode = "auth"
                    self.security.start_authentication()

                elif key == ord('s'):
                    # 설정 모드
                    self.mode = "setup"
                    self.setup_gestures = []
                    print(f"\n📝 설정 모드: {self.security.password_length}개의 제스처를 입력하세요.")

                elif key == ord('r'):
                    # 비밀번호 초기화
                    self.security.reset_password()

                elif key == ord('l'):
                    # 로그 보기
                    self.security.print_logs()

                # FPS 제한
                elapsed_time = time.time() - start_time
                sleep_time = frame_duration - elapsed_time
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n\n사용자 중단")

        finally:
            self.cleanup()

    def cleanup(self):
        """리소스 정리"""
        print("\n\n🧹 정리 중...")
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()
        print("✅ 종료 완료")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='제스처 보안 시스템 데모')
    parser.add_argument('--rtsp', type=str, help='RTSP 스트림 URL')
    parser.add_argument('--sim', action='store_true', help='시뮬레이션 모드')
    parser.add_argument('--device', type=str, choices=['raspberry_pi_3', 'raspberry_pi_4', 'raspberry_pi_zero'],
                        help='라즈베리파이 모델')

    args = parser.parse_args()

    # 디바이스 설정 변경
    if args.device:
        config.CURRENT_DEVICE = args.device

    try:
        demo = SecurityDemo(rtsp_url=args.rtsp, simulation_mode=args.sim)
        demo.run()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
