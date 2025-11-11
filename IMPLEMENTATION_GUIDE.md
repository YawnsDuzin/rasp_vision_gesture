# 라즈베리파이 RTSP 카메라 손가락 제스처 인식 시스템 개발 가이드

## 1. 프로젝트 개요

### 1.1 목표
- RTSP 프로토콜을 통해 IP 카메라에서 실시간 영상 스트리밍 수신
- MediaPipe를 활용한 손가락 및 손 랜드마크 검출
- 실시간 제스처 인식 (예: 손가락 개수, 특정 제스처 등)
- 라즈베리파이에서 안정적으로 동작하는 최적화된 시스템

### 1.2 시스템 아키텍처

```
[RTSP 카메라]
    ↓ (RTSP Stream)
[OpenCV VideoCapture]
    ↓ (프레임 수신)
[전처리 & 리사이징]
    ↓
[MediaPipe Hands 모델]
    ↓ (손 랜드마크 검출)
[제스처 분석 로직]
    ↓
[결과 출력 / 액션 실행]
```

---

## 2. 기술 스택 및 라이브러리

### 2.1 핵심 라이브러리

#### **OpenCV (opencv-python)**
- **목적**: RTSP 스트림 수신, 이미지 처리
- **이유**: RTSP 프로토콜 지원, 다양한 코덱 호환
- **버전**: 4.5.x 이상 권장

#### **MediaPipe**
- **목적**: 손 검출 및 21개 손 랜드마크 추출
- **이유**:
  - Google이 개발한 경량화된 ML 솔루션
  - 라즈베리파이에서도 실시간 처리 가능
  - 높은 정확도
- **버전**: 0.10.x 권장

#### **NumPy**
- **목적**: 벡터 연산, 각도 계산
- **이유**: 제스처 인식 로직에 필요한 수학 연산

#### **추가 라이브러리 (선택사항)**
- **imutils**: 이미지 처리 유틸리티
- **threading**: 비동기 프레임 처리
- **queue**: 프레임 버퍼링

---

## 3. 개발 환경 설정

### 3.1 라즈베리파이 준비

```bash
# 시스템 업데이트
sudo apt-get update
sudo apt-get upgrade -y

# Python 3 및 pip 확인
python3 --version
pip3 --version

# 필수 시스템 라이브러리 설치
sudo apt-get install -y python3-opencv
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y libhdf5-dev libhdf5-serial-dev
sudo apt-get install -y libqt5gui5 libqt5webkit5 libqt5test5
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install -y libv4l-dev libxvidcore-dev libx264-dev
```

### 3.2 Python 가상환경 설정 (권장)

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip
```

### 3.3 Python 패키지 설치

```bash
# 핵심 라이브러리
pip install opencv-python
pip install mediapipe
pip install numpy

# 추가 유틸리티
pip install imutils
```

**주의사항**: 라즈베리파이에서 MediaPipe 설치 시 시간이 오래 걸릴 수 있습니다.

---

## 4. RTSP 스트리밍 수신 구현

### 4.1 RTSP URL 형식

```
rtsp://[username:password@]host[:port]/path
```

**예시**:
- `rtsp://192.168.1.100:554/stream1`
- `rtsp://admin:password123@192.168.1.100:554/live/main`

### 4.2 OpenCV를 통한 RTSP 수신

```python
import cv2

# RTSP 스트림 연결
rtsp_url = "rtsp://admin:password@192.168.1.100:554/stream1"
cap = cv2.VideoCapture(rtsp_url)

# 연결 설정 (중요!)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 버퍼 크기 최소화 (지연 감소)
cap.set(cv2.CAP_PROP_FPS, 15)  # 프레임레이트 제한

if not cap.isOpened():
    print("RTSP 스트림 연결 실패")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("프레임 수신 실패")
        break

    # 프레임 처리
    cv2.imshow('RTSP Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### 4.3 RTSP 연결 최적화 팁

```python
# FFmpeg 백엔드 사용 (더 안정적)
import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

