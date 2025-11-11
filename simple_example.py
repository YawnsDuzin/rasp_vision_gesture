#!/usr/bin/env python3
"""
간단한 RTSP 손가락 제스처 인식 예제

이 스크립트는 가장 기본적인 형태로 RTSP 스트림을 받아
손을 검출하고 손가락 개수를 세는 기능을 구현합니다.
"""

import cv2
import mediapipe as mp
import sys


class SimpleGestureDetector:
    def __init__(self, rtsp_url):
        """
        초기화

        Args:
            rtsp_url: RTSP 스트림 URL
        """
        self.rtsp_url = rtsp_url

        # MediaPipe 초기화
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # 비디오 캡처 초기화
        print(f"RTSP 연결 시도: {rtsp_url}")
        self.cap = cv2.VideoCapture(rtsp_url)

        # 버퍼 설정 (지연 최소화)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            print("❌ RTSP 스트림 연결 실패!")
            sys.exit(1)

        print("✅ RTSP 스트림 연결 성공!")

    def count_fingers(self, hand_landmarks, handedness):
        """
        손가락 개수 세기

        Args:
            hand_landmarks: MediaPipe 손 랜드마크
            handedness: 'Left' 또는 'Right'

        Returns:
            펴진 손가락 개수
        """
        fingers = []

        # 엄지 판별 (좌/우 손에 따라 다름)
        if handedness == 'Right':
            if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                fingers.append(1)
            else:
                fingers.append(0)
        else:  # Left hand
            if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
                fingers.append(1)
            else:
                fingers.append(0)

        # 나머지 손가락 (검지, 중지, 약지, 소지)
        tip_ids = [8, 12, 16, 20]  # 손가락 끝 ID
        pip_ids = [6, 10, 14, 18]  # 두 번째 관절 ID

        for tip, pip in zip(tip_ids, pip_ids):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                fingers.append(1)  # 펴짐
            else:
                fingers.append(0)  # 접힘

        return sum(fingers)

    def run(self):
        """
        메인 루프 실행
        """
        print("\n제스처 인식 시작!")
        print("종료하려면 'q'를 누르세요.\n")

        while True:
            # 프레임 읽기
            ret, frame = self.cap.read()

            if not ret:
                print("프레임 수신 실패. 재연결 시도...")
                break

            # 성능 최적화를 위한 리사이징
            frame = cv2.resize(frame, (640, 480))

            # BGR을 RGB로 변환 (MediaPipe는 RGB 사용)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 손 검출
            results = self.hands.process(rgb_frame)

            # 검출된 손이 있는 경우
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # 손 랜드마크 그리기
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )

                    # 손 방향 (좌/우)
                    handedness = results.multi_handedness[idx].classification[0].label

                    # 손가락 개수 세기
                    finger_count = self.count_fingers(hand_landmarks, handedness)

                    # 화면에 정보 표시
                    y_offset = 30 + (idx * 150)
                    cv2.putText(frame, f"{handedness} Hand", (10, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Fingers: {finger_count}", (10, y_offset + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # 콘솔에도 출력
                    print(f"\r{handedness} 손: {finger_count}개 손가락", end="")

            # 프레임 표시
            cv2.imshow('Gesture Detection', frame)

            # 'q' 키로 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def cleanup(self):
        """
        리소스 정리
        """
        print("\n\n정리 중...")
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()
        print("✅ 종료 완료")


def main():
    """
    메인 함수
    """
    # RTSP URL 설정 (여기를 수정하세요!)
    rtsp_url = "rtsp://admin:password@192.168.1.100:554/stream1"

    # 또는 로컬 웹캠 테스트: rtsp_url = 0

    # 제스처 검출기 생성 및 실행
    detector = SimpleGestureDetector(rtsp_url)
    detector.run()


if __name__ == "__main__":
    main()
