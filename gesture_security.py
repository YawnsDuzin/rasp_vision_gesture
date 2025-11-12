#!/usr/bin/env python3
"""
제스처 기반 보안 인증 시스템

제스처 시퀀스를 비밀번호로 사용하여 잠금을 해제하는 보안 시스템입니다.
예: 브이 → 주먹 → 엄지척 → OK
"""

import time
import json
import hashlib
from datetime import datetime
from collections import deque
from enum import Enum
import os


class SecurityState(Enum):
    """보안 상태"""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    SETUP_MODE = "setup_mode"
    AUTH_MODE = "auth_mode"


class AuthResult(Enum):
    """인증 결과"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    TOO_MANY_ATTEMPTS = "too_many_attempts"
    IN_PROGRESS = "in_progress"


class GestureSecurity:
    """제스처 보안 시스템"""

    def __init__(self,
                 password_length=4,
                 max_attempts=3,
                 timeout_seconds=10,
                 lockout_duration=30,
                 log_file="security_log.json"):
        """
        초기화

        Args:
            password_length: 비밀번호 길이 (제스처 개수)
            max_attempts: 최대 시도 횟수
            timeout_seconds: 제스처 입력 제한 시간 (초)
            lockout_duration: 잠금 지속 시간 (초)
            log_file: 로그 파일 경로
        """
        self.password_length = password_length
        self.max_attempts = max_attempts
        self.timeout_seconds = timeout_seconds
        self.lockout_duration = lockout_duration
        self.log_file = log_file

        # 상태 관리
        self.state = SecurityState.LOCKED
        self.password_hash = None
        self.current_input = []
        self.input_start_time = None
        self.failed_attempts = 0
        self.lockout_until = None

        # 제스처 히스토리
        self.gesture_history = deque(maxlen=10)

        # 비밀번호 파일
        self.password_file = "gesture_password.json"
        self._load_password()

        # 허용된 제스처 목록
        self.valid_gestures = [
            "FIST", "OPEN_PALM", "THUMBS_UP", "V_SIGN",
            "OK_SIGN", "POINTING", "ONE_FINGER", "TWO_FINGERS",
            "THREE_FINGERS", "FOUR_FINGERS", "FIVE_FINGERS"
        ]

    def _hash_password(self, gesture_sequence):
        """
        제스처 시퀀스를 해시로 변환

        Args:
            gesture_sequence: 제스처 리스트

        Returns:
            해시 문자열
        """
        sequence_str = "|".join(gesture_sequence)
        return hashlib.sha256(sequence_str.encode()).hexdigest()

    def _save_password(self):
        """비밀번호를 파일에 저장"""
        data = {
            'password_hash': self.password_hash,
            'password_length': self.password_length,
            'created_at': datetime.now().isoformat()
        }

        with open(self.password_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ 비밀번호가 저장되었습니다: {self.password_file}")

    def _load_password(self):
        """파일에서 비밀번호 로드"""
        if os.path.exists(self.password_file):
            try:
                with open(self.password_file, 'r') as f:
                    data = json.load(f)
                    self.password_hash = data.get('password_hash')
                    self.password_length = data.get('password_length', self.password_length)
                    print(f"✅ 비밀번호가 로드되었습니다: {self.password_file}")
                    return True
            except Exception as e:
                print(f"⚠️  비밀번호 로드 실패: {e}")

        print("⚠️  저장된 비밀번호가 없습니다. 설정 모드를 실행하세요.")
        return False

    def setup_password(self, gesture_sequence):
        """
        비밀번호 설정

        Args:
            gesture_sequence: 제스처 시퀀스 리스트

        Returns:
            성공 여부
        """
        if len(gesture_sequence) != self.password_length:
            print(f"❌ 비밀번호는 정확히 {self.password_length}개의 제스처여야 합니다.")
            return False

        # 유효한 제스처인지 확인
        for gesture in gesture_sequence:
            if gesture not in self.valid_gestures:
                print(f"❌ 유효하지 않은 제스처: {gesture}")
                return False

        # 비밀번호 해시 저장
        self.password_hash = self._hash_password(gesture_sequence)
        self._save_password()

        print(f"✅ 제스처 비밀번호가 설정되었습니다!")
        print(f"   길이: {self.password_length}개 제스처")
        print(f"   패턴: {' → '.join(gesture_sequence)}")

        self.state = SecurityState.LOCKED
        return True

    def start_authentication(self):
        """인증 시작"""
        # 잠금 상태 확인
        if self.lockout_until:
            remaining = self.lockout_until - time.time()
            if remaining > 0:
                print(f"🔒 일시적으로 잠겼습니다. {remaining:.0f}초 후 다시 시도하세요.")
                return False

        # 비밀번호 설정 확인
        if not self.password_hash:
            print("❌ 비밀번호가 설정되지 않았습니다. 먼저 설정 모드를 실행하세요.")
            return False

        self.state = SecurityState.AUTH_MODE
        self.current_input = []
        self.input_start_time = time.time()
        print(f"\n🔐 인증 시작! {self.password_length}개의 제스처를 입력하세요.")
        print(f"   제한 시간: {self.timeout_seconds}초")
        return True

    def add_gesture(self, gesture, handedness="Right"):
        """
        제스처 입력

        Args:
            gesture: 제스처 이름
            handedness: 손 방향 (사용 안 함, 호환성 위해 유지)

        Returns:
            AuthResult
        """
        # 인증 모드가 아니면 무시
        if self.state != SecurityState.AUTH_MODE:
            return AuthResult.IN_PROGRESS

        # 유효한 제스처인지 확인
        if gesture not in self.valid_gestures:
            return AuthResult.IN_PROGRESS

        # 타임아웃 확인
        elapsed = time.time() - self.input_start_time
        if elapsed > self.timeout_seconds:
            print(f"\n⏱️  시간 초과! ({elapsed:.1f}초)")
            self._handle_failed_attempt()
            return AuthResult.TIMEOUT

        # 제스처 추가
        self.current_input.append(gesture)
        print(f"   입력됨: {gesture} ({len(self.current_input)}/{self.password_length})")

        # 비밀번호 길이에 도달했는지 확인
        if len(self.current_input) >= self.password_length:
            return self._verify_password()

        return AuthResult.IN_PROGRESS

    def _verify_password(self):
        """
        비밀번호 검증

        Returns:
            AuthResult
        """
        input_hash = self._hash_password(self.current_input)

        if input_hash == self.password_hash:
            # 성공!
            self.state = SecurityState.UNLOCKED
            self.failed_attempts = 0
            self.lockout_until = None

            print("\n✅ 인증 성공!")
            self._log_event("success", self.current_input)

            return AuthResult.SUCCESS

        else:
            # 실패
            print("\n❌ 잘못된 비밀번호!")
            self._handle_failed_attempt()
            return AuthResult.FAILED

    def _handle_failed_attempt(self):
        """실패한 시도 처리"""
        self.failed_attempts += 1
        remaining = self.max_attempts - self.failed_attempts

        self._log_event("failed", self.current_input)

        if self.failed_attempts >= self.max_attempts:
            # 최대 시도 횟수 초과
            self.lockout_until = time.time() + self.lockout_duration
            print(f"🚫 최대 시도 횟수 초과! {self.lockout_duration}초 동안 잠깁니다.")
            self.state = SecurityState.LOCKED
            self.failed_attempts = 0
        else:
            print(f"   남은 시도 횟수: {remaining}회")
            self.state = SecurityState.LOCKED
            self.current_input = []

    def lock(self):
        """잠금"""
        self.state = SecurityState.LOCKED
        print("🔒 잠금되었습니다.")

    def unlock(self):
        """강제 잠금 해제 (관리자 전용)"""
        self.state = SecurityState.UNLOCKED
        self.failed_attempts = 0
        self.lockout_until = None
        print("🔓 잠금이 해제되었습니다.")

    def is_locked(self):
        """잠금 상태 확인"""
        return self.state == SecurityState.LOCKED

    def is_unlocked(self):
        """잠금 해제 상태 확인"""
        return self.state == SecurityState.UNLOCKED

    def get_status(self):
        """
        상태 조회

        Returns:
            상태 딕셔너리
        """
        status = {
            'state': self.state.value,
            'has_password': self.password_hash is not None,
            'failed_attempts': self.failed_attempts,
            'max_attempts': self.max_attempts,
            'is_locked_out': self.lockout_until is not None and self.lockout_until > time.time(),
        }

        if status['is_locked_out']:
            status['lockout_remaining'] = int(self.lockout_until - time.time())

        if self.state == SecurityState.AUTH_MODE:
            status['input_progress'] = len(self.current_input)
            status['password_length'] = self.password_length
            status['timeout_remaining'] = int(self.timeout_seconds - (time.time() - self.input_start_time))

        return status

    def _log_event(self, event_type, gesture_sequence):
        """
        이벤트 로그 기록

        Args:
            event_type: 이벤트 타입 (success, failed, timeout 등)
            gesture_sequence: 입력된 제스처 시퀀스
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'gesture_count': len(gesture_sequence),
            'failed_attempts': self.failed_attempts
        }

        # 보안을 위해 실제 제스처는 저장하지 않음 (선택사항)
        # log_entry['gestures'] = gesture_sequence

        # 로그 파일에 추가
        logs = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []

        logs.append(log_entry)

        # 최근 100개 로그만 유지
        logs = logs[-100:]

        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def get_recent_logs(self, count=10):
        """
        최근 로그 조회

        Args:
            count: 조회할 로그 개수

        Returns:
            로그 리스트
        """
        if not os.path.exists(self.log_file):
            return []

        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
                return logs[-count:]
        except:
            return []

    def print_logs(self, count=10):
        """로그 출력"""
        logs = self.get_recent_logs(count)

        print("\n" + "=" * 60)
        print(f"📜 최근 보안 로그 ({len(logs)}개)")
        print("=" * 60)

        if not logs:
            print("로그가 없습니다.")
        else:
            for log in logs:
                timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                event = log['event']
                event_icon = "✅" if event == "success" else "❌"

                print(f"{event_icon} [{timestamp}] {event.upper()} - {log['gesture_count']}개 제스처")

        print("=" * 60 + "\n")

    def reset_password(self):
        """비밀번호 초기화"""
        if os.path.exists(self.password_file):
            os.remove(self.password_file)

        self.password_hash = None
        self.state = SecurityState.LOCKED
        self.failed_attempts = 0
        self.lockout_until = None

        print("🔄 비밀번호가 초기화되었습니다.")


