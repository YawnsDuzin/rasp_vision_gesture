"""
라즈베리파이 제스처 인식 시스템 설정 파일
"""

# RTSP 카메라 설정
RTSP_URL = "rtsp://admin:password@192.168.1.100:554/stream1"
# 예시:
# RTSP_URL = "rtsp://192.168.1.100:554/stream1"  # 인증 없음
# RTSP_URL = "rtsp://username:password@192.168.1.100:554/live/main"

# 비디오 처리 설정
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 15
BUFFER_SIZE = 1

# MediaPipe 설정
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
MODEL_COMPLEXITY = 0  # 0: 빠름, 1: 정확함

# 라즈베리파이 모델에 따른 최적화 프리셋
DEVICE_PRESETS = {
    'raspberry_pi_4': {
        'frame_width': 640,
        'frame_height': 480,
        'fps': 15,
        'model_complexity': 0,
        'max_num_hands': 2
    },
    'raspberry_pi_3': {
        'frame_width': 480,
        'frame_height': 360,
        'fps': 10,
        'model_complexity': 0,
        'max_num_hands': 1
    },
    'raspberry_pi_zero': {
        'frame_width': 320,
        'frame_height': 240,
        'fps': 5,
        'model_complexity': 0,
        'max_num_hands': 1
    }
}

# 현재 사용 중인 디바이스 설정
CURRENT_DEVICE = 'raspberry_pi_4'

# 디스플레이 설정
SHOW_FPS = True
SHOW_LANDMARKS = True
SHOW_HAND_LABEL = True

# 로깅 설정
ENABLE_LOGGING = True
LOG_FILE = 'gesture_log.txt'

# 제스처 인식 설정
GESTURE_CONFIDENCE_THRESHOLD = 0.7
GESTURE_HOLD_FRAMES = 5  # 제스처가 몇 프레임 지속되어야 인식할지

# ===== 스마트 홈 허브 설정 =====

# 스마트 홈 디바이스 설정
# GPIO 핀 번호는 BCM 모드 기준입니다
SMART_HOME_DEVICES = [
    {
        'name': '거실 조명',
        'type': 'LIGHT',
        'pin': 17,
        'initial_state': False
    },
    {
        'name': '침실 조명',
        'type': 'LIGHT',
        'pin': 27,
        'initial_state': False
    },
    {
        'name': '선풍기',
        'type': 'FAN',
        'pin': 22,
        'initial_state': False
    },
    {
        'name': '에어컨',
        'type': 'AC',
        'pin': 23,
        'initial_state': False
    },
    # 필요한 디바이스를 추가하세요
    # {
    #     'name': '주방 조명',
    #     'type': 'LIGHT',
    #     'pin': 24,
    #     'initial_state': False
    # },
]

# 음악 플레이어 설정
MUSIC_DIRECTORY = "~/Music"  # 음악 파일 디렉토리
DEFAULT_VOLUME = 70  # 기본 볼륨 (0-100)

# 제스처 액션 쿨다운 (초)
# 같은 제스처를 연속으로 인식하지 않도록 하는 최소 시간 간격
ACTION_COOLDOWN = 1.0

# ===== 제스처 보안 시스템 설정 =====

# 제스처 비밀번호 설정
SECURITY_SETTINGS = {
    'password_length': 4,        # 비밀번호 길이 (제스처 개수)
    'max_attempts': 3,           # 최대 시도 횟수
    'timeout_seconds': 10,       # 제스처 입력 제한 시간 (초)
    'lockout_duration': 30,      # 잠금 지속 시간 (초)
}

# 추천 비밀번호 패턴 (예시)
EXAMPLE_PASSWORDS = [
    # 간단한 패턴
    ["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"],
    ["THUMBS_UP", "THUMBS_UP", "V_SIGN", "V_SIGN"],

    # 숫자 패턴 (손가락 개수)
    ["ONE_FINGER", "TWO_FINGERS", "THREE_FINGERS", "FOUR_FINGERS"],
    ["FIVE_FINGERS", "FOUR_FINGERS", "THREE_FINGERS", "TWO_FINGERS"],

    # 복잡한 패턴
    ["OK_SIGN", "POINTING", "FIST", "OPEN_PALM"],
    ["V_SIGN", "OK_SIGN", "THUMBS_UP", "POINTING"],
]
