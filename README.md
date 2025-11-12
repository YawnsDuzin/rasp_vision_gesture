# 라즈베리파이 RTSP 카메라 손가락 제스처 인식 시스템

라즈베리파이에서 RTSP 프로토콜을 통해 IP 카메라의 실시간 스트리밍을 받아 손가락 제스처를 인식하는 Python 기반 시스템입니다.

## 주요 기능

- 🎥 RTSP 카메라 스트리밍 실시간 수신
- 🖐️ MediaPipe를 활용한 손 검출 및 21개 랜드마크 추적
- 🔢 손가락 개수 인식 (0-5개)
- 👌 다양한 제스처 패턴 인식 (주먹, 브이, 엄지척, OK 사인 등)
- ⚡ 라즈베리파이 최적화 (성능/정확도 밸런스)
- 📊 실시간 FPS 및 신뢰도 표시

## 시스템 요구사항

### 하드웨어
- 라즈베리파이 3/4/5 (4GB RAM 권장)
- RTSP 지원 IP 카메라
- (선택) 디스플레이 또는 VNC/SSH 원격 접속

### 소프트웨어
- Raspberry Pi OS (Bullseye 이상)
- Python 3.7+
- OpenCV 4.5+
- MediaPipe 0.10+

## 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/YawnsDuzin/rasp_vision_gesture.git
cd rasp_vision_gesture
```

### 2. 시스템 라이브러리 설치

```bash
sudo apt-get update
sudo apt-get install -y python3-opencv
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y libhdf5-dev libhdf5-serial-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev
```

### 3. Python 가상환경 설정 (권장)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Python 패키지 설치

```bash
pip install -r requirements.txt
```

## 설정

`config.py` 파일을 열어 RTSP URL과 디바이스 설정을 수정하세요:

```python
# RTSP 카메라 URL 설정
RTSP_URL = "rtsp://admin:password@192.168.1.100:554/stream1"

# 사용 중인 라즈베리파이 모델
CURRENT_DEVICE = 'raspberry_pi_4'  # 또는 'raspberry_pi_3', 'raspberry_pi_zero'
```

## 사용 방법

### 간단한 예제 실행

```bash
python3 simple_example.py
```

이 스크립트는 기본적인 손 검출과 손가락 개수 세기 기능을 제공합니다.

### 고급 제스처 인식 실행

```bash
python3 advanced_gesture_recognizer.py
```

다양한 제스처 패턴 인식과 최적화된 성능을 제공합니다.

### 종료

프로그램 실행 중 `q` 키를 누르면 종료됩니다.

## 인식 가능한 제스처

| 제스처 | 설명 | 손가락 개수 |
|--------|------|-------------|
| FIST | 주먹 | 0 |
| POINTING | 가리키기 | 1 (검지) |
| THUMBS_UP | 엄지척 | 1 (엄지) |
| V_SIGN | 브이 사인 | 2 (검지+중지) |
| OK_SIGN | OK 사인 | 3 (엄지+검지 붙임) |
| OPEN_PALM | 손바닥 펴기 | 5 |

## 성능 최적화

### 라즈베리파이 4
```python
config = {
    'resolution': (640, 480),
    'fps': 15,
    'model_complexity': 0,
    'max_num_hands': 2
}
```

### 라즈베리파이 3
```python
config = {
    'resolution': (480, 360),
    'fps': 10,
    'model_complexity': 0,
    'max_num_hands': 1
}
```

## 트러블슈팅

### RTSP 연결 실패
```bash
# 카메라 URL 확인
ping <카메라_IP>

# FFmpeg 설치 확인
ffmpeg -version
```

### 낮은 FPS
- `config.py`에서 해상도 낮추기
- `model_complexity`를 0으로 설정
- `max_num_hands`를 1로 제한

### 메모리 부족
```bash
# 스왑 메모리 증가
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 프로젝트 구조

```
rasp_vision_gesture/
├── config.py                        # 설정 파일
├── simple_example.py                # 간단한 예제
├── advanced_gesture_recognizer.py   # 고급 제스처 인식
├── requirements.txt                 # Python 패키지 의존성
├── IMPLEMENTATION_GUIDE.md          # 상세 개발 가이드
└── README.md                        # 프로젝트 설명
```

## 상세 개발 가이드

프로젝트의 전체 구조, 알고리즘 설명, 단계별 개발 절차는 [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) 파일을 참고하세요.

## 라이센스

MIT License

## 참고 자료

- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV VideoCapture](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)

## 기여

이슈와 풀 리퀘스트는 언제나 환영합니다!
