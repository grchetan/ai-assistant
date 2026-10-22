"""
================================================================================
                    JARVIS CORE CONFIGURATION MANAGER
================================================================================
Provides centralized, validated, thread-safe configuration management with
JSON persistence, environment variable overrides, and theme palettes.
================================================================================
"""

import os
import json
import threading
from typing import Any, Dict, Optional, List
from pathlib import Path

# Paths
WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = WORKSPACE_DIR / "jarvis" / "data"
CONFIG_FILE = CONFIG_DIR / "system_config.json"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.enc"
VOICE_PROFILE_FILE = CONFIG_DIR / "voice_profile.npy"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────
#  THEMES DEFINITION (HIGH-TECH HUD PALETTES)
# ─────────────────────────────────────────────────────────────
THEMES: Dict[str, Dict[str, str]] = {
    "ARC_REACTOR": {
        "bg_primary": "#040914",
        "bg_secondary": "#0a1324",
        "bg_card": "#0f1c35",
        "accent": "#00f0ff",
        "accent_dim": "#0088aa",
        "accent_glow": "#00f0ff33",
        "text_primary": "#e6f8ff",
        "text_secondary": "#7fa4cc",
        "text_dim": "#405b7a",
        "success": "#00ff99",
        "warning": "#ffaa00",
        "danger": "#ff3355",
        "border": "#1b335a",
        "canvas_ring": "#00e1ff",
        "canvas_core": "#33f5ff",
    },
    "IRON_MAN": {
        "bg_primary": "#120508",
        "bg_secondary": "#1d0a0f",
        "bg_card": "#2a0f16",
        "accent": "#ffb703",
        "accent_dim": "#b38000",
        "accent_glow": "#ffb70333",
        "text_primary": "#fff5ea",
        "text_secondary": "#d4a373",
        "text_dim": "#73513b",
        "success": "#55d6be",
        "warning": "#fb8500",
        "danger": "#d90429",
        "border": "#4a1c24",
        "canvas_ring": "#e63946",
        "canvas_core": "#ffb703",
    },
    "CYBERPUNK": {
        "bg_primary": "#0d0221",
        "bg_secondary": "#150634",
        "bg_card": "#200950",
        "accent": "#ff007f",
        "accent_dim": "#a30052",
        "accent_glow": "#ff007f33",
        "text_primary": "#fefefe",
        "text_secondary": "#00f0ff",
        "text_dim": "#712282",
        "success": "#00ff66",
        "warning": "#ffee00",
        "danger": "#ff0055",
        "border": "#3f147a",
        "canvas_ring": "#ff007f",
        "canvas_core": "#00f0ff",
    },
    "MATRIX": {
        "bg_primary": "#020d04",
        "bg_secondary": "#051809",
        "bg_card": "#08260e",
        "accent": "#00ff41",
        "accent_dim": "#009926",
        "accent_glow": "#00ff4133",
        "text_primary": "#e0ffe6",
        "text_secondary": "#5cff80",
        "text_dim": "#226633",
        "success": "#00ff66",
        "warning": "#ccff00",
        "danger": "#ff3b30",
        "border": "#0f4418",
        "canvas_ring": "#00ff41",
        "canvas_core": "#80ff9e",
    },
    "MIDNIGHT_STEALTH": {
        "bg_primary": "#08080a",
        "bg_secondary": "#111115",
        "bg_card": "#18181f",
        "accent": "#7952ec",
        "accent_dim": "#4d2db7",
        "accent_glow": "#7952ec33",
        "text_primary": "#f0f0f5",
        "text_secondary": "#a2a2b8",
        "text_dim": "#57576b",
        "success": "#2ec4b6",
        "warning": "#ff9f1c",
        "danger": "#e71d36",
        "border": "#282836",
        "canvas_ring": "#7952ec",
        "canvas_core": "#9d7eff",
    }
}

