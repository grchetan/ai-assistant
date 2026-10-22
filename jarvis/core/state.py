"""
================================================================================
                    JARVIS CENTRAL STATE MACHINE
================================================================================
Thread-safe reactive runtime state store with state transition guards,
system performance metrics tracking, listeners, and serializable snapshots.
================================================================================
"""

import time
import threading
from enum import Enum
from typing import Dict, Any, List, Callable, Optional


class AssistantMode(Enum):
    STANDBY         = "STANDBY"
    INITIALIZING    = "INITIALIZING"
    IDLE            = "IDLE"
    LISTENING       = "LISTENING"
    PROCESSING      = "PROCESSING"
    SPEAKING        = "SPEAKING"
    ENROLLING_VOICE = "ENROLLING_VOICE"
    PAUSED          = "PAUSED"
    MUTED           = "MUTED"
    TERMINATING     = "TERMINATING"


class StateManager:
    """Singleton thread-safe system state keeper."""
    
    _instance: Optional["StateManager"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "StateManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._start_time = time.time()
        self._mode = AssistantMode.STANDBY
        self._last_user_speech_time = time.time()
        self._last_assistant_speech_time = time.time()
        
        # Audio metrics
        self._current_rms: float = 0.0
        self._is_vad_active: bool = False
        self._audio_input_muted: bool = False
        self._audio_output_muted: bool = False

        # Voice security state
        self._voice_auth_active: bool = False
        self._current_speaker_verified: bool = False
        self._last_confidence_score: float = 0.0
        self._authorized_user_name: str = "Master"

        # Hardware metrics cache
        self._cpu_percent: float = 0.0
        self._ram_percent: float = 0.0
        self._battery_percent: Optional[float] = None
        self._battery_plugged: bool = True
        self._network_status: str = "Online"
        self._active_window_title: str = "Desktop"

        # Conversation & Task metrics
        self._total_commands_executed: int = 0
        self._consecutive_unclear_count: int = 0
        self._consecutive_silence_count: int = 0
        self._active_command_text: str = ""
        self._active_llm_response: str = ""

        # Observers
        self._mode_listeners: List[Callable[[AssistantMode, AssistantMode], None]] = []
        self._metric_listeners: List[Callable[[Dict[str, Any]], None]] = []

        self._initialized = True

    # ─────────────────────────────────────────────────────────
    #  MODE MANAGEMENT & TRANSITIONS
    # ─────────────────────────────────────────────────────────
    @property
    def mode(self) -> AssistantMode:
        with self._lock:
            return self._mode

    def set_mode(self, new_mode: AssistantMode) -> None:
        """Safely transition to a new assistant state mode with notification."""
        old_mode = None
        with self._lock:
            if self._mode == new_mode:
                return
            old_mode = self._mode
            self._mode = new_mode

        # Notify observers outside of lock
        for listener in self._mode_listeners:
            try:
                listener(old_mode, new_mode)
            except Exception as e:
                print(f"[StateManager] Error in mode listener: {e}")

    def add_mode_listener(self, listener: Callable[[AssistantMode, AssistantMode], None]) -> None:
        with self._lock:
            if listener not in self._mode_listeners:
                self._mode_listeners.append(listener)

    # ─────────────────────────────────────────────────────────
    #  SPEECH & AUDIO TELEMETRY
    # ─────────────────────────────────────────────────────────
    def update_rms(self, rms: float, is_vad: bool = False) -> None:
        with self._lock:
            self._current_rms = rms
            self._is_vad_active = is_vad

    def mark_user_spoke(self) -> None:
        with self._lock:
            self._last_user_speech_time = time.time()
            self._consecutive_silence_count = 0
            self._consecutive_unclear_count = 0

    def mark_assistant_spoke(self) -> None:
        with self._lock:
            self._last_assistant_speech_time = time.time()

    def record_silence(self) -> int:
        with self._lock:
            self._consecutive_silence_count += 1
            return self._consecutive_silence_count

    def record_unclear(self) -> int:
        with self._lock:
            self._consecutive_unclear_count += 1
            return self._consecutive_unclear_count

    def reset_speech_counters(self) -> None:
        with self._lock:
            self._consecutive_silence_count = 0
            self._consecutive_unclear_count = 0

    @property
    def idle_time(self) -> float:
        """Seconds since either the user or assistant spoke."""
        with self._lock:
            latest = max(self._last_user_speech_time, self._last_assistant_speech_time)
            return time.time() - latest

    # ─────────────────────────────────────────────────────────
    #  HARDWARE & SYSTEM TELEMETRY
    # ─────────────────────────────────────────────────────────
    def update_hardware_metrics(
        self,
        cpu: float,
        ram: float,
        battery: Optional[float] = None,
        plugged: bool = True,
        net_status: str = "Online",
        active_window: str = "Desktop"
    ) -> None:
        with self._lock:
            self._cpu_percent = cpu
            self._ram_percent = ram
            self._battery_percent = battery
            self._battery_plugged = plugged
            self._network_status = net_status
            self._active_window_title = active_window

        snapshot = self.get_telemetry_snapshot()
        for listener in self._metric_listeners:
            try:
                listener(snapshot)
            except Exception as e:
                print(f"[StateManager] Telemetry listener error: {e}")

    def add_telemetry_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        with self._lock:
            if listener not in self._metric_listeners:
                self._metric_listeners.append(listener)

    # ─────────────────────────────────────────────────────────
    #  SECURITY & AUTH STATE
    # ─────────────────────────────────────────────────────────
    def set_voice_auth_status(self, enabled: bool, verified: bool = False, score: float = 0.0) -> None:
        with self._lock:
            self._voice_auth_active = enabled
            self._current_speaker_verified = verified
            self._last_confidence_score = score

    # ─────────────────────────────────────────────────────────
    #  SYSTEM SNAPSHOT
    # ─────────────────────────────────────────────────────────
    def get_telemetry_snapshot(self) -> Dict[str, Any]:
        """Produce a complete, thread-safe, serializable state snapshot."""
        with self._lock:
            now = time.time()
            return {
                "timestamp": now,
                "uptime_seconds": round(now - self._start_time, 1),
                "mode": self._mode.value,
                "idle_seconds": round(self.idle_time, 1),
                "rms_energy": round(self._current_rms, 2),
                "vad_active": self._is_vad_active,
                "cpu_percent": self._cpu_percent,
                "ram_percent": self._ram_percent,
                "battery_percent": self._battery_percent,
                "battery_plugged": self._battery_plugged,
                "network_status": self._network_status,
                "active_window": self._active_window_title,
                "commands_executed": self._total_commands_executed,
                "voice_auth_enabled": self._voice_auth_active,
                "voice_auth_verified": self._current_speaker_verified,
                "voice_auth_score": round(self._last_confidence_score, 3),
                "silence_count": self._consecutive_silence_count,
                "unclear_count": self._consecutive_unclear_count
            }

    def increment_command_count(self) -> int:
        with self._lock:
            self._total_commands_executed += 1
            return self._total_commands_executed


def get_state_manager() -> StateManager:
    """Helper singleton accessor for StateManager."""
    return StateManager()
