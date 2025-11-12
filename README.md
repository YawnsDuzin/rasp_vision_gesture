# 라즈베리파이 RTSP 카메라 손가락 제스처 인식 시스템

라즈베리파이에서 RTSP 프로토콜을 통해 IP 카메라의 실시간 스트리밍을 받아 손가락 제스처를 인식하는 Python 기반 시스템입니다.

## 주요 기능

### 기본 제스처 인식
- 🎥 RTSP 카메라 스트리밍 실시간 수신
- 🖐️ MediaPipe를 활용한 손 검출 및 21개 랜드마크 추적
- 🔢 손가락 개수 인식 (0-5개)
- 👌 다양한 제스처 패턴 인식 (주먹, 브이, 엄지척, OK 사인 등)
- ⚡ 라즈베리파이 최적화 (성능/정확도 밸런스)
- 📊 실시간 FPS 및 신뢰도 표시

### 🏠 스마트 홈 허브
- 💡 **스마트 홈 제어**: GPIO를 통한 조명, 선풍기, 에어컨 등 제어
- 🎵 **음악 플레이어**: 제스처로 음악 재생/정지, 곡 변경, 볼륨 조절
- 🔄 **양손 제어**: 왼손은 스마트 홈, 오른손은 음악 플레이어
- 🎮 **통합 제어**: 하나의 인터페이스로 모든 기능 제어

### 🔐 제스처 보안 시스템 ⭐ NEW!
- 🔑 **제스처 비밀번호**: 특정 순서의 제스처 조합으로 인증
- 🛡️ **무차별 대입 방지**: 최대 시도 횟수 제한
- ⏱️ **타임아웃**: 제스처 입력 시간 제한
- 📊 **로그 기록**: 모든 인증 시도 기록
- 🔒 **자동 잠금**: 실패 시 일시 잠금

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

### 🏠 스마트 홈 허브 실행

완전한 스마트 홈 제어 시스템:

```bash
python3 smart_hub.py
```

시뮬레이션 모드 (GPIO/pygame 없이 테스트):
```bash
python3 smart_hub.py --sim
```

**상세 가이드**: [SMART_HUB_GUIDE.md](SMART_HUB_GUIDE.md) 참고

### 🔐 제스처 보안 시스템 실행 ⭐ NEW!

제스처 비밀번호 인증 데모:

```bash
python3 security_demo.py
```

시뮬레이션 모드:
```bash
python3 security_demo.py --sim
```

예제 모음 실행:
```bash
python3 security_examples.py
```

**상세 가이드**: [SECURITY_GUIDE.md](SECURITY_GUIDE.md) 참고

### 간단한 예제 실행

기본적인 손 검출과 손가락 개수 세기:

```bash
python3 simple_example.py
```

### 고급 제스처 인식 실행

다양한 제스처 패턴 인식:

```bash
python3 advanced_gesture_recognizer.py
```

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
├── smart_hub.py                     # 🚀 스마트 홈 허브 (메인)
├── smart_home_controller.py         # 스마트 홈 GPIO 제어
├── music_player_controller.py       # 음악 플레이어 제어
├── gesture_actions.py               # 제스처 액션 매핑
│
├── security_demo.py                 # 🔐 제스처 보안 시스템 데모
├── gesture_security.py              # 제스처 보안 모듈
├── security_examples.py             # 보안 시스템 예제 모음
│
├── simple_example.py                # 간단한 예제
├── advanced_gesture_recognizer.py   # 고급 제스처 인식
├── config.py                        # 설정 파일
│
├── requirements.txt                 # Python 패키지 의존성
├── README.md                        # 프로젝트 설명
├── IMPLEMENTATION_GUIDE.md          # 상세 개발 가이드
├── SMART_HUB_GUIDE.md              # 스마트 홈 허브 가이드
├── SECURITY_GUIDE.md               # 제스처 보안 가이드
└── .gitignore
```

## 📚 문서

- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)**: 제스처 인식 시스템 개발 가이드
  - 기술 스택 및 아키텍처
  - MediaPipe 손 검출 알고리즘
  - 단계별 개발 절차
  - 최적화 전략

- **[SMART_HUB_GUIDE.md](SMART_HUB_GUIDE.md)**: 스마트 홈 허브 완벽 가이드
  - 제스처 컨트롤 가이드
  - 하드웨어 연결 방법
  - GPIO 핀 배치
  - 커스터마이징 방법
  - 트러블슈팅

- **[SECURITY_GUIDE.md](SECURITY_GUIDE.md)**: 제스처 보안 시스템 가이드 ⭐ NEW!
  - 제스처 비밀번호 설정
  - 보안 메커니즘 설명
  - 비밀번호 패턴 추천
  - 실제 사용 예제
  - API 레퍼런스

## 라이센스

MIT License

## 참고 자료

- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV VideoCapture](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)

## 기여

이슈와 풀 리퀘스트는 언제나 환영합니다!