# 테스트 코드
def main():
    """테스트 함수"""
    print("🔐 제스처 보안 시스템 테스트\n")

    # 보안 시스템 초기화
    security = GestureSecurity(
        password_length=4,
        max_attempts=3,
        timeout_seconds=30
    )

    # 테스트 시나리오
    print("=" * 60)
    print("시나리오 1: 비밀번호 설정")
    print("=" * 60)

    password = ["V_SIGN", "FIST", "THUMBS_UP", "OK_SIGN"]
    security.setup_password(password)

    print("\n" + "=" * 60)
    print("시나리오 2: 성공적인 인증")
    print("=" * 60)

    security.start_authentication()
    for gesture in password:
        result = security.add_gesture(gesture)
        time.sleep(0.5)

    if result == AuthResult.SUCCESS:
        print("잠금이 해제되었습니다!")

    # 다시 잠금
    security.lock()

    print("\n" + "=" * 60)
    print("시나리오 3: 실패한 인증")
    print("=" * 60)

    security.start_authentication()
    wrong_password = ["FIST", "FIST", "FIST", "FIST"]
    for gesture in wrong_password:
        result = security.add_gesture(gesture)
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("시나리오 4: 타임아웃")
    print("=" * 60)

    # 타임아웃 테스트를 위해 짧은 시간 설정
    security_short = GestureSecurity(
        password_length=4,
        max_attempts=3,
        timeout_seconds=3
    )
    security_short.password_hash = security.password_hash

    security_short.start_authentication()
    security_short.add_gesture("V_SIGN")
    print("   3초 대기 중...")
    time.sleep(4)
    result = security_short.add_gesture("FIST")

    # 로그 출력
    security.print_logs()

    # 상태 출력
    print("현재 상태:")
    print(json.dumps(security.get_status(), indent=2))


if __name__ == "__main__":
    main()
