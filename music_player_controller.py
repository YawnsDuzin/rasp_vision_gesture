#!/usr/bin/env python3
"""
음악 플레이어 제어 모듈

pygame.mixer를 사용한 음악 재생 제어 모듈입니다.
VLC, MPD 등 다른 플레이어로 확장 가능합니다.
"""

import os
import glob
from pathlib import Path
from enum import Enum

# pygame 사용 여부 확인
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️  pygame을 사용할 수 없습니다. 시뮬레이션 모드로 실행됩니다.")


class PlayerState(Enum):
    """플레이어 상태"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class MusicPlayerController:
    """음악 플레이어 컨트롤러"""

    def __init__(self, music_directory=None, simulation_mode=None):
        """
        초기화

        Args:
            music_directory: 음악 파일 디렉토리
            simulation_mode: 시뮬레이션 모드 강제 설정
        """
        if simulation_mode is not None:
            self.simulation_mode = simulation_mode
        else:
            self.simulation_mode = not PYGAME_AVAILABLE

        self.music_directory = music_directory or os.path.expanduser("~/Music")
        self.playlist = []
        self.current_index = 0
        self.state = PlayerState.STOPPED
        self.volume = 70  # 0-100
        self.current_song = None

        if not self.simulation_mode:
            print("✅ pygame 음악 플레이어 초기화 완료")
        else:
            print("🔧 시뮬레이션 모드로 실행")

        # 재생 목록 로드
        self.load_playlist()

    def load_playlist(self, directory=None):
        """
        재생 목록 로드

        Args:
            directory: 음악 디렉토리 (None이면 기본 디렉토리)
        """
        if directory:
            self.music_directory = directory

        # 지원하는 음악 파일 확장자
        extensions = ['*.mp3', '*.wav', '*.ogg', '*.flac', '*.m4a']

        self.playlist = []

        if os.path.exists(self.music_directory):
            for ext in extensions:
                pattern = os.path.join(self.music_directory, '**', ext)
                files = glob.glob(pattern, recursive=True)
                self.playlist.extend(files)

            self.playlist.sort()
            print(f"📂 재생 목록 로드: {len(self.playlist)}개 파일")

            if self.playlist:
                for idx, song in enumerate(self.playlist[:5]):
                    print(f"   {idx + 1}. {Path(song).name}")
                if len(self.playlist) > 5:
                    print(f"   ... 외 {len(self.playlist) - 5}개")
        else:
            print(f"⚠️  음악 디렉토리를 찾을 수 없습니다: {self.music_directory}")
            # 테스트용 더미 재생 목록
            self.playlist = [
                "Song 1.mp3",
                "Song 2.mp3",
                "Song 3.mp3",
                "Song 4.mp3",
                "Song 5.mp3"
            ]
            print(f"📂 테스트 재생 목록: {len(self.playlist)}개")

    def play(self, index=None):
        """
        음악 재생

        Args:
            index: 재생할 곡 인덱스 (None이면 현재 곡)

        Returns:
            성공 여부
        """
        if not self.playlist:
            print("❌ 재생 목록이 비어있습니다.")
            return False

        if index is not None:
            self.current_index = max(0, min(index, len(self.playlist) - 1))

        self.current_song = self.playlist[self.current_index]

        if not self.simulation_mode:
            try:
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()
                self.state = PlayerState.PLAYING
                print(f"▶️  재생: {Path(self.current_song).name}")
                return True
            except Exception as e:
                print(f"❌ 재생 실패: {e}")
                self.state = PlayerState.STOPPED
                return False
        else:
            self.state = PlayerState.PLAYING
            print(f"▶️  재생 (시뮬레이션): {Path(self.current_song).name}")
            return True

    def pause(self):
        """일시정지"""
        if self.state == PlayerState.PLAYING:
            if not self.simulation_mode:
                pygame.mixer.music.pause()
            self.state = PlayerState.PAUSED
            print("⏸️  일시정지")
            return True
        return False

    def resume(self):
        """재생 재개"""
        if self.state == PlayerState.PAUSED:
            if not self.simulation_mode:
                pygame.mixer.music.unpause()
            self.state = PlayerState.PLAYING
            print("▶️  재생 재개")
            return True
        return False

    def stop(self):
        """정지"""
        if not self.simulation_mode:
            pygame.mixer.music.stop()
        self.state = PlayerState.STOPPED
        print("⏹️  정지")
        return True

    def toggle_play_pause(self):
        """재생/일시정지 토글"""
        if self.state == PlayerState.PLAYING:
            return self.pause()
        elif self.state == PlayerState.PAUSED:
            return self.resume()
        elif self.state == PlayerState.STOPPED:
            return self.play()
        return False

    def next_track(self):
        """다음 곡"""
        if not self.playlist:
            print("❌ 재생 목록이 비어있습니다.")
            return False

        self.current_index = (self.current_index + 1) % len(self.playlist)
        print(f"⏭️  다음 곡 ({self.current_index + 1}/{len(self.playlist)})")
        return self.play()

    def previous_track(self):
        """이전 곡"""
        if not self.playlist:
            print("❌ 재생 목록이 비어있습니다.")
            return False

        self.current_index = (self.current_index - 1) % len(self.playlist)
        print(f"⏮️  이전 곡 ({self.current_index + 1}/{len(self.playlist)})")
        return self.play()

    def set_volume(self, volume):
        """
        볼륨 설정

        Args:
            volume: 볼륨 (0-100)

        Returns:
            성공 여부
        """
        self.volume = max(0, min(100, volume))

        if not self.simulation_mode:
            pygame.mixer.music.set_volume(self.volume / 100.0)

        print(f"🔊 볼륨: {self.volume}%")
        return True

    def volume_up(self, step=10):
        """
        볼륨 증가

        Args:
            step: 증가량

        Returns:
            성공 여부
        """
        return self.set_volume(self.volume + step)

    def volume_down(self, step=10):
        """
        볼륨 감소

        Args:
            step: 감소량

        Returns:
            성공 여부
        """
        return self.set_volume(self.volume - step)

    def get_status(self):
        """
        플레이어 상태 조회

        Returns:
            상태 딕셔너리
        """
        return {
            'state': self.state.value,
            'current_song': Path(self.current_song).name if self.current_song else None,
            'current_index': self.current_index,
            'playlist_length': len(self.playlist),
            'volume': self.volume
        }

    def print_status(self):
        """상태 출력"""
        print("\n" + "=" * 50)
        print("🎵 음악 플레이어 상태")
        print("=" * 50)
        print(f"상태: {self.state.value.upper()}")
        print(f"현재 곡: {Path(self.current_song).name if self.current_song else 'None'}")
        print(f"재생 목록: {self.current_index + 1}/{len(self.playlist)}")
        print(f"볼륨: {self.volume}%")
        print("=" * 50 + "\n")

    def cleanup(self):
        """정리"""
        if not self.simulation_mode:
            pygame.mixer.quit()
        print("🧹 음악 플레이어 정리 완료")


# 테스트 코드
def main():
    """테스트 함수"""
    import time

    print("🎵 음악 플레이어 컨트롤러 테스트\n")

    # 플레이어 초기화 (시뮬레이션 모드)
    player = MusicPlayerController(simulation_mode=True)

    # 초기 상태
    player.print_status()

    # 테스트 시나리오
    print("📝 테스트 시나리오 시작\n")

    print("1. 음악 재생")
    player.play()
    time.sleep(1)

    player.print_status()

    print("2. 일시정지")
    player.pause()
    time.sleep(1)

    print("\n3. 재생 재개")
    player.resume()
    time.sleep(1)

    print("\n4. 볼륨 50%")
    player.set_volume(50)
    time.sleep(1)

    print("\n5. 볼륨 업")
    player.volume_up(20)
    time.sleep(1)

    print("\n6. 다음 곡")
    player.next_track()
    time.sleep(1)

    print("\n7. 다음 곡")
    player.next_track()
    time.sleep(1)

    print("\n8. 이전 곡")
    player.previous_track()
    time.sleep(1)

    player.print_status()

    print("9. 정지")
    player.stop()

    # 최종 상태
    player.print_status()

    # 정리
    player.cleanup()


if __name__ == "__main__":
    main()
