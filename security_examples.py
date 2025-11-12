#!/usr/bin/env python3
"""
제스처 보안 시스템 예제 모음

다양한 사용 시나리오의 예제 코드를 제공합니다.
"""

import time
from gesture_security import GestureSecurity, AuthResult


def example_1_basic_usage():
    """예제 1: 기본 사용법"""
    print("\n" + "=" * 60)
    print("예제 1: 기본 사용법")
    print("=" * 60)

    # 보안 시스템 생성
    security = GestureSecurity(
        password_length=4,
        max_attempts=3,
        timeout_seconds=10
    )

    # 비밀번호 설정
    password = ["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"]
    security.setup_password(password)

    # 인증 시작
    security.start_authentication()

    # 제스처 입력
    for gesture in password:
        result = security.add_gesture(gesture)
        time.sleep(0.3)

    if result == AuthResult.SUCCESS:
        print("\n✅ 인증 성공!")
    else:
        print("\n❌ 인증 실패!")


def example_2_simple_doorlock():
    """예제 2: 간단한 도어락 시뮬레이션"""
    print("\n" + "=" * 60)
    print("예제 2: 간단한 도어락")
    print("=" * 60)

    class SimpleDoorLock:
        def __init__(self):
            self.security = GestureSecurity(password_length=4)
            self.is_door_open = False

        def setup(self, password):
            """도어락 비밀번호 설정"""
            return self.security.setup_password(password)

        def unlock(self, input_gestures):
            """도어락 열기"""
            self.security.start_authentication()

            for gesture in input_gestures:
                result = self.security.add_gesture(gesture)

            if result == AuthResult.SUCCESS:
                self.is_door_open = True
                print("🚪 문이 열렸습니다!")
                print("   3초 후 자동으로 닫힙니다...")
                time.sleep(3)
                self.close()
                return True
            else:
                print("🚫 잘못된 비밀번호입니다!")
                return False

        def close(self):
            """도어락 닫기"""
            self.is_door_open = False
            self.security.lock()
            print("🔒 문이 잠겼습니다.")

    # 도어락 사용
    door = SimpleDoorLock()
    door.setup(["THUMBS_UP", "V_SIGN", "OK_SIGN", "FIST"])

    # 올바른 비밀번호로 열기
    print("\n[시도 1] 올바른 비밀번호")
    door.unlock(["THUMBS_UP", "V_SIGN", "OK_SIGN", "FIST"])

    # 잘못된 비밀번호로 시도
    print("\n[시도 2] 잘못된 비밀번호")
    door.unlock(["FIST", "FIST", "FIST", "FIST"])


def example_3_multiple_attempts():
    """예제 3: 여러 번 시도 및 잠금"""
    print("\n" + "=" * 60)
    print("예제 3: 여러 번 시도 및 자동 잠금")
    print("=" * 60)

    security = GestureSecurity(
        password_length=4,
        max_attempts=3,
        timeout_seconds=10,
        lockout_duration=5  # 테스트를 위해 5초로 설정
    )

    # 비밀번호 설정
    correct_password = ["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"]
    security.setup_password(correct_password)

    # 3번 틀리면 잠김
    for attempt in range(1, 4):
        print(f"\n[시도 {attempt}] 잘못된 비밀번호 입력")
        security.start_authentication()

        wrong_password = ["FIST", "FIST", "FIST", "FIST"]
        for gesture in wrong_password:
            result = security.add_gesture(gesture)

        if result == AuthResult.FAILED:
            print(f"   ❌ 실패! 남은 시도: {3 - attempt}회")

    # 잠금 상태 확인
    status = security.get_status()
    if status['is_locked_out']:
        print(f"\n🔒 시스템이 {status['lockout_remaining']}초 동안 잠겼습니다!")

        # 잠금 해제 대기
        print("   잠금 해제 대기 중...")
        time.sleep(6)

        print("\n✅ 잠금이 해제되었습니다. 다시 시도할 수 있습니다.")