# ─────────────────────────────────────────────────────────────
#  DEFAULT CONFIGURATION BLUEPRINT
# ─────────────────────────────────────────────────────────────
DEFAULT_CONFIG: Dict[str, Any] = {
    "system": {
        "app_name": "JARVIS Intelligent Quantum Assistant",
        "version": "4.0.0",
        "user_name": "Sir",
        "assistant_name": "JARVIS",
        "active_theme": "ARC_REACTOR",
        "start_minimized": False,
        "run_on_startup": False,
        "log_level": "INFO",
        "data_directory": str(CONFIG_DIR),
        "debug_mode": False
    },
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
        "chunk_size": 1024,
        "energy_threshold": 300,
        "dynamic_energy_threshold": True,
        "pause_threshold": 0.8,
        "phrase_time_limit": 15.0,
        "ambient_noise_duration": 1.0,
        "silence_timeout": 3.0,
        "input_device_index": None,
        "output_device_index": None,
        "audio_feedback_enabled": True
    },
    "stt": {
        "engine": "google",          # google, sphinx, whisper_api
        "primary_language": "en-IN",
        "secondary_language": "hi-IN",
        "multilingual_auto_detect": True,
        "retry_count": 3,
        "offline_fallback": True
    },
    "tts": {
        "engine": "edge_tts",        # edge_tts, pyttsx3
        "edge_voice": "hi-IN-MadhurNeural", # hi-IN-SwaraNeural, en-US-ChristopherNeural, en-IN-MadhurNeural
        "rate": "+0%",
        "pitch": "+0Hz",
        "volume": "+0%",
        "pyttsx3_voice_index": 0,
        "pyttsx3_rate": 185,
        "pyttsx3_volume": 1.0,
        "auto_detect_hinglish": True,
        "speech_queue_limit": 10,
        "enable_sound_fx": True
    },
    "voice_auth": {
        "enabled": False,
        "threshold": 0.72,
        "min_enrollment_samples": 4,
        "feature_extraction": "mfcc_spectral",
        "strict_mode": False,
        "enrolled_name": "Master"
    },
    "llm": {
        "provider": "gemini",        # gemini, openai, local_heuristic
        "model_name": "gemini-2.5-flash",
        "backup_model": "gemini-1.5-flash",
        "temperature": 0.7,
        "max_output_tokens": 1024,
        "top_p": 0.95,
        "top_k": 40,
        "streaming": True,
        "persona": "JARVIS_SUPREME",
        "memory_turns_limit": 25,
        "proactive_idle_chat": True,
        "idle_interval_seconds": 45,
        "system_instruction": (
            "You are J.A.R.V.I.S., an ultra-intelligent, witty, highly loyal, and capable AI assistant. "
            "You speak naturally in fluent Hinglish (Hindi + English blend) or pure English as appropriate. "
            "You address the user with respect as 'Sir'. Keep responses concise, punchy, crisp, yet profoundly helpful. "
            "You possess vast technical knowledge, desktop control prowess, and a subtle gentlemanly charm."
        )
    },
    "automation": {
        "web_search_engine": "google",
        "default_browser": "default",
        "media_player": "system",
        "enable_screen_vision": True,
        "enable_hardware_telemetry": True,
        "telemetry_interval_sec": 2.0,
        "quick_launch_apps": {
            "chrome": ["chrome.exe", "Google Chrome"],
            "code": ["code.cmd", "code.exe", "Visual Studio Code"],
            "terminal": ["wt.exe", "powershell.exe", "cmd.exe"],
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "spotify": ["spotify.exe"],
            "discord": ["discord.exe"],
            "steam": ["steam.exe"],
            "task_manager": ["taskmgr.exe"],
            "file_explorer": ["explorer.exe"]
        }
    },
    "plugins": {
        "weather_enabled": True,
        "crypto_stocks_enabled": True,
        "news_enabled": True,
        "system_diagnostics_enabled": True,
        "dev_tools_enabled": True,
        "trivia_games_enabled": True,
        "scheduler_enabled": True
    }
}


class ConfigManager:
    """Thread-safe, reactive configuration manager with persistence."""
    
    _instance: Optional["ConfigManager"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "ConfigManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._config: Dict[str, Any] = {}
        self._subscribers: List[Any] = []
        self._load()
        self._initialized = True

    def _load(self) -> None:
        """Load configuration from disk, falling back to defaults."""
        with self._lock:
            if CONFIG_FILE.exists():
                try:
                    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                        disk_data = json.load(f)
                    self._config = self._deep_merge(DEFAULT_CONFIG, disk_data)
                except Exception as e:
                    print(f"[ConfigManager] Error reading config: {e}. Using defaults.")
                    self._config = DEFAULT_CONFIG.copy()
            else:
                self._config = DEFAULT_CONFIG.copy()
                self._save()

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries safely without mutating arguments."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _save(self) -> None:
        """Persist current configuration to disk safely."""
        with self._lock:
            try:
                temp_file = CONFIG_FILE.with_suffix(".tmp")
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(self._config, f, indent=4, ensure_ascii=False)
                temp_file.replace(CONFIG_FILE)
            except Exception as e:
                print(f"[ConfigManager] Failed to persist config: {e}")

    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Get a value by section and optional key."""
        with self._lock:
            sec_data = self._config.get(section, {})
            if key is None:
                return sec_data
            if isinstance(sec_data, dict):
                return sec_data.get(key, default)
            return default

    def set(self, section: str, key: str, value: Any, persist: bool = True) -> None:
        """Update a configuration value and optionally persist."""
        with self._lock:
            if section not in self._config or not isinstance(self._config[section], dict):
                self._config[section] = {}
            self._config[section][key] = value
            if persist:
                self._save()
            self._notify(section, key, value)

    def subscribe(self, callback: Any) -> None:
        """Subscribe to configuration changes."""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def _notify(self, section: str, key: str, value: Any) -> None:
        for cb in self._subscribers:
            try:
                cb(section, key, value)
            except Exception as e:
                print(f"[ConfigManager] Error in config subscriber callback: {e}")

    def get_theme(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Retrieve palette dictionary for the specified or active theme."""
        with self._lock:
            name = theme_name or self.get("system", "active_theme", "ARC_REACTOR")
            return THEMES.get(name, THEMES["ARC_REACTOR"]).copy()

    def get_available_themes(self) -> List[str]:
        """List all supported theme names."""
        return list(THEMES.keys())

    def reset_to_defaults(self) -> None:
        """Reset configuration back to factory default blueprint."""
        with self._lock:
            self._config = DEFAULT_CONFIG.copy()
            self._save()


def get_config() -> ConfigManager:
    """Helper singleton accessor for ConfigManager."""
    return ConfigManager()
