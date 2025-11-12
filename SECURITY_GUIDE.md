# 제스처 보안 시스템 완벽 가이드

## 🔐 프로젝트 개요

제스처 시퀀스를 비밀번호로 사용하여 잠금을 해제하는 혁신적인 보안 인증 시스템입니다.

### 주요 기능

- 🔑 **제스처 비밀번호**: 특정 순서의 제스처 조합으로 인증
- 🛡️ **무차별 대입 방지**: 최대 시도 횟수 제한
- ⏱️ **타임아웃**: 제스처 입력 시간 제한
- 🔒 **자동 잠금**: 일정 시도 실패 시 일시 잠금
- 📊 **로그 기록**: 모든 인증 시도 기록
- 🔐 **해시 저장**: 비밀번호를 SHA-256 해시로 안전하게 저장

---

## 🎯 작동 원리

### 제스처 비밀번호 시스템

```
사용자가 설정한 제스처 시퀀스:
브이(✌️) → 주먹(👊) → 엄지척(👍) → OK(👌)

시스템은 이 시퀀스를 해시값으로 저장:
"V_SIGN|FIST|THUMBS_UP|OK_SIGN" → SHA-256 → [해시값]

인증 시도:
1. 사용자가 제스처 시퀀스 입력
2. 시스템이 해시 생성
3. 저장된 해시와 비교
4. 일치하면 잠금 해제 ✅
```

### 보안 메커니즘

```
┌─────────────────────────────────────────────────┐
│          제스처 입력 (최대 10초)                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ 해시 생성 및   │
         │ 비교           │
         └───────┬───────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    ✅ 성공           ❌ 실패
    잠금 해제         시도 횟수 -1
                         │
                         ▼
                   ┌──────────────┐
                   │ 3회 실패?    │
                   └─────┬────────┘
                         │
                         ▼
                   🔒 30초 잠금
```

---

## 🚀 빠른 시작

### 1. 데모 실행

```bash
python3 security_demo.py
```

시뮬레이션 모드 (카메라 없이 테스트):
```bash
python3 security_demo.py --sim
```

### 2. 비밀번호 설정

1. 프로그램 실행 후 `S` 키 누르기
2. 설정 모드 진입
3. 4개의 제스처를 순서대로 입력
4. 자동으로 저장됨

**예시**:
```
제스처 입력 순서:
1. ✌️ 브이 사인
2. 👊 주먹
3. 👍 엄지척
4. 👌 OK 사인

→ 비밀번호 저장 완료!
```

### 3. 인증 시도

1. `A` 키를 눌러 인증 시작
2. 설정한 제스처를 순서대로 입력
3. 10초 이내에 입력 완료
4. 성공 시 잠금 해제

---

## 🎮 키보드 단축키

| 키 | 기능 | 설명 |
|----|------|------|
| `A` | 인증 시작 | 제스처 비밀번호 입력 모드 |
| `S` | 설정 모드 | 새 비밀번호 설정 |
| `R` | 초기화 | 비밀번호 완전 삭제 |
| `L` | 로그 보기 | 최근 인증 기록 출력 |
| `Q` | 종료 | 프로그램 종료 |

---

## 🔑 비밀번호 추천 패턴

### 레벨 1: 간단한 패턴 (낮은 보안)

```python
# 같은 제스처 반복
["THUMBS_UP", "THUMBS_UP", "V_SIGN", "V_SIGN"]

# 순차적 패턴
["ONE_FINGER", "TWO_FINGERS", "THREE_FINGERS", "FOUR_FINGERS"]
```

**보안 수준**: ⭐⭐☆☆☆ (약함)
**추천**: 테스트 용도만

### 레벨 2: 중간 패턴 (중간 보안)

```python
# 다양한 제스처
["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"]

# 역순 패턴
["FIVE_FINGERS", "FOUR_FINGERS", "THREE_FINGERS", "TWO_FINGERS"]
```