def example_4_timeout():
    """예제 4: 타임아웃 처리"""
    print("\n" + "=" * 60)
    print("예제 4: 타임아웃")
    print("=" * 60)

    security = GestureSecurity(
        password_length=4,
        max_attempts=3,
        timeout_seconds=3  # 3초로 짧게 설정
    )

    password = ["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"]
    security.setup_password(password)

    # 인증 시작
    security.start_authentication()

    # 일부만 입력하고 대기
    security.add_gesture("V_SIGN")
    security.add_gesture("FIST")
    print("\n   제스처 입력을 멈추고 3초 대기...")
    time.sleep(4)

    # 타임아웃 후 제스처 입력
    result = security.add_gesture("THUMBS_UP")

    if result == AuthResult.TIMEOUT:
        print("\n⏱️  타임아웃! 처음부터 다시 입력하세요.")


def example_5_password_patterns():
    """예제 5: 다양한 비밀번호 패턴"""
    print("\n" + "=" * 60)
    print("예제 5: 다양한 비밀번호 패턴")
    print("=" * 60)

    patterns = [
        {
            'name': '간단한 패턴',
            'password': ["V_SIGN", "V_SIGN", "FIST", "FIST"],
            'strength': '⭐⭐☆☆☆'
        },
        {
            'name': '순차 숫자',
            'password': ["ONE_FINGER", "TWO_FINGERS", "THREE_FINGERS", "FOUR_FINGERS"],
            'strength': '⭐⭐☆☆☆'
        },
        {
            'name': '다양한 제스처',
            'password': ["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"],
            'strength': '⭐⭐⭐☆☆'
        },
        {
            'name': '복잡한 조합',
            'password': ["OK_SIGN", "POINTING", "FIST", "OPEN_PALM"],
            'strength': '⭐⭐⭐⭐☆'
        },
    ]

    for pattern in patterns:
        print(f"\n패턴: {pattern['name']}")
        print(f"강도: {pattern['strength']}")
        print(f"제스처: {' → '.join(pattern['password'])}")


def example_6_custom_configuration():
    """예제 6: 커스텀 설정"""
    print("\n" + "=" * 60)
    print("예제 6: 커스텀 설정")
    print("=" * 60)

    # 짧은 비밀번호, 많은 시도 횟수
    easy_mode = GestureSecurity(
        password_length=3,
        max_attempts=5,
        timeout_seconds=15,
        lockout_duration=10
    )

    print("\n[Easy 모드]")
    print(f"  비밀번호 길이: 3")
    print(f"  최대 시도: 5회")
    print(f"  타임아웃: 15초")

    # 긴 비밀번호, 적은 시도 횟수
    hard_mode = GestureSecurity(
        password_length=6,
        max_attempts=2,
        timeout_seconds=8,
        lockout_duration=60
    )

    print("\n[Hard 모드]")
    print(f"  비밀번호 길이: 6")
    print(f"  최대 시도: 2회")
    print(f"  타임아웃: 8초")
    print(f"  잠금 시간: 60초")


def example_7_log_monitoring():
    """예제 7: 로그 모니터링"""
    print("\n" + "=" * 60)
    print("예제 7: 로그 모니터링")
    print("=" * 60)

    security = GestureSecurity(password_length=4)
    password = ["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"]
    security.setup_password(password)

    # 여러 인증 시도 (성공/실패 혼합)
    attempts = [
        (["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"], "성공"),
        (["FIST", "FIST", "FIST", "FIST"], "실패"),
        (["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"], "성공"),
        (["OPEN_PALM", "OPEN_PALM", "OPEN_PALM", "OPEN_PALM"], "실패"),
    ]

    for gestures, expected in attempts:
        security.start_authentication()
        for gesture in gestures:
            result = security.add_gesture(gesture)
        print(f"  인증 시도: {expected}")
        time.sleep(0.5)

    # 로그 출력
    print("\n" + "=" * 60)
    security.print_logs()


