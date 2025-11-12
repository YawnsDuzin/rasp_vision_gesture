#!/usr/bin/env python3
"""
제스처 액션 매핑 모듈

제스처를 스마트 홈 제어 및 음악 플레이어 액션으로 매핑합니다.
"""

from enum import Enum
from collections import deque
import time


class GestureType(Enum):
    """제스처 타입"""
    FIST = "FIST"
    OPEN_PALM = "OPEN_PALM"
    THUMBS_UP = "THUMBS_UP"
    V_SIGN = "V_SIGN"
    OK_SIGN = "OK_SIGN"
    POINTING = "POINTING"
    ONE_FINGER = "ONE_FINGER"
    TWO_FINGERS = "TWO_FINGERS"
    THREE_FINGERS = "THREE_FINGERS"
    FOUR_FINGERS = "FOUR_FINGERS"
    FIVE_FINGERS = "FIVE_FINGERS"
    UNKNOWN = "UNKNOWN"


class ActionType(Enum):
    """액션 타입"""
    # 스마트 홈 액션
    LIGHT_ON = "light_on"
    LIGHT_OFF = "light_off"
    LIGHT_TOGGLE = "light_toggle"
    ALL_ON = "all_on"
    ALL_OFF = "all_off"
    FAN_TOGGLE = "fan_toggle"
    AC_TOGGLE = "ac_toggle"
    SET_BRIGHTNESS = "set_brightness"

    # 음악 플레이어 액션
    PLAY_PAUSE = "play_pause"
    STOP = "stop"
    NEXT_TRACK = "next_track"
    PREV_TRACK = "prev_track"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    SET_VOLUME = "set_volume"

    # 시스템 액션
    NONE = "none"


