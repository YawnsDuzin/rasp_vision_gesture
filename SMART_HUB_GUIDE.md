# 스마트 홈 허브 - 제스처 제어 시스템 완벽 가이드

## 🏠 프로젝트 개요

라즈베리파이와 RTSP 카메라를 활용하여 손 제스처로 스마트 홈 기기와 음악 플레이어를 제어하는 통합 시스템입니다.

### 주요 기능

- 🖐️ **제스처 인식**: MediaPipe를 활용한 실시간 손 제스처 인식
- 💡 **스마트 홈 제어**: GPIO를 통한 조명, 선풍기, 에어컨 등 제어
- 🎵 **음악 플레이어**: 제스처로 음악 재생/정지, 곡 변경, 볼륨 조절
- 🔄 **양손 제어**: 왼손은 스마트 홈, 오른손은 음악 플레이어
- 📊 **실시간 피드백**: FPS, 디바이스 상태, 음악 정보 표시

---

## 🎯 제스처 컨트롤 가이드

### 왼손 - 스마트 홈 제어

| 제스처 | 아이콘 | 동작 | 설명 |
|--------|--------|------|------|
| 주먹 | 👊 | 모든 디바이스 끄기 | 모든 조명과 가전제품 일괄 OFF |
| 손바닥 펴기 | 🖐️ | 모든 디바이스 켜기 | 모든 조명과 가전제품 일괄 ON |
| 엄지척 | 👍 | 조명 토글 | 메인 조명 ON/OFF |
| 브이 사인 | ✌️ | 선풍기 토글 | 선풍기 ON/OFF |
| OK 사인 | 👌 | 에어컨 토글 | 에어컨 ON/OFF |
| 손가락 1개 | ☝️ | 밝기 20% | 조명 밝기 20% 설정 |
| 손가락 2개 | ✌️ | 밝기 40% | 조명 밝기 40% 설정 |
| 손가락 3개 | 🖖 | 밝기 60% | 조명 밝기 60% 설정 |
| 손가락 4개 | 🖐️ | 밝기 80% | 조명 밝기 80% 설정 |
| 손가락 5개 | 🖐️ | 밝기 100% | 조명 밝기 100% 설정 |

### 오른손 - 음악 플레이어 제어

| 제스처 | 아이콘 | 동작 | 설명 |
|--------|--------|------|------|
| 주먹 | 👊 | 음악 정지 | 재생 중인 음악 정지 |
| 엄지척 | 👍 | 재생/일시정지 | 음악 재생 또는 일시정지 토글 |
| 가리키기 | ☝️ | 다음 곡 | 재생 목록의 다음 곡으로 이동 |
| 브이 사인 | ✌️ | 이전 곡 | 재생 목록의 이전 곡으로 이동 |
| 손바닥 펴기 | 🖐️ | 볼륨 업 | 현재 볼륨 +10% |
| 손가락 1개 | ☝️ | 볼륨 20% | 볼륨 20% 설정 |
| 손가락 2개 | ✌️ | 볼륨 40% | 볼륨 40% 설정 |
| 손가락 3개 | 🖖 | 볼륨 60% | 볼륨 60% 설정 |
| 손가락 4개 | 🖐️ | 볼륨 80% | 볼륨 80% 설정 |
| 손가락 5개 | 🖐️ | 볼륨 100% | 볼륨 100% 설정 |

---

## 🔧 시스템 구조

```
┌─────────────────────────────────────────────────────────────┐
│                      RTSP IP 카메라                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ RTSP Stream
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               라즈베리파이 (스마트 홈 허브)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         OpenCV + MediaPipe 제스처 인식 엔진           │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│         ┌───────────────┴───────────────┐                   │
│         │                               │                   │
│         ▼                               ▼                   │
│  ┌──────────────┐              ┌──────────────┐            │
│  │ 스마트 홈     │              │ 음악 플레이어 │            │
│  │ 컨트롤러     │              │ 컨트롤러      │            │
│  │ (GPIO)       │              │ (pygame)      │            │
│  └──────┬───────┘              └──────┬───────┘            │
│         │                             │                     │
└─────────┼─────────────────────────────┼─────────────────────┘
          │                             │
          ▼                             ▼
  ┌───────────────┐           ┌──────────────────┐
  │ 조명, 선풍기,  │           │ 스피커/오디오    │
  │ 에어컨 등     │           │                  │
  └───────────────┘           └──────────────────┘
```