def example_8_integration_with_smart_home():
    """예제 8: 스마트 홈 통합"""
    print("\n" + "=" * 60)
    print("예제 8: 스마트 홈 통합 시뮬레이션")
    print("=" * 60)

    class SecureSmartHome:
        def __init__(self):
            self.security = GestureSecurity(password_length=4)
            self.devices = {
                '현관문': False,
                '거실 조명': False,
                '보안 시스템': True
            }

        def setup_password(self, password):
            return self.security.setup_password(password)

        def authenticate_and_control(self, input_gestures, action):
            """인증 후 기기 제어"""
            self.security.start_authentication()

            for gesture in input_gestures:
                result = self.security.add_gesture(gesture)

            if result == AuthResult.SUCCESS:
                print(f"\n✅ 인증 성공! {action} 실행")
                self._execute_action(action)
                return True
            else:
                print(f"\n❌ 인증 실패! {action} 차단됨")
                return False

        def _execute_action(self, action):
            """액션 실행"""
            if action == "unlock_door":
                self.devices['현관문'] = True
                print("   🚪 현관문 열림")
            elif action == "lights_on":
                self.devices['거실 조명'] = True
                print("   💡 거실 조명 켜짐")
            elif action == "disable_security":
                self.devices['보안 시스템'] = False
                print("   🔓 보안 시스템 해제")

        def print_status(self):
            """상태 출력"""
            print("\n[스마트 홈 상태]")
            for device, state in self.devices.items():
                status = "🟢 ON" if state else "🔴 OFF"
                print(f"  {device}: {status}")

    # 스마트 홈 사용
    home = SecureSmartHome()
    password = ["THUMBS_UP", "V_SIGN", "OK_SIGN", "FIST"]
    home.setup_password(password)

    # 현관문 열기
    print("\n[시나리오 1] 현관문 열기")
    home.authenticate_and_control(password, "unlock_door")

    # 조명 켜기
    print("\n[시나리오 2] 조명 켜기")
    home.authenticate_and_control(password, "lights_on")

    # 보안 시스템 해제
    print("\n[시나리오 3] 보안 시스템 해제")
    home.authenticate_and_control(password, "disable_security")

    # 상태 확인
    home.print_status()


def example_9_password_strength():
    """예제 9: 비밀번호 강도 분석"""
    print("\n" + "=" * 60)
    print("예제 9: 비밀번호 강도 분석")
    print("=" * 60)

    def calculate_combinations(length, allow_duplicates=True):
        """가능한 조합 계산"""
        valid_gestures = 11  # 사용 가능한 제스처 수

        if allow_duplicates:
            return valid_gestures ** length
        else:
            result = 1
            for i in range(length):
                result *= (valid_gestures - i)
            return result

    def estimate_crack_time(combinations, attempts_per_minute=20):
        """추측 시간 예상"""
        minutes = combinations / attempts_per_minute
        hours = minutes / 60
        days = hours / 24
        return {
            'minutes': minutes,
            'hours': hours,
            'days': days
        }

    # 다양한 길이의 비밀번호 분석
    for length in [3, 4, 5, 6]:
        combinations = calculate_combinations(length, allow_duplicates=True)
        time_est = estimate_crack_time(combinations)

        print(f"\n비밀번호 길이: {length}")
        print(f"  가능한 조합: {combinations:,}가지")
        print(f"  추측 시간 (최악): {time_est['days']:.1f}일")

        if time_est['days'] < 1:
            print(f"  보안 등급: ⚠️ 약함")
        elif time_est['days'] < 7:
            print(f"  보안 등급: ⭐⭐ 보통")
        elif time_est['days'] < 30:
            print(f"  보안 등급: ⭐⭐⭐ 좋음")
        else:
            print(f"  보안 등급: ⭐⭐⭐⭐ 매우 좋음")


def main():
    """모든 예제 실행"""
    examples = [
        ("기본 사용법", example_1_basic_usage),
        ("간단한 도어락", example_2_simple_doorlock),
        ("여러 번 시도 및 잠금", example_3_multiple_attempts),
        ("타임아웃", example_4_timeout),
        ("다양한 비밀번호 패턴", example_5_password_patterns),
        ("커스텀 설정", example_6_custom_configuration),
        ("로그 모니터링", example_7_log_monitoring),
        ("스마트 홈 통합", example_8_integration_with_smart_home),
        ("비밀번호 강도 분석", example_9_password_strength),
    ]

    print("🔐 제스처 보안 시스템 예제 모음")
    print("=" * 60)

    for idx, (name, func) in enumerate(examples, 1):
        print(f"\n{idx}. {name}")

    print("\n0. 모든 예제 실행")
    print("Q. 종료")

    choice = input("\n선택하세요: ").strip()

    if choice.lower() == 'q':
        return
    elif choice == '0':
        for _, func in examples:
            func()
            input("\n계속하려면 Enter를 누르세요...")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                examples[idx][1]()
            else:
                print("잘못된 선택입니다.")
        except ValueError:
            print("잘못된 입력입니다.")


if __name__ == "__main__":
    main()