class GestureActionMapper:
    """제스처 액션 매퍼"""

    def __init__(self, smart_home_controller=None, music_player=None):
        """
        초기화

        Args:
            smart_home_controller: 스마트 홈 컨트롤러 인스턴스
            music_player: 음악 플레이어 인스턴스
        """
        self.smart_home = smart_home_controller
        self.music_player = music_player

        # 기본 제스처 매핑
        self.gesture_mappings = {
            # 왼손 제스처 → 스마트 홈 제어
            ('Left', GestureType.FIST): ActionType.ALL_OFF,
            ('Left', GestureType.OPEN_PALM): ActionType.ALL_ON,
            ('Left', GestureType.THUMBS_UP): ActionType.LIGHT_TOGGLE,
            ('Left', GestureType.V_SIGN): ActionType.FAN_TOGGLE,
            ('Left', GestureType.OK_SIGN): ActionType.AC_TOGGLE,

            # 오른손 제스처 → 음악 플레이어 제어
            ('Right', GestureType.FIST): ActionType.STOP,
            ('Right', GestureType.THUMBS_UP): ActionType.PLAY_PAUSE,
            ('Right', GestureType.POINTING): ActionType.NEXT_TRACK,
            ('Right', GestureType.V_SIGN): ActionType.PREV_TRACK,
            ('Right', GestureType.OPEN_PALM): ActionType.VOLUME_UP,

            # 손가락 개수 → 볼륨/밝기 제어
            ('Right', GestureType.ONE_FINGER): (ActionType.SET_VOLUME, 20),
            ('Right', GestureType.TWO_FINGERS): (ActionType.SET_VOLUME, 40),
            ('Right', GestureType.THREE_FINGERS): (ActionType.SET_VOLUME, 60),
            ('Right', GestureType.FOUR_FINGERS): (ActionType.SET_VOLUME, 80),
            ('Right', GestureType.FIVE_FINGERS): (ActionType.SET_VOLUME, 100),

            ('Left', GestureType.ONE_FINGER): (ActionType.SET_BRIGHTNESS, 20),
            ('Left', GestureType.TWO_FINGERS): (ActionType.SET_BRIGHTNESS, 40),
            ('Left', GestureType.THREE_FINGERS): (ActionType.SET_BRIGHTNESS, 60),
            ('Left', GestureType.FOUR_FINGERS): (ActionType.SET_BRIGHTNESS, 80),
            ('Left', GestureType.FIVE_FINGERS): (ActionType.SET_BRIGHTNESS, 100),
        }

        # 제스처 히스토리 (중복 실행 방지)
        self.last_gesture = None
        self.last_action_time = 0
        self.action_cooldown = 1.0  # 초

        # 실행된 액션 로그
        self.action_history = deque(maxlen=10)

    def map_gesture_to_action(self, handedness, gesture):
        """
        제스처를 액션으로 매핑

        Args:
            handedness: 손 방향 ('Left' or 'Right')
            gesture: 제스처 이름 (문자열)

        Returns:
            (ActionType, parameter) 튜플 또는 None
        """
        try:
            gesture_enum = GestureType[gesture]
        except KeyError:
            return None

        key = (handedness, gesture_enum)

        if key in self.gesture_mappings:
            mapping = self.gesture_mappings[key]

            # 튜플이면 (액션, 파라미터)
            if isinstance(mapping, tuple):
                return mapping
            else:
                return (mapping, None)

        return None

    def execute_action(self, handedness, gesture, force=False):
        """
        제스처에 해당하는 액션 실행

        Args:
            handedness: 손 방향
            gesture: 제스처 이름
            force: 쿨다운 무시

        Returns:
            실행 성공 여부
        """
        current_time = time.time()

        # 쿨다운 체크 (같은 제스처 연속 실행 방지)
        if not force:
            if (handedness, gesture) == self.last_gesture:
                if current_time - self.last_action_time < self.action_cooldown:
                    return False

        # 액션 매핑
        action_info = self.map_gesture_to_action(handedness, gesture)

        if not action_info:
            return False

        action_type, param = action_info

        # 액션 실행
        success = self._execute_specific_action(action_type, param)

        if success:
            self.last_gesture = (handedness, gesture)
            self.last_action_time = current_time

            # 로그 기록
            self.action_history.append({
                'time': current_time,
                'handedness': handedness,
                'gesture': gesture,
                'action': action_type.value,
                'param': param
            })

        return success

    def _execute_specific_action(self, action_type, param):
        """
        특정 액션 실행

        Args:
            action_type: ActionType
            param: 파라미터

        Returns:
            성공 여부
        """
        # 스마트 홈 액션
        if action_type == ActionType.ALL_ON:
            if self.smart_home:
                self.smart_home.turn_on_all()
                return True

        elif action_type == ActionType.ALL_OFF:
            if self.smart_home:
                self.smart_home.turn_off_all()
                return True

        elif action_type == ActionType.LIGHT_TOGGLE:
            if self.smart_home:
                # 첫 번째 조명 토글 (또는 모든 조명)
                devices = list(self.smart_home.devices.keys())
                if devices:
                    self.smart_home.toggle(devices[0])
                    return True

        elif action_type == ActionType.FAN_TOGGLE:
            if self.smart_home and "선풍기" in self.smart_home.devices:
                self.smart_home.toggle("선풍기")
                return True

        elif action_type == ActionType.AC_TOGGLE:
            if self.smart_home and "에어컨" in self.smart_home.devices:
                self.smart_home.toggle("에어컨")
                return True

        elif action_type == ActionType.SET_BRIGHTNESS:
            if self.smart_home and param is not None:
                devices = list(self.smart_home.devices.keys())
                if devices:
                    self.smart_home.set_brightness(devices[0], param)
                    return True

        # 음악 플레이어 액션
        elif action_type == ActionType.PLAY_PAUSE:
            if self.music_player:
                self.music_player.toggle_play_pause()
                return True

        elif action_type == ActionType.STOP:
            if self.music_player:
                self.music_player.stop()
                return True

        elif action_type == ActionType.NEXT_TRACK:
            if self.music_player:
                self.music_player.next_track()
                return True

        elif action_type == ActionType.PREV_TRACK:
            if self.music_player:
                self.music_player.previous_track()
                return True

        elif action_type == ActionType.VOLUME_UP:
            if self.music_player:
                self.music_player.volume_up()
                return True

        elif action_type == ActionType.VOLUME_DOWN:
            if self.music_player:
                self.music_player.volume_down()
                return True

        elif action_type == ActionType.SET_VOLUME:
            if self.music_player and param is not None:
                self.music_player.set_volume(param)
                return True

        return False

    def get_gesture_help(self):
        """
        제스처 도움말 반환

        Returns:
            도움말 문자열
        """
        help_text = """
╔═══════════════════════════════════════════════════════════════╗
║                    제스처 컨트롤 가이드                        ║
╠═══════════════════════════════════════════════════════════════╣
║ [왼손 - 스마트 홈 제어]                                        ║
║  👊 주먹           → 모든 디바이스 끄기                        ║
║  🖐️ 손바닥 펴기    → 모든 디바이스 켜기                        ║
║  👍 엄지척         → 조명 토글                                 ║
║  ✌️ 브이 사인      → 선풍기 토글                               ║
║  👌 OK 사인        → 에어컨 토글                               ║
║  1-5 손가락       → 조명 밝기 (20%, 40%, 60%, 80%, 100%)      ║
║                                                                ║
║ [오른손 - 음악 플레이어 제어]                                  ║
║  👊 주먹           → 음악 정지                                 ║
║  👍 엄지척         → 재생/일시정지                             ║
║  ☝️ 가리키기       → 다음 곡                                   ║
║  ✌️ 브이 사인      → 이전 곡                                   ║
║  🖐️ 손바닥 펴기    → 볼륨 업                                   ║
║  1-5 손가락       → 볼륨 설정 (20%, 40%, 60%, 80%, 100%)      ║
╚═══════════════════════════════════════════════════════════════╝
        """
        return help_text

    def print_help(self):
        """도움말 출력"""
        print(self.get_gesture_help())

    def print_action_history(self):
        """액션 히스토리 출력"""
        print("\n" + "=" * 60)
        print("📜 최근 실행된 액션")
        print("=" * 60)

        if not self.action_history:
            print("실행된 액션이 없습니다.")
        else:
            for action in self.action_history:
                time_str = time.strftime('%H:%M:%S', time.localtime(action['time']))
                param_str = f" ({action['param']})" if action['param'] else ""
                print(f"[{time_str}] {action['handedness']:5} {action['gesture']:15} → {action['action']}{param_str}")

        print("=" * 60 + "\n")