# TCP 연결 (안정성 우선)
# os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
```

---

## 5. MediaPipe Hands를 통한 손 검출

### 5.1 MediaPipe Hands 초기화

```python
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Hands 모델 설정
hands = mp_hands.Hands(
    static_image_mode=False,      # 비디오 스트림 모드
    max_num_hands=2,               # 최대 손 개수
    min_detection_confidence=0.5,  # 검출 신뢰도
    min_tracking_confidence=0.5    # 추적 신뢰도
)
```

### 5.2 손 랜드마크 검출

MediaPipe는 손마다 **21개의 랜드마크**를 검출합니다:

```
손가락 구조:
- 엄지 (THUMB): 0-4
- 검지 (INDEX): 5-8
- 중지 (MIDDLE): 9-12
- 약지 (RING): 13-16
- 소지 (PINKY): 17-20
```

```python
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # BGR → RGB 변환 (MediaPipe 입력)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 손 검출
    results = hands.process(rgb_frame)

    # 검출된 손이 있는 경우
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 랜드마크 그리기
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # 랜드마크 좌표 추출
            for id, landmark in enumerate(hand_landmarks.landmark):
                h, w, c = frame.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                print(f"Landmark {id}: ({cx}, {cy})")

    cv2.imshow('Hand Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

---

## 6. 제스처 인식 로직 구현

### 6.1 손가락 펴짐/접힘 판별

```python
def count_fingers(hand_landmarks, handedness):
    """
    손가락이 펴져있는지 확인하여 개수 반환

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
```

### 6.2 제스처 패턴 인식

```python
import numpy as np

def recognize_gesture(hand_landmarks):
    """
    특정 제스처 인식

    Returns:
        제스처 이름 (str)
    """
    landmarks = []
    for landmark in hand_landmarks.landmark:
        landmarks.append([landmark.x, landmark.y, landmark.z])

    landmarks = np.array(landmarks)

    # 예시: 브이(V) 제스처 인식
    # 검지와 중지가 펴져있고, 나머지는 접혀있는지 확인
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    wrist = landmarks[0]

    # 검지, 중지가 손목보다 위에 있고
    # 약지, 소지가 손목보다 아래에 있으면 V 제스처
    if (index_tip[1] < wrist[1] and
        middle_tip[1] < wrist[1] and
        ring_tip[1] > wrist[1] and
        pinky_tip[1] > wrist[1]):
        return "V_SIGN"

    # 주먹 제스처
    if (index_tip[1] > wrist[1] and
        middle_tip[1] > wrist[1] and
        ring_tip[1] > wrist[1] and
        pinky_tip[1] > wrist[1]):
        return "FIST"

    # 손바닥 펴기
    if (index_tip[1] < wrist[1] and
        middle_tip[1] < wrist[1] and
        ring_tip[1] < wrist[1] and
        pinky_tip[1] < wrist[1]):
        return "OPEN_PALM"

    return "UNKNOWN"
```

### 6.3 각도 기반 제스처 인식

```python
def calculate_angle(a, b, c):
    """
    세 점 사이의 각도 계산

    Args:
        a, b, c: 각 점의 [x, y] 좌표

    Returns:
        각도 (도)
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

def detect_thumbs_up(hand_landmarks):
    """
    엄지척 제스처 인식
    """
    # 엄지 끝, 엄지 중간, 손목
    thumb_tip = [hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y]
    thumb_mcp = [hand_landmarks.landmark[2].x, hand_landmarks.landmark[2].y]
    wrist = [hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y]

    angle = calculate_angle(thumb_tip, thumb_mcp, wrist)

    # 엄지가 위로 향하는지 확인
    if thumb_tip[1] < wrist[1] and angle > 160:
        return True

    return False
```

---

## 7. 통합 시스템 구현

### 7.1 전체 파이프라인

```python
import cv2
import mediapipe as mp
import numpy as np

class GestureRecognizer:
    def __init__(self, rtsp_url):
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

        # 비디오 캡처
        self.cap = cv2.VideoCapture(rtsp_url)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def count_fingers(self, hand_landmarks, handedness):
        # 이전에 구현한 함수 사용
        pass

    def recognize_gesture(self, hand_landmarks):
        # 이전에 구현한 함수 사용
        pass

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("프레임 수신 실패")
                break

            # 성능 최적화: 프레임 크기 조정
            frame = cv2.resize(frame, (640, 480))

            # RGB 변환
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 손 검출
            results = self.hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # 손 그리기
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )

                    # 손 방향 (좌/우)
                    handedness = results.multi_handedness[idx].classification[0].label

                    # 손가락 개수
                    finger_count = self.count_fingers(hand_landmarks, handedness)

                    # 제스처 인식
                    gesture = self.recognize_gesture(hand_landmarks)

                    # 화면에 표시
                    cv2.putText(frame, f"{handedness} Hand", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Fingers: {finger_count}", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 110),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 화면 출력
            cv2.imshow('Gesture Recognition', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()

if __name__ == "__main__":
    rtsp_url = "rtsp://admin:password@192.168.1.100:554/stream1"
    recognizer = GestureRecognizer(rtsp_url)
    recognizer.run()
```

---

## 8. 라즈베리파이 최적화

### 8.1 성능 최적화 전략

#### **1) 프레임 해상도 조정**
```python
# 640x480 또는 480x360으로 리사이징
frame = cv2.resize(frame, (640, 480))
```

#### **2) FPS 제한**
```python
import time

target_fps = 15
frame_duration = 1.0 / target_fps

while True:
    start_time = time.time()

    # 프레임 처리
    # ...

    elapsed_time = time.time() - start_time
    sleep_time = frame_duration - elapsed_time

    if sleep_time > 0:
        time.sleep(sleep_time)
```

#### **3) MediaPipe 모델 복잡도 조정**
```python
hands = self.mp_hands.Hands(
    model_complexity=0,  # 0 (가벼움) ~ 1 (정확함)
    max_num_hands=1,     # 손 개수 제한
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
```

#### **4) 멀티스레딩 (프레임 수신 분리)**
```python
import threading
from queue import Queue

class VideoStream:
    def __init__(self, rtsp_url):
        self.cap = cv2.VideoCapture(rtsp_url)
        self.queue = Queue(maxsize=2)
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.queue.full():
                ret, frame = self.cap.read()
                if ret:
                    self.queue.put(frame)

    def read(self):
        return self.queue.get()

    def stop(self):
        self.stopped = True
        self.cap.release()
```

### 8.2 라즈베리파이 4 권장 설정

```python
# 라즈베리파이 4 (4GB RAM)
config = {
    'resolution': (640, 480),
    'fps': 15,
    'model_complexity': 0,
    'max_num_hands': 1,
    'min_detection_confidence': 0.7,
    'min_tracking_confidence': 0.5
}

# 라즈베리파이 3
config = {
    'resolution': (480, 360),
    'fps': 10,
    'model_complexity': 0,
    'max_num_hands': 1,
    'min_detection_confidence': 0.7,
    'min_tracking_confidence': 0.5
}
```

---

## 9. 개발 단계별 절차

### Phase 1: 기본 환경 구축 (1일)
1. ✅ 라즈베리파이 OS 설치 및 업데이트
2. ✅ Python 환경 설정
3. ✅ 필수 라이브러리 설치
4. ✅ RTSP 카메라 연결 테스트

### Phase 2: RTSP 스트리밍 구현 (1일)
1. ✅ OpenCV로 RTSP 스트림 수신
2. ✅ 프레임 표시 확인
3. ✅ 연결 안정성 테스트
4. ✅ 버퍼링/지연 최적화

### Phase 3: 손 검출 구현 (2일)
1. ✅ MediaPipe Hands 통합
2. ✅ 손 랜드마크 시각화
3. ✅ 실시간 손 추적 테스트
4. ✅ 성능 측정 및 최적화

### Phase 4: 제스처 인식 로직 (2-3일)
1. ✅ 손가락 개수 세기 구현
2. ✅ 기본 제스처 패턴 정의
3. ✅ 제스처 인식 알고리즘 개발
4. ✅ 정확도 테스트 및 개선

### Phase 5: 시스템 통합 및 최적화 (2일)
1. ✅ 전체 파이프라인 통합
2. ✅ 라즈베리파이 최적화
3. ✅ 에러 핸들링 추가
4. ✅ 로깅 시스템 구현

### Phase 6: 테스트 및 배포 (1일)
1. ✅ 다양한 조명 환경 테스트
2. ✅ 다양한 손 크기/모양 테스트
3. ✅ 장시간 안정성 테스트
4. ✅ 문서화

---

## 10. 트러블슈팅

### 10.1 RTSP 연결 문제

**문제**: "Unable to open RTSP stream"

**해결방법**:
```python
# 1. 카메라 URL 확인
# 2. 네트워크 연결 확인
# 3. FFmpeg 백엔드 사용
import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

# 4. 타임아웃 설정
cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
```

### 10.2 프레임 지연 문제

**해결방법**:
```python
# 버퍼 크기 최소화
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# 낮은 해상도 사용
frame = cv2.resize(frame, (480, 360))

# 프레임 스킵
frame_count = 0
while True:
    ret, frame = cap.read()
    frame_count += 1

    if frame_count % 2 == 0:  # 2프레임마다 1번 처리
        continue
```

### 10.3 MediaPipe 성능 문제

**해결방법**:
```python
# 모델 복잡도 낮추기
hands = mp_hands.Hands(model_complexity=0)

# 검출 횟수 줄이기
hands = mp_hands.Hands(
    static_image_mode=False,  # 비디오 모드 (추적 사용)
    min_detection_confidence=0.7
)
```

### 10.4 메모리 부족 문제

**해결방법**:
```bash
# 스왑 메모리 증가
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048 설정
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 11. 추가 기능 확장

### 11.1 제스처 기반 제어
```python
def execute_gesture_action(gesture):
    if gesture == "THUMBS_UP":
        print("좋아요!")
        # LED 켜기, 알림 전송 등

    elif gesture == "FIST":
        print("정지!")
        # 프로세스 일시정지

    elif gesture == "OPEN_PALM":
        print("시작!")
        # 프로세스 시작
```

### 11.2 데이터 로깅
```python
import json
from datetime import datetime

def log_gesture(gesture, confidence):
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'gesture': gesture,
        'confidence': confidence
    }

    with open('gesture_log.json', 'a') as f:
        json.dump(log_data, f)
        f.write('\n')