**보안 수준**: ⭐⭐⭐☆☆ (보통)
**추천**: 일반 용도

### 레벨 3: 복잡한 패턴 (높은 보안)

```python
# 불규칙한 조합
["OK_SIGN", "POINTING", "FIST", "OPEN_PALM"]

# 혼합 패턴
["V_SIGN", "FOUR_FINGERS", "FIST", "TWO_FINGERS"]
```

**보안 수준**: ⭐⭐⭐⭐☆ (강함)
**추천**: 중요한 보안

### 레벨 4: 매우 복잡한 패턴 (최고 보안)

```python
# 6개 제스처 (config 수정 필요)
["OK_SIGN", "POINTING", "V_SIGN", "FIST", "THUMBS_UP", "OPEN_PALM"]

# 예측 불가능한 조합
["THREE_FINGERS", "FIST", "OK_SIGN", "ONE_FINGER", "OPEN_PALM"]
```

**보안 수준**: ⭐⭐⭐⭐⭐ (매우 강함)
**추천**: 최고 보안이 필요한 경우

---

## ⚙️ 설정

### config.py 편집

```python
# 제스처 보안 시스템 설정
SECURITY_SETTINGS = {
    'password_length': 4,        # 비밀번호 길이 (제스처 개수)
    'max_attempts': 3,           # 최대 시도 횟수
    'timeout_seconds': 10,       # 제스처 입력 제한 시간 (초)
    'lockout_duration': 30,      # 잠금 지속 시간 (초)
}
```

### 설정 변경 예시

#### 더 긴 비밀번호 (보안 강화)

```python
SECURITY_SETTINGS = {
    'password_length': 6,  # 6개 제스처
    'max_attempts': 3,
    'timeout_seconds': 15,  # 시간 여유 증가
    'lockout_duration': 60,  # 잠금 시간 증가
}
```

#### 더 짧은 비밀번호 (편의성)

```python
SECURITY_SETTINGS = {
    'password_length': 3,  # 3개 제스처
    'max_attempts': 5,     # 시도 횟수 증가
    'timeout_seconds': 8,
    'lockout_duration': 20,
}
```

---

## 🔒 보안 기능

### 1. 해시 저장

비밀번호는 절대 평문으로 저장되지 않습니다.

```python
# 저장되는 내용 (gesture_password.json)
{
  "password_hash": "a1b2c3d4e5f6....",  # SHA-256 해시
  "password_length": 4,
  "created_at": "2025-11-12T10:30:00"
}
```

### 2. 무차별 대입 방지

- 최대 3회 시도 가능
- 3회 실패 시 30초 잠금
- 잠금 중에는 인증 시도 불가

### 3. 타임아웃

- 제스처 입력 시간 제한 (기본 10초)
- 시간 초과 시 실패 처리
- 다시 인증 시작 필요

### 4. 로그 기록

```json
[
  {
    "timestamp": "2025-11-12T10:30:00",
    "event": "success",
    "gesture_count": 4,
    "failed_attempts": 0
  },
  {
    "timestamp": "2025-11-12T10:31:00",
    "event": "failed",
    "gesture_count": 4,
    "failed_attempts": 1
  }
]
```

---

## 💡 사용 시나리오

### 시나리오 1: 스마트 홈 도어락

```python
from gesture_security import GestureSecurity
from smart_home_controller import SmartHomeController

# 보안 시스템 초기화
security = GestureSecurity(password_length=4)

# 인증 성공 시 문 열기
if security.verify_password(input_gestures):
    smart_home.turn_on("현관문")
    time.sleep(5)
    smart_home.turn_off("현관문")
```

### 시나리오 2: 컴퓨터 잠금 해제

```python
import subprocess

# 인증 성공 시 화면 잠금 해제
if security.verify_password(input_gestures):
    # 리눅스
    subprocess.run(["loginctl", "unlock-session"])

    # Windows
    # subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
```

### 시나리오 3: 금고 열기

