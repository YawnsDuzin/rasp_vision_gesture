#!/usr/bin/env python3
"""
고급 제스처 인식 시스템

다양한 제스처 패턴을 인식하고, 최적화된 성능을 제공합니다.
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
import config


class AdvancedGestureRecognizer:
    def __init__(self, rtsp_url=None):
        """
        초기화

        Args:
            rtsp_url: RTSP 스트림 URL (None이면 config에서 로드)
        """
        self.rtsp_url = rtsp_url or config.RTSP_URL

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

        # 비디오 캡처 초기화
        self.cap = self._initialize_capture()

        # FPS 계산용
        self.fps_queue = deque(maxlen=30)
        self.last_time = time.time()

        # 제스처 히스토리 (안정성을 위해)
        self.gesture_history = deque(maxlen=config.GESTURE_HOLD_FRAMES)

    def _initialize_capture(self):
        """
        비디오 캡처 초기화
        """
        print(f"RTSP 연결 시도: {self.rtsp_url}")

        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, config.BUFFER_SIZE)

        if not cap.isOpened():
            print("❌ RTSP 스트림 연결 실패!")
            raise ConnectionError("RTSP 연결 실패")

        print("✅ RTSP 스트림 연결 성공!")
        return cap

    def count_fingers(self, hand_landmarks, handedness):
        """
        손가락 개수 세기
        """
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
        """
        제스처 인식

        Returns:
            제스처 이름, 신뢰도
        """
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.append([lm.x, lm.y, lm.z])

        landmarks = np.array(landmarks)

        # 손가락 끝과 손목 위치
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        wrist = landmarks[0]
        index_mcp = landmarks[5]

        # 1. 주먹 (FIST)
        if finger_count == 0:
            return "FIST", 0.95

        # 2. 손바닥 펴기 (OPEN_PALM)
        elif finger_count == 5:
            return "OPEN_PALM", 0.95

        # 3. 엄지척 (THUMBS_UP)
        elif finger_count == 1 and thumb_tip[1] < wrist[1]:
            return "THUMBS_UP", 0.90

        # 4. 브이 사인 (V_SIGN)
        elif finger_count == 2:
            # 검지와 중지가 펴져있는지 확인
            if (index_tip[1] < wrist[1] and
                middle_tip[1] < wrist[1] and
                ring_tip[1] > index_mcp[1]):
                return "V_SIGN", 0.90
            else:
                return "TWO_FINGERS", 0.85

        # 5. OK 사인 (검지와 엄지가 닿음)
        elif finger_count == 3:
            thumb_index_dist = np.linalg.norm(thumb_tip[:2] - index_tip[:2])
            if thumb_index_dist < 0.05:  # 매우 가까움
                return "OK_SIGN", 0.85

        # 6. 가리키기 (POINTING)
        elif finger_count == 1:
            if index_tip[1] < wrist[1]:
                return "POINTING", 0.85

        return "UNKNOWN", 0.0

    def calculate_angle(self, a, b, c):
        """
        세 점 사이의 각도 계산
        """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
                  np.arctan2(a[1] - b[1], a[0] - b[0])

        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def get_stable_gesture(self, current_gesture):
        """
        제스처 히스토리를 사용하여 안정적인 제스처 반환
        """
        self.gesture_history.append(current_gesture)

        # 가장 많이 나타난 제스처 반환
        if len(self.gesture_history) >= config.GESTURE_HOLD_FRAMES:
            gesture_counts = {}
            for gesture in self.gesture_history:
                gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1

            most_common = max(gesture_counts, key=gesture_counts.get)
            if gesture_counts[most_common] >= config.GESTURE_HOLD_FRAMES * 0.6:
                return most_common

        return current_gesture

    def calculate_fps(self):
        """
        FPS 계산
        """
        current_time = time.time()
        fps = 1.0 / (current_time - self.last_time)
        self.last_time = current_time
        self.fps_queue.append(fps)

        return np.mean(self.fps_queue)

    def draw_info(self, frame, hand_info):
        """
        프레임에 정보 그리기
        """
        # FPS 표시
        if config.SHOW_FPS:
            fps = self.calculate_fps()
            cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # 손 정보 표시
        for idx, info in enumerate(hand_info):
            y_offset = 30 + (idx * 120)

            cv2.putText(frame, f"{info['handedness']} Hand",
                        (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Fingers: {info['finger_count']}",
                        (10, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Gesture: {info['gesture']}",
                        (10, y_offset + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            cv2.putText(frame, f"Confidence: {info['confidence']:.2f}",
                        (10, y_offset + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    def process_frame(self, frame):
        """
        프레임 처리
        """
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

                # 안정적인 제스처
                stable_gesture = self.get_stable_gesture(gesture)

                hand_info.append({
                    'handedness': handedness,
                    'finger_count': finger_count,
                    'gesture': stable_gesture,
                    'confidence': confidence
                })

        # 정보 그리기
        self.draw_info(frame, hand_info)

        return frame, hand_info

    def run(self):
        """
        메인 루프
        """
        print("\n🚀 고급 제스처 인식 시작!")
        print("종료: 'q' 키")
        print(f"디바이스: {config.CURRENT_DEVICE}")
        print(f"해상도: {self.frame_width}x{self.frame_height}")
        print(f"목표 FPS: {self.target_fps}\n")

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
                cv2.imshow('Advanced Gesture Recognition', processed_frame)

                # 콘솔 출력
                if hand_info:
                    info_str = " | ".join([
                        f"{info['handedness']}: {info['gesture']} ({info['finger_count']})"
                        for info in hand_info
                    ])
                    print(f"\r{info_str}                    ", end="")

                # FPS 제한
                elapsed_time = time.time() - start_time
                sleep_time = frame_duration - elapsed_time
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # 종료 확인
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\n\n사용자 중단")

        finally:
            self.cleanup()

    def cleanup(self):
        """
        리소스 정리
        """
        print("\n\n🧹 정리 중...")
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()
        print("✅ 종료 완료")


def main():
    """
    메인 함수
    """
    try:
        recognizer = AdvancedGestureRecognizer()
        recognizer.run()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
