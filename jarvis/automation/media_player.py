"""
================================================================================
                    JARVIS MULTIMEDIA & AUDIO PLAYER
================================================================================
Controls system media playback using Windows multimedia virtual key events
(Play/Pause, Track Skip, Track Previous) and audio streams via yt-dlp / pygame.
================================================================================
"""

import ctypes
import threading
import subprocess
from typing import Optional, Tuple

from jarvis.core.logger import get_logger

# Windows Virtual-Key codes for Media
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP       = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3


class MediaPlayerController:
    """Controls OS multimedia and streams background music."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def _send_vk(self, code: int) -> None:
        ctypes.windll.user32.keybd_event(code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(code, 0, 2, 0)

    def play_pause(self) -> str:
        """Toggle system media Play/Pause (Spotify, YouTube, VLC, Browser)."""
        self._send_vk(VK_MEDIA_PLAY_PAUSE)
        self.logger.info("Sent Media Play/Pause toggle.", "MEDIA")
        return "Media play pause toggle kar diya sir."

    def next_track(self) -> str:
        """Skip to next media track."""
        self._send_vk(VK_MEDIA_NEXT_TRACK)
        self.logger.info("Sent Media Next Track.", "MEDIA")
        return "Agla gaana play kar raha hoon sir."

    def previous_track(self) -> str:
        """Skip to previous media track."""
        self._send_vk(VK_MEDIA_PREV_TRACK)
        self.logger.info("Sent Media Previous Track.", "MEDIA")
        return "Pichhla gaana play kar raha hoon sir."

    def stop_media(self) -> str:
        """Stop current media playback."""
        self._send_vk(VK_MEDIA_STOP)
        self.logger.info("Sent Media Stop.", "MEDIA")
        return "Music band kar diya sir."


def get_media_player() -> MediaPlayerController:
    return MediaPlayerController()
