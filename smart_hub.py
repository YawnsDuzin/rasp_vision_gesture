#!/usr/bin/env python3
"""
스마트 홈 허브 - 통합 제스처 제어 시스템

RTSP 카메라를 통한 제스처 인식으로 스마트 홈과 음악 플레이어를 제어합니다.
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
import argparse
import sys

# 프로젝트 모듈
from smart_home_controller import SmartHomeController, DeviceType
from music_player_controller import MusicPlayerController
from gesture_actions import GestureActionMapper
import config


class SmartHub:
    """스마트 홈 허브 메인 클래스"""

    def __init__(self, rtsp_url=None, simulation_mode=False):
        """
        초기화

        Args:
            rtsp_url: RTSP 스트림 URL
            simulation_mode: 시뮬레이션 모드 (GPIO/pygame 없이 실행)
        """
        print("🏠 스마트 홈 허브 초기화 중...\n")

        self.rtsp_url = rtsp_url or config.RTSP_URL
        self.simulation_mode = simulation_mode

        # 설정 로드
        device_config = config.DEVICE_PRESETS[config.CURRENT_DEVICE]
        self.frame_width = device_config['frame_width']
        self.frame_height = device_config['frame_height']
        self.target_fps = device_config['fps']

        # MediaPipe 초기화
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=device_config['max_num_hands'],
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
            model_complexity=device_config['model_complexity']
        )

        # 스마트 홈 컨트롤러 초기화
        self.smart_home = SmartHomeController(simulation_mode=simulation_mode)
        self._setup_smart_home_devices()

        # 음악 플레이어 초기화
        self.music_player = MusicPlayerController(simulation_mode=simulation_mode)

        # 제스처 액션 매퍼 초기화
        self.gesture_mapper = GestureActionMapper(self.smart_home, self.music_player)

        # 비디오 캡처 초기화
        self.cap = self._initialize_capture()

        # FPS 계산용
        self.fps_queue = deque(maxlen=30)
        self.last_time = time.time()

        # 제스처 히스토리 (안정성)
        self.gesture_history = deque(maxlen=config.GESTURE_HOLD_FRAMES)

        # UI 표시 옵션
        self.show_help = True
        self.show_status = True

        print("✅ 스마트 홈 허브 초기화 완료!\n")

    def _setup_smart_home_devices(self):
        """스마트 홈 디바이스 설정"""
        print("🔌 스마트 홈 디바이스 설정 중...")

        # config.py에서 디바이스 설정 가져오기
        if hasattr(config, 'SMART_HOME_DEVICES'):
            for device_config in config.SMART_HOME_DEVICES:
                self.smart_home.add_device(
                    device_config['name'],
                    DeviceType[device_config['type']],
                    device_config['pin'],
                    device_config.get('initial_state', False)
                )
        else:
            # 기본 디바이스
            self.smart_home.add_device("거실 조명", DeviceType.LIGHT, pin=17)
            self.smart_home.add_device("침실 조명", DeviceType.LIGHT, pin=27)
            self.smart_home.add_device("선풍기", DeviceType.FAN, pin=22)
            self.smart_home.add_device("에어컨", DeviceType.AC, pin=23)

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

    def count_fingers(self, hand_landmarks, handedness):
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

    def draw_ui(self, frame, hand_info):
        """UI 그리기"""
        h, w, _ = frame.shape

        # 반투명 배경 (상단)
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # FPS 표시
        if config.SHOW_FPS:
            fps = self.calculate_fps()
            cv2.putText(frame, f"FPS: {fps:.1f}", (w - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # 타이틀
        cv2.putText(frame, "Smart Home Hub", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        # 손 정보 표시
        y_offset = 70
        for idx, info in enumerate(hand_info):
            hand_icon = "👈" if info['handedness'] == 'Left' else "👉"
            text = f"{hand_icon} {info['handedness']}: {info['gesture']} ({info['finger_count']})"
            cv2.putText(frame, text, (10, y_offset + idx * 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 상태 표시 (하단)
        if self.show_status:
            status_y = h - 100

            # 반투명 배경 (하단)
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, status_y - 10), (w, h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            # 스마트 홈 상태
            smart_status = self.smart_home.get_status()
            on_count = sum(1 for device in smart_status.values() if device['state'])
            cv2.putText(frame, f"Home: {on_count}/{len(smart_status)} ON", (10, status_y + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)

            # 음악 플레이어 상태
            music_status = self.music_player.get_status()
            music_icon = "▶️" if music_status['state'] == 'playing' else "⏸️" if music_status['state'] == 'paused' else "⏹️"
            cv2.putText(frame, f"Music {music_icon}: Vol {music_status['volume']}%", (10, status_y + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 100), 2)

        # 도움말 표시
        if self.show_help:
            help_text = "Press: [H]elp | [S]tatus | [Q]uit"
            cv2.putText(frame, help_text, (10, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    def process_frame(self, frame):
        """프레임 처리"""
        # 리사이징
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))

        # RGB 변환
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 손 검출
        results = self.hands.process(rgb_frame)

        hand_info = []

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 랜드마크 그리기
                if config.SHOW_LANDMARKS:
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )

                # 손 방향
                handedness = results.multi_handedness[idx].classification[0].label

                # 손가락 개수
                finger_count = self.count_fingers(hand_landmarks, handedness)

                # 제스처 인식
                gesture, confidence = self.recognize_gesture(hand_landmarks, finger_count)

                # 액션 실행
                self.gesture_mapper.execute_action(handedness, gesture)

                hand_info.append({
                    'handedness': handedness,
                    'finger_count': finger_count,
                    'gesture': gesture,
                    'confidence': confidence
                })

        # UI 그리기
        self.draw_ui(frame, hand_info)

        return frame, hand_info

    def run(self):
        """메인 루프"""
        print("\n" + "="*60)
        print("🚀 스마트 홈 허브 시작!")
        print("="*60)

        # 도움말 출력
        self.gesture_mapper.print_help()

        print(f"\n디바이스: {config.CURRENT_DEVICE}")
        print(f"해상도: {self.frame_width}x{self.frame_height}")
        print(f"목표 FPS: {self.target_fps}")
        print("\n키보드 단축키:")
        print("  [H] - 도움말 토글")
        print("  [S] - 상태 표시 토글")
        print("  [P] - 상태 출력")
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

                # 프레임 처리
                processed_frame, hand_info = self.process_frame(frame)

                # 화면 표시
                cv2.imshow('Smart Home Hub', processed_frame)

                # 키보드 입력 처리
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    break
                elif key == ord('h'):
                    self.show_help = not self.show_help
                    print(f"도움말 표시: {'ON' if self.show_help else 'OFF'}")
                elif key == ord('s'):
                    self.show_status = not self.show_status
                    print(f"상태 표시: {'ON' if self.show_status else 'OFF'}")
                elif key == ord('p'):
                    self.smart_home.print_status()
                    self.music_player.print_status()
                    self.gesture_mapper.print_action_history()

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
        self.smart_home.cleanup()
        self.music_player.cleanup()
        print("✅ 종료 완료")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='스마트 홈 허브 - 제스처 제어 시스템')
    parser.add_argument('--rtsp', type=str, help='RTSP 스트림 URL')
    parser.add_argument('--sim', action='store_true', help='시뮬레이션 모드 (GPIO/pygame 없이 실행)')
    parser.add_argument('--device', type=str, choices=['raspberry_pi_3', 'raspberry_pi_4', 'raspberry_pi_zero'],
                        help='라즈베리파이 모델')

    args = parser.parse_args()

    # 디바이스 설정 변경
    if args.device:
        config.CURRENT_DEVICE = args.device

    try:
        hub = SmartHub(rtsp_url=args.rtsp, simulation_mode=args.sim)
        hub.run()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