```python
import RPi.GPIO as GPIO

LOCK_PIN = 24

# 인증 성공 시 금고 잠금 해제
if security.verify_password(input_gestures):
    GPIO.output(LOCK_PIN, GPIO.HIGH)  # 솔레노이드 잠금장치 해제
    print("금고가 열렸습니다!")
    time.sleep(3)
    GPIO.output(LOCK_PIN, GPIO.LOW)
```

---

## 🧪 테스트

### 단위 테스트

```bash
# 보안 시스템 모듈 테스트
python3 gesture_security.py
```

테스트 시나리오:
1. 비밀번호 설정
2. 성공적인 인증
3. 실패한 인증
4. 타임아웃

### 통합 테스트

```bash
# 전체 시스템 테스트
python3 security_demo.py --sim
```

---

## 🎨 UI 상태 표시

### 색상 코드

| 상태 | 배경색 | 의미 |
|------|--------|------|
| 🔒 LOCKED | 빨간색 | 잠금 상태 |
| 🔐 AUTH MODE | 노란색 | 인증 진행 중 |
| 🔓 UNLOCKED | 초록색 | 잠금 해제됨 |

### 화면 표시

```
┌─────────────────────────────────────────┐
│ 🔐 AUTH MODE               FPS: 15.2    │
│ SETUP MODE                              │
│ Gesture: V_SIGN                         │
│ Fingers: 2                              │
│                                         │
│                                         │
│           [손 랜드마크 표시]             │
│                                         │
│                                         │
│ Progress: 2/4          Timeout: 8s      │
│ Attempts: 2/3                           │
│                                         │
│ [A]uth | [S]etup | [R]eset | [Q]uit    │
└─────────────────────────────────────────┘
```

---

## 🐛 트러블슈팅

### 제스처가 인식되지 않음

**원인**: 손이 화면 밖으로 나감, 조명 부족

**해결방법**:
1. 손을 화면 중앙에 위치
2. 조명 환경 개선
3. 카메라와의 거리 조절 (50-100cm)

### 비밀번호 파일이 손상됨

**증상**: "비밀번호 로드 실패" 메시지

**해결방법**:
```bash
# 비밀번호 파일 삭제 후 재설정
rm gesture_password.json
python3 security_demo.py
# [S] 키를 눌러 새 비밀번호 설정
```

### 잠금이 자꾸 발생함

**원인**: 비밀번호를 잘못 입력하거나 타임아웃

**해결방법**:
1. `config.py`에서 `timeout_seconds` 증가
2. `max_attempts` 증가
3. 비밀번호를 더 간단한 패턴으로 변경

### 제스처 입력이 너무 빠름

**원인**: 제스처 쿨다운 시간 부족

**해결방법**:
```python
# security_demo.py 수정
self.gesture_cooldown = 1.5  # 기본 1.0에서 증가
```

---

## 📊 보안 분석

### 비밀번호 강도 계산

```
허용된 제스처 개수: 11개
비밀번호 길이: 4개

가능한 조합:
- 중복 허용: 11^4 = 14,641 가지
- 중복 불허: 11×10×9×8 = 7,920 가지

추측 시간 (무차별 대입):
- 제스처당 1초 소요 가정
- 3회 실패 시 30초 잠금

최악의 경우: 약 5-7일
```

### 보안 강화 방법

1. **비밀번호 길이 증가**
   ```python
   password_length = 6  # 14,641 → 1,771,561 조합
   ```

2. **잠금 시간 증가**
   ```python
   lockout_duration = 300  # 5분
   ```

3. **로그 모니터링**
   ```bash
   # 의심스러운 활동 감지
   python3 -c "
   from gesture_security import GestureSecurity
   security = GestureSecurity()
   security.print_logs(50)
   "
   ```

---

## 🔗 다른 시스템과 통합

### Home Assistant 연동