# 테스트 코드
def main():
    """테스트 함수"""
    from smart_home_controller import SmartHomeController, DeviceType
    from music_player_controller import MusicPlayerController
    import time

    print("🎮 제스처 액션 매퍼 테스트\n")

    # 컨트롤러 초기화
    smart_home = SmartHomeController(simulation_mode=True)
    smart_home.add_device("거실 조명", DeviceType.LIGHT, pin=17)
    smart_home.add_device("선풍기", DeviceType.FAN, pin=22)
    smart_home.add_device("에어컨", DeviceType.AC, pin=23)

    music_player = MusicPlayerController(simulation_mode=True)

    # 매퍼 초기화
    mapper = GestureActionMapper(smart_home, music_player)

    # 도움말 출력
    mapper.print_help()

    # 테스트 시나리오
    print("📝 테스트 시나리오 시작\n")

    test_gestures = [
        ('Left', 'OPEN_PALM', "모든 디바이스 켜기"),
        ('Right', 'THUMBS_UP', "음악 재생"),
        ('Left', 'V_SIGN', "선풍기 토글"),
        ('Right', 'THREE_FINGERS', "볼륨 60%"),
        ('Left', 'FOUR_FINGERS', "조명 밝기 80%"),
        ('Right', 'POINTING', "다음 곡"),
        ('Left', 'FIST', "모든 디바이스 끄기"),
        ('Right', 'FIST', "음악 정지"),
    ]

    for idx, (hand, gesture, description) in enumerate(test_gestures, 1):
        print(f"{idx}. {description} ({hand} - {gesture})")
        mapper.execute_action(hand, gesture)
        time.sleep(1.5)
        print()

    # 상태 출력
    smart_home.print_status()
    music_player.print_status()

    # 액션 히스토리
    mapper.print_action_history()

    # 정리
    smart_home.cleanup()
    music_player.cleanup()


if __name__ == "__main__":
    main()