---

## 📦 설치 및 설정

### 1. 시스템 요구사항

**하드웨어:**
- 라즈베리파이 3/4/5 (4GB RAM 권장)
- RTSP 지원 IP 카메라
- GPIO 연결 가능한 릴레이 모듈 (스마트 홈 제어용)
- 스피커 (음악 재생용, 선택)

**소프트웨어:**
- Raspberry Pi OS (Bullseye 이상)
- Python 3.7+

### 2. 라즈베리파이 설정

```bash
# 시스템 업데이트
sudo apt-get update
sudo apt-get upgrade -y

# 시스템 라이브러리 설치
sudo apt-get install -y python3-opencv
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y libhdf5-dev libhdf5-serial-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install -y python3-pygame
sudo apt-get install -y python3-rpi.gpio

# 오디오 라이브러리 (음악 재생용)
sudo apt-get install -y libsdl2-mixer-2.0-0
```

### 3. 프로젝트 설치

```bash
# 저장소 클론
git clone <repository-url>
cd rasp_vision_gesture

# Python 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate

# Python 패키지 설치
pip install -r requirements.txt
```

### 4. 설정 파일 수정

`config.py` 파일을 편집하여 환경에 맞게 설정하세요:

```python
# RTSP 카메라 URL
RTSP_URL = "rtsp://admin:password@192.168.1.100:554/stream1"

# 라즈베리파이 모델 (성능 최적화)
CURRENT_DEVICE = 'raspberry_pi_4'  # 또는 'raspberry_pi_3', 'raspberry_pi_zero'

# 음악 디렉토리
MUSIC_DIRECTORY = "~/Music"

# 스마트 홈 디바이스 (GPIO 핀 번호 확인 필수!)
SMART_HOME_DEVICES = [
    {
        'name': '거실 조명',
        'type': 'LIGHT',
        'pin': 17,  # BCM 핀 번호
        'initial_state': False
    },
    # ... 추가 디바이스
]
```

---

## 🚀 실행 방법

### 기본 실행

```bash
python3 smart_hub.py
```

### 시뮬레이션 모드 (GPIO/pygame 없이 테스트)

```bash
python3 smart_hub.py --sim
```

이 모드는 실제 하드웨어 없이 시스템을 테스트할 수 있습니다.

### RTSP URL 지정

```bash
python3 smart_hub.py --rtsp "rtsp://192.168.1.100:554/stream1"
```

### 라즈베리파이 모델 지정

```bash
python3 smart_hub.py --device raspberry_pi_3
```

### 전체 옵션 예제

```bash
python3 smart_hub.py \
  --rtsp "rtsp://admin:pass@192.168.1.100:554/stream" \
  --device raspberry_pi_4
```

---

## ⌨️ 키보드 단축키

실행 중 사용 가능한 키보드 단축키:

| 키 | 기능 |
|----|------|
| `H` | 화면 도움말 표시 ON/OFF |
| `S` | 상태 표시 ON/OFF |
| `P` | 콘솔에 상세 상태 출력 |
| `Q` | 프로그램 종료 |

---

## 🔌 하드웨어 연결

### GPIO 핀 배치 (BCM 모드)

라즈베리파이의 GPIO 핀을 사용하여 릴레이 모듈을 연결합니다.

```
기본 설정:
- GPIO 17: 거실 조명
- GPIO 27: 침실 조명
- GPIO 22: 선풍기
- GPIO 23: 에어컨
```

### 릴레이 모듈 연결 예시

```
릴레이 모듈 (4채널 예시)

   라즈베리파이                릴레이 모듈
┌─────────────┐            ┌──────────────┐
│             │            │              │
│  GPIO 17 ───┼───────────►│ IN1 (조명1)  │───► 조명 1
│  GPIO 27 ───┼───────────►│ IN2 (조명2)  │───► 조명 2
│  GPIO 22 ───┼───────────►│ IN3 (선풍기) │───► 선풍기
│  GPIO 23 ───┼───────────►│ IN4 (에어컨) │───► 에어컨
│             │            │              │
│  GND     ───┼───────────►│ GND          │
│  5V      ───┼───────────►│ VCC          │
└─────────────┘            └──────────────┘
```