```

### 11.3 웹 인터페이스 (Flask)
```python
from flask import Flask, Response

app = Flask(__name__)

def generate_frames():
    while True:
        # 프레임 처리
        ret, frame = cap.read()

        # JPEG 인코딩
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 12. 참고 자료

### 공식 문서
- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV VideoCapture](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)
- [라즈베리파이 공식 문서](https://www.raspberrypi.org/documentation/)

### 튜토리얼
- MediaPipe Hand Tracking: https://google.github.io/mediapipe/solutions/hands
- RTSP Streaming with OpenCV: https://opencv.org/

### 커뮤니티
- 라즈베리파이 포럼
- Stack Overflow (opencv, mediapipe 태그)

---

## 13. 프로젝트 구조 예시

```
rasp_vision_gesture/
├── main.py                      # 메인 실행 파일
├── config.py                    # 설정 파일
├── gesture_recognizer.py        # 제스처 인식 클래스
├── stream_handler.py            # RTSP 스트림 핸들러
├── gesture_actions.py           # 제스처 액션 실행
├── utils/
│   ├── __init__.py
│   ├── image_processing.py      # 이미지 전처리
│   └── logger.py                # 로깅 유틸리티
├── tests/
│   ├── test_gesture.py
│   └── test_stream.py
├── requirements.txt             # 패키지 의존성
├── README.md                    # 프로젝트 설명
└── .gitignore
```

---

## 14. requirements.txt

```txt
opencv-python==4.8.0.74
mediapipe==0.10.3
numpy==1.24.3
imutils==0.5.4
```

---

이 가이드를 따라 단계별로 진행하시면 라즈베리파이에서 RTSP 카메라를 통한 손가락 제스처 인식 시스템을 구축하실 수 있습니다!
