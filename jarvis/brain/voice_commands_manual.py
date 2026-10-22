"""
================================================================================
                    JARVIS COMMAND DIRECTORY & INTERACTIVE HELP
================================================================================
Comprehensive catalog of all supported voice and text commands organized by
operational category with examples and spoken guidance.
================================================================================
"""

from typing import List, Dict, Any

COMMAND_CATALOG: Dict[str, List[Dict[str, str]]] = {
    "System & Power": [
        {"cmd": "shutdown pc / system band karo", "desc": "Schedules PC shutdown with 30s countdown"},
        {"cmd": "cancel shutdown", "desc": "Aborts a pending scheduled shutdown"},
        {"cmd": "restart pc", "desc": "Reboots the computer"},
        {"cmd": "lock screen / pc lock karo", "desc": "Instantly locks the Windows workstation"},
        {"cmd": "battery status", "desc": "Announces current battery percentage and charging state"},
        {"cmd": "hardware status / performance", "desc": "Reports CPU and RAM utilization metrics"}
    ],
    "Window Management": [
        {"cmd": "minimize all / show desktop", "desc": "Minimizes all open windows to desktop"},
        {"cmd": "maximize window", "desc": "Maximizes active window"},
        {"cmd": "close window", "desc": "Closes current foreground application"},
        {"cmd": "snap left / snap right", "desc": "Snaps active window to split-screen half"}
    ],
    "Applications & Web": [
        {"cmd": "open chrome / vs code / terminal", "desc": "Launches designated desktop app"},
        {"cmd": "google search <query>", "desc": "Opens search query in Google"},
        {"cmd": "youtube search <song/video>", "desc": "Finds and plays query on YouTube"},
        {"cmd": "github search <repo>", "desc": "Searches repositories on GitHub"}
    ],
    "Media & Audio": [
        {"cmd": "volume up / volume down", "desc": "Increases or decreases master volume"},
        {"cmd": "volume 60 percent", "desc": "Sets volume to exact percentage level"},
        {"cmd": "mute / unmute karo", "desc": "Toggles master audio mute"},
        {"cmd": "play music / pause music", "desc": "Toggles media playback"}
    ],
    "Productivity & Notes": [
        {"cmd": "take note <text>", "desc": "Records voice-dictated note"},
        {"cmd": "read my notes", "desc": "Reads recent notes out loud"},
        {"cmd": "add todo <task>", "desc": "Adds task to To-Do checklist"},
        {"cmd": "show todo", "desc": "Lists pending tasks"},
        {"cmd": "set timer for <N> minutes", "desc": "Starts background countdown alarm"}
    ],
    "Developer & Network": [
        {"cmd": "git status", "desc": "Inspects local repository status"},
        {"cmd": "ping test", "desc": "Measures ICMP network latency"},
        {"cmd": "speed test / ip address", "desc": "Reports Wi-Fi SSID, local and public IP"},
        {"cmd": "organize desktop", "desc": "Sorts messy desktop files into neat folders"}
    ],
    "Plugins & Trivia": [
        {"cmd": "weather in <city>", "desc": "Reports live temperature and conditions"},
        {"cmd": "crypto price / bitcoin price", "desc": "Announces real-time BTC and ETH prices"},
        {"cmd": "latest news", "desc": "Reads top breaking headlines"},
        {"cmd": "tell me a joke", "desc": "Tells witty programmer and general jokes"},
        {"cmd": "flip a coin / roll dice", "desc": "Interactive coin toss and dice simulator"}
    ],
    "Voice Security": [
        {"cmd": "enroll my voice", "desc": "Launches multi-sample biometric voice recording"},
        {"cmd": "toggle voice lock", "desc": "Enables/disables speaker biometric verification"},
        {"cmd": "voice security status", "desc": "Checks if voice lock is currently active"}
    ]
}


class VoiceCommandsManual:
    """Provides user assistance on available commands."""

    @classmethod
    def get_category_summary(cls) -> str:
        cats = list(COMMAND_CATALOG.keys())
        return f"Sir, mere paas {len(cats)} main command categories hain: " + ", ".join(cats) + ". Kisi category ki detail janne ke liye pooch sakte hain!"

    @classmethod
    def get_commands_for_category(cls, category: str) -> List[Dict[str, str]]:
        c_low = category.lower()
        for cat_name, commands in COMMAND_CATALOG.items():
            if c_low in cat_name.lower():
                return commands
        return []