**⚠️ 주의사항:**
- 고전압 가전제품 연결 시 반드시 전문가와 상담하세요
- 릴레이 모듈의 정격 전압/전류를 확인하세요
- 안전을 위해 차단기를 설치하세요

---

## 📁 프로젝트 파일 구조

```
rasp_vision_gesture/
├── smart_hub.py                    # 🚀 메인 프로그램 (통합 허브)
├── smart_home_controller.py        # 스마트 홈 GPIO 제어
├── music_player_controller.py      # 음악 플레이어 제어
├── gesture_actions.py              # 제스처 → 액션 매핑
├── config.py                       # 설정 파일
│
├── simple_example.py               # 기본 제스처 인식 예제
├── advanced_gesture_recognizer.py  # 고급 제스처 인식
│
├── requirements.txt                # Python 의존성
├── README.md                       # 프로젝트 개요
├── IMPLEMENTATION_GUIDE.md         # 개발 가이드
├── SMART_HUB_GUIDE.md             # 이 문서
└── .gitignore
```

---

## 🧪 개별 모듈 테스트

각 모듈은 독립적으로 테스트할 수 있습니다.

### 스마트 홈 컨트롤러 테스트

```bash
python3 smart_home_controller.py
```

### 음악 플레이어 테스트

```bash
python3 music_player_controller.py
```

### 제스처 액션 매퍼 테스트

```bash
python3 gesture_actions.py
```

---

## 🎨 커스터마이징

### 제스처 매핑 변경

`gesture_actions.py`의 `GestureActionMapper.__init__()` 메서드에서 제스처 매핑을 수정할 수 있습니다:

```python
self.gesture_mappings = {
    # 커스텀 매핑 추가
    ('Left', GestureType.THUMBS_UP): ActionType.LIGHT_TOGGLE,
    ('Right', GestureType.OPEN_PALM): ActionType.VOLUME_UP,
    # ... 원하는 매핑 추가
}
```

### 새로운 디바이스 추가

`config.py`에서 디바이스를 추가하세요:

```python
SMART_HOME_DEVICES = [
    # 기존 디바이스...
    {
        'name': '주방 조명',
        'type': 'LIGHT',
        'pin': 24,
        'initial_state': False
    },
    {
        'name': '공기청정기',
        'type': 'RELAY',
        'pin': 25,
        'initial_state': False
    },
]
```

### 액션 쿨다운 조정

같은 제스처를 연속으로 인식하는 시간 간격을 조정:

```python
# config.py
ACTION_COOLDOWN = 1.0  # 초 단위 (기본 1초)
```

---

## 🐛 트러블슈팅

### RTSP 연결 실패

**증상**: "RTSP 스트림 연결 실패" 메시지

**해결방법**:
1. 카메라 IP 주소 확인: `ping <카메라_IP>`
2. RTSP URL 형식 확인
3. 카메라 인증 정보 확인
4. 네트워크 방화벽 확인
5. FFmpeg 설치 확인: `ffmpeg -version`

### GPIO 권한 오류

**증상**: "Permission denied" 또는 GPIO 접근 오류

**해결방법**:
```bash
# 현재 사용자를 gpio 그룹에 추가
sudo usermod -a -G gpio $USER
sudo reboot

# 또는 sudo로 실행
sudo python3 smart_hub.py
```

### pygame 오디오 오류

**증상**: "pygame.error: No available audio device"

**해결방법**:
```bash
# ALSA 설정 확인
aplay -l

# 오디오 장치 테스트
speaker-test -t wav -c 2

# pygame 재설치
pip uninstall pygame
pip install pygame --no-cache-dir
```

### 낮은 FPS

**해결방법**:
1. `config.py`에서 해상도 낮추기
2. `CURRENT_DEVICE`를 실제 모델에 맞게 설정
3. `max_num_hands`를 1로 제한
4. `model_complexity`를 0으로 설정

```python
# config.py - 라즈베리파이 3 최적화 예시
CURRENT_DEVICE = 'raspberry_pi_3'
```

### 메모리 부족

```bash
# 스왑 메모리 증가
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048 설정
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
sudo reboot
```