```python
import requests

def notify_home_assistant(event):
    url = "http://homeassistant.local:8123/api/services/notify/mobile_app"
    data = {
        "message": f"보안 이벤트: {event}",
        "title": "제스처 보안"
    }
    requests.post(url, json=data)

# 인증 실패 시 알림
if result == AuthResult.FAILED:
    notify_home_assistant("인증 실패")
```

### MQTT 연동

```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("mqtt.broker.com", 1883)

# 상태 발행
client.publish("home/security/status", "locked")
```

### 이메일 알림

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = "security@example.com"
    msg['To'] = "admin@example.com"

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("user", "password")
        server.send_message(msg)

# 잠금 상태 알림
if security.lockout_until:
    send_alert("보안 경고", "3회 인증 실패로 시스템이 잠겼습니다.")
```

---

## 📚 API 참조

### GestureSecurity 클래스

```python
class GestureSecurity:
    def __init__(self,
                 password_length=4,
                 max_attempts=3,
                 timeout_seconds=10,
                 lockout_duration=30):
        """보안 시스템 초기화"""

    def setup_password(self, gesture_sequence):
        """비밀번호 설정"""

    def start_authentication(self):
        """인증 시작"""

    def add_gesture(self, gesture):
        """제스처 입력"""

    def lock(self):
        """잠금"""

    def unlock(self):
        """잠금 해제"""

    def is_locked(self):
        """잠금 상태 확인"""

    def get_status(self):
        """상태 조회"""

    def reset_password(self):
        """비밀번호 초기화"""
```

---

## 🎓 고급 기능

### 다중 사용자 지원

```python
class MultiUserSecurity:
    def __init__(self):
        self.users = {}

    def add_user(self, username, password_sequence):
        self.users[username] = GestureSecurity()
        self.users[username].setup_password(password_sequence)

    def authenticate(self, username, input_sequence):
        if username in self.users:
            return self.users[username].verify_password(input_sequence)
        return False
```

### 제스처 시퀀스 녹화

```python
class GestureRecorder:
    def __init__(self):
        self.recorded_sequences = []

    def record_sequence(self, name, gestures):
        self.recorded_sequences.append({
            'name': name,
            'gestures': gestures,
            'created_at': datetime.now()
        })

    def replay_sequence(self, name):
        # 저장된 시퀀스 재생
        pass
```

---

## 🌟 실제 사용 예제

### 예제 1: 간단한 도어락

```python
#!/usr/bin/env python3
from gesture_security import GestureSecurity
import RPi.GPIO as GPIO

DOOR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_PIN, GPIO.OUT)

security = GestureSecurity(password_length=4)

# 비밀번호 설정 (최초 1회만)
# security.setup_password(["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"])

# 인증 시작
security.start_authentication()

# 제스처 입력 (카메라에서 읽어온 값)
gestures = ["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"]

for gesture in gestures:
    result = security.add_gesture(gesture)

if result == AuthResult.SUCCESS:
    print("문이 열렸습니다!")
    GPIO.output(DOOR_PIN, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(DOOR_PIN, GPIO.LOW)
else:
    print("인증 실패!")
```

---

## 📖 FAQ

### Q: 비밀번호를 잊어버렸어요!

**A**: `gesture_password.json` 파일을 삭제하고 새로 설정하세요:
```bash
rm gesture_password.json
python3 security_demo.py
```

### Q: 더 많은 제스처를 사용하고 싶어요

**A**: `config.py`에서 `password_length`를 증가시키세요:
```python
SECURITY_SETTINGS = {
    'password_length': 6,  # 4에서 6으로 증가
    # ...
}
```

### Q: 실패 횟수를 늘리고 싶어요

**A**: `max_attempts`를 수정하세요:
```python
SECURITY_SETTINGS = {
    'max_attempts': 5,  # 3에서 5로 증가
    # ...
}
```

### Q: 보안 로그는 어디에 저장되나요?

**A**: `security_log.json` 파일에 저장됩니다. 최근 100개 로그가 유지됩니다.

---

**🔒 안전한 제스처 인증을 경험하세요!**
