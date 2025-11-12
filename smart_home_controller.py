#!/usr/bin/env python3
"""
스마트 홈 제어 모듈

GPIO를 통해 조명, 가전제품 등을 제어하는 모듈입니다.
릴레이 모듈, LED, 서보모터 등을 제어할 수 있습니다.
"""

import time
from enum import Enum

# GPIO 사용 여부 확인 (라즈베리파이가 아닌 환경에서는 시뮬레이션 모드)
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO를 사용할 수 없습니다. 시뮬레이션 모드로 실행됩니다.")


class DeviceType(Enum):
    """디바이스 타입"""
    LIGHT = "light"
    FAN = "fan"
    AC = "ac"
    RELAY = "relay"
    LED = "led"
    SERVO = "servo"


class Device:
    """스마트 홈 디바이스 클래스"""

    def __init__(self, name, device_type, pin, initial_state=False):
        """
        초기화

        Args:
            name: 디바이스 이름
            device_type: 디바이스 타입 (DeviceType)
            pin: GPIO 핀 번호
            initial_state: 초기 상태 (True=ON, False=OFF)
        """
        self.name = name
        self.device_type = device_type
        self.pin = pin
        self.state = initial_state
        self.brightness = 100  # 밝기 (0-100%)

    def __str__(self):
        return f"{self.name} ({self.device_type.value}): {'ON' if self.state else 'OFF'} - {self.brightness}%"


class SmartHomeController:
    """스마트 홈 컨트롤러"""

    def __init__(self, simulation_mode=None):
        """
        초기화

        Args:
            simulation_mode: 시뮬레이션 모드 강제 설정 (None=자동감지)
        """
        if simulation_mode is not None:
            self.simulation_mode = simulation_mode
        else:
            self.simulation_mode = not GPIO_AVAILABLE

        self.devices = {}

        if not self.simulation_mode:
            # 실제 GPIO 초기화
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            print("✅ GPIO 초기화 완료 (실제 모드)")
        else:
            print("🔧 시뮬레이션 모드로 실행")

    def add_device(self, name, device_type, pin, initial_state=False):
        """
        디바이스 추가

        Args:
            name: 디바이스 이름
            device_type: 디바이스 타입 (DeviceType)
            pin: GPIO 핀 번호
            initial_state: 초기 상태
        """
        device = Device(name, device_type, pin, initial_state)
        self.devices[name] = device

        if not self.simulation_mode:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH if initial_state else GPIO.LOW)

        print(f"➕ 디바이스 추가: {device}")

    def turn_on(self, device_name):
        """
        디바이스 켜기

        Args:
            device_name: 디바이스 이름

        Returns:
            성공 여부
        """
        if device_name not in self.devices:
            print(f"❌ 디바이스를 찾을 수 없습니다: {device_name}")
            return False

        device = self.devices[device_name]
        device.state = True

        if not self.simulation_mode:
            GPIO.output(device.pin, GPIO.HIGH)

        print(f"💡 ON: {device.name} ({device.device_type.value})")
        return True

    def turn_off(self, device_name):
        """
        디바이스 끄기

        Args:
            device_name: 디바이스 이름

        Returns:
            성공 여부
        """
        if device_name not in self.devices:
            print(f"❌ 디바이스를 찾을 수 없습니다: {device_name}")
            return False

        device = self.devices[device_name]
        device.state = False

        if not self.simulation_mode:
            GPIO.output(device.pin, GPIO.LOW)

        print(f"🌑 OFF: {device.name} ({device.device_type.value})")
        return True

    def toggle(self, device_name):
        """
        디바이스 토글

        Args:
            device_name: 디바이스 이름

        Returns:
            성공 여부
        """
        if device_name not in self.devices:
            print(f"❌ 디바이스를 찾을 수 없습니다: {device_name}")
            return False

        device = self.devices[device_name]

        if device.state:
            return self.turn_off(device_name)
        else:
            return self.turn_on(device_name)

    def set_brightness(self, device_name, brightness):
        """
        밝기 설정 (PWM 필요)

        Args:
            device_name: 디바이스 이름
            brightness: 밝기 (0-100)

        Returns:
            성공 여부
        """
        if device_name not in self.devices:
            print(f"❌ 디바이스를 찾을 수 없습니다: {device_name}")
            return False

        device = self.devices[device_name]
        device.brightness = max(0, min(100, brightness))

        # PWM 구현 필요 (여기서는 임계값으로 ON/OFF)
        if device.brightness > 0:
            device.state = True
            if not self.simulation_mode:
                GPIO.output(device.pin, GPIO.HIGH)
        else:
            device.state = False
            if not self.simulation_mode:
                GPIO.output(device.pin, GPIO.LOW)

        print(f"🔆 밝기 설정: {device.name} → {device.brightness}%")
        return True

    def turn_on_all(self):
        """모든 디바이스 켜기"""
        print("🌟 모든 디바이스 켜기")
        for device_name in self.devices:
            self.turn_on(device_name)

    def turn_off_all(self):
        """모든 디바이스 끄기"""
        print("🌙 모든 디바이스 끄기")
        for device_name in self.devices:
            self.turn_off(device_name)

    def get_status(self, device_name=None):
        """
        디바이스 상태 조회

        Args:
            device_name: 디바이스 이름 (None이면 전체)

        Returns:
            상태 딕셔너리 또는 디바이스 정보
        """
        if device_name:
            if device_name in self.devices:
                device = self.devices[device_name]
                return {
                    'name': device.name,
                    'type': device.device_type.value,
                    'state': device.state,
                    'brightness': device.brightness
                }
            return None
        else:
            return {name: {
                'type': device.device_type.value,
                'state': device.state,
                'brightness': device.brightness
            } for name, device in self.devices.items()}

    def print_status(self):
        """전체 상태 출력"""
        print("\n" + "=" * 50)
        print("📊 스마트 홈 디바이스 상태")
        print("=" * 50)

        if not self.devices:
            print("등록된 디바이스가 없습니다.")
        else:
            for name, device in self.devices.items():
                status = "🟢 ON " if device.state else "🔴 OFF"
                print(f"{status} | {device.name:15} | {device.device_type.value:8} | Pin:{device.pin:2} | {device.brightness}%")

        print("=" * 50 + "\n")

    def cleanup(self):
        """GPIO 정리"""
        if not self.simulation_mode:
            GPIO.cleanup()
            print("🧹 GPIO 정리 완료")