---

## 🔒 보안 고려사항

### RTSP 인증

RTSP URL에 비밀번호가 포함되므로 `config.py` 파일을 안전하게 관리하세요:

```bash
# config.py 권한 제한
chmod 600 config.py

# Git에서 제외 (.gitignore에 이미 포함)
echo "config.py" >> .gitignore
```

### GPIO 안전

- 잘못된 연결로 인한 하드웨어 손상 주의
- 고전압 장치 연결 시 전문가와 상담
- 릴레이 모듈의 정격 확인

---

## 📊 성능 최적화

### 라즈베리파이 모델별 권장 설정

| 모델 | 해상도 | FPS | 손 개수 | 복잡도 |
|------|--------|-----|---------|--------|
| RPi 4 (4GB) | 640×480 | 15 | 2 | 0 |
| RPi 4 (2GB) | 480×360 | 12 | 2 | 0 |
| RPi 3 B+ | 480×360 | 10 | 1 | 0 |
| RPi 3 B | 320×240 | 8 | 1 | 0 |
| RPi Zero 2 | 320×240 | 5 | 1 | 0 |

### 오버클러킹 (선택)

**⚠️ 주의**: 오버클러킹은 발열과 안정성 문제를 야기할 수 있습니다.

```bash
# /boot/config.txt 편집
sudo nano /boot/config.txt

# 라즈베리파이 4 예시
over_voltage=6
arm_freq=2000

# 재부팅
sudo reboot
```

---

## 🌟 고급 기능 확장 아이디어

### 1. 음성 피드백 추가

```python
# pyttsx3 사용
import pyttsx3

engine = pyttsx3.init()
engine.say("조명을 켰습니다")
engine.runAndWait()
```

### 2. MQTT 연동

```python
import paho.mqtt.client as mqtt

# Home Assistant, OpenHAB 등과 연동
client = mqtt.Client()
client.connect("mqtt.broker.com", 1883)
client.publish("home/light/1", "ON")
```

### 3. 웹 대시보드

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    status = smart_home.get_status()
    return render_template('dashboard.html', status=status)
```

### 4. 제스처 녹화/재생

특정 제스처 시퀀스를 매크로로 저장하고 재생

### 5. 스케줄링

```python
import schedule

schedule.every().day.at("07:00").do(smart_home.turn_on, "거실 조명")
schedule.every().day.at("23:00").do(smart_home.turn_off_all)
```

---

## 📚 참고 자료

### 공식 문서
- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Raspberry Pi GPIO](https://www.raspberrypi.com/documentation/computers/os.html#gpio-and-the-40-pin-header)
- [pygame Documentation](https://www.pygame.org/docs/)

### 튜토리얼
- [RTSP Streaming with OpenCV](https://opencv.org/)
- [GPIO Zero Library](https://gpiozero.readthedocs.io/)
- [Home Assistant Integration](https://www.home-assistant.io/)

---

## 🤝 기여

버그 리포트, 기능 제안, 풀 리퀘스트는 언제나 환영합니다!

---

## 📄 라이센스

MIT License

---

## 💬 FAQ

### Q: 웹캠으로도 사용 가능한가요?

**A**: 네! RTSP URL 대신 `0`을 사용하세요:

```bash
python3 smart_hub.py --rtsp 0
```

또는 `config.py`에서:
```python
RTSP_URL = 0  # 기본 웹캠
```

### Q: 실제 GPIO 없이 테스트할 수 있나요?

**A**: 시뮬레이션 모드를 사용하세요:

```bash
python3 smart_hub.py --sim
```

### Q: 여러 대의 카메라를 사용할 수 있나요?

**A**: 현재 버전은 단일 카메라만 지원합니다. 다중 카메라 지원은 향후 추가 예정입니다.

### Q: 음악 파일 형식은 무엇을 지원하나요?

**A**: MP3, WAV, OGG, FLAC, M4A를 지원합니다.

### Q: 제스처 인식 정확도를 높이려면?

**A**:
1. 조명 환경 개선
2. 카메라 해상도 높이기
3. `MIN_DETECTION_CONFIDENCE` 값 조정
4. 단색 배경 사용

---

**🎉 즐거운 스마트 홈 제스처 제어 경험을 즐기세요!**