# 테스트 코드
def main():
    """테스트 함수"""
    print("🏠 스마트 홈 컨트롤러 테스트\n")

    # 컨트롤러 초기화 (시뮬레이션 모드)
    controller = SmartHomeController(simulation_mode=True)

    # 디바이스 추가
    controller.add_device("거실 조명", DeviceType.LIGHT, pin=17)
    controller.add_device("침실 조명", DeviceType.LIGHT, pin=27)
    controller.add_device("선풍기", DeviceType.FAN, pin=22)
    controller.add_device("에어컨", DeviceType.AC, pin=23)

    # 초기 상태
    controller.print_status()

    # 테스트 시나리오
    print("📝 테스트 시나리오 시작\n")

    print("1. 거실 조명 켜기")
    controller.turn_on("거실 조명")
    time.sleep(1)

    print("\n2. 선풍기 켜기")
    controller.turn_on("선풍기")
    time.sleep(1)

    print("\n3. 거실 조명 밝기 50%")
    controller.set_brightness("거실 조명", 50)
    time.sleep(1)

    print("\n4. 모든 디바이스 켜기")
    controller.turn_on_all()
    time.sleep(1)

    controller.print_status()

    print("5. 침실 조명 토글")
    controller.toggle("침실 조명")
    time.sleep(1)
    controller.toggle("침실 조명")
    time.sleep(1)

    print("\n6. 모든 디바이스 끄기")
    controller.turn_off_all()

    # 최종 상태
    controller.print_status()

    # 정리
    controller.cleanup()


if __name__ == "__main__":
    main()
