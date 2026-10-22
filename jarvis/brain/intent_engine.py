"""
================================================================================
                    JARVIS ADVANCED INTENT CLASSIFICATION ENGINE
================================================================================
Natural language understanding engine parsing 150+ spoken command patterns in
Hinglish, Hindi, and English with regex routing, token normalization, entity
extraction, and prioritized execution dispatch.
================================================================================
"""

import re
import os
import time
from enum import Enum
from typing import Dict, Any, Optional, Tuple, Callable, List

from jarvis.core.logger import get_logger
from jarvis.core.state import get_state_manager


class IntentType(Enum):
    # System & Hardware
    SYSTEM_SHUTDOWN       = "system.shutdown"
    SYSTEM_RESTART        = "system.restart"
    SYSTEM_SLEEP          = "system.sleep"
    SYSTEM_LOCK           = "system.lock"
    SYSTEM_CANCEL_SHUTDOWN= "system.cancel_shutdown"
    SYSTEM_BATTERY        = "system.battery"
    SYSTEM_METRICS        = "system.metrics"
    SYSTEM_TAKE_SCREENSHOT= "system.screenshot"
    SYSTEM_EMPTY_RECYCLE  = "system.empty_recycle"

    # Volume & Brightness
    VOLUME_SET            = "volume.set"
    VOLUME_UP             = "volume.up"
    VOLUME_DOWN           = "volume.down"
    VOLUME_MUTE           = "volume.mute"
    VOLUME_UNMUTE         = "volume.unmute"
    BRIGHTNESS_SET        = "brightness.set"

    # Window Management
    WINDOW_MINIMIZE_ALL   = "window.minimize_all"
    WINDOW_MAXIMIZE       = "window.maximize"
    WINDOW_CLOSE_ACTIVE   = "window.close_active"
    WINDOW_SNAP_LEFT      = "window.snap_left"
    WINDOW_SNAP_RIGHT     = "window.snap_right"
    WINDOW_SWITCH         = "window.switch"

    # Application Launching & Closing
    APP_LAUNCH            = "app.launch"
    APP_TERMINATE         = "app.terminate"

    # Web & Media
    WEB_SEARCH_GOOGLE     = "web.google_search"
    WEB_SEARCH_YOUTUBE    = "web.youtube_search"
    WEB_OPEN_URL          = "web.open_url"
    WEB_SEARCH_GITHUB     = "web.github_search"
    WEB_STACKOVERFLOW     = "web.stackoverflow_search"
    MEDIA_PLAY_PAUSE      = "media.play_pause"
    MEDIA_NEXT            = "media.next"
    MEDIA_PREVIOUS        = "media.prev"

    # Productivity & Notes
    NOTE_TAKE             = "notes.take"
    NOTE_READ             = "notes.read"
    TODO_ADD              = "todo.add"
    TODO_LIST             = "todo.list"
    TIMER_SET             = "timer.set"
    ALARM_SET             = "alarm.set"

    # Dev & Network Tools
    DEV_GIT_STATUS        = "dev.git_status"
    DEV_NETWORK_PING      = "dev.network_ping"
    DEV_NETWORK_SPEED     = "dev.network_speed"
    DEV_ORGANIZE_DESKTOP  = "dev.organize_desktop"
    DEV_UNDO_DESKTOP      = "dev.undo_desktop"
    DEV_ORGANIZE_DOWNLOADS= "dev.organize_downloads"

    # Plugins: Weather, Stocks, Trivia
    PLUGIN_WEATHER        = "plugin.weather"
    PLUGIN_CRYPTO         = "plugin.crypto"
    PLUGIN_NEWS           = "plugin.news"
    PLUGIN_CALCULATOR     = "plugin.calc"
    PLUGIN_JOKE           = "plugin.joke"
    PLUGIN_COIN_FLIP      = "plugin.coin_flip"
    PLUGIN_DICE_ROLL      = "plugin.dice_roll"

    # Time & General
    GENERAL_TIME          = "general.time"
    GENERAL_DATE          = "general.date"
    GENERAL_GREETING      = "general.greeting"
    GENERAL_EXIT          = "general.exit"

    # Voice Biometrics
    AUTH_ENROLL           = "auth.enroll"
    AUTH_TOGGLE           = "auth.toggle"
    AUTH_STATUS           = "auth.status"

    # Face Biometrics
    FACE_ENROLL           = "face.enroll"
    FACE_VERIFY           = "face.verify"

    # Interactive & Gamification
    INTERACTIVE_RPG       = "game.rpg"
    POMODORO_START        = "pomo.start"
    POMODORO_STOP         = "pomo.stop"
    HABIT_LOG_WATER       = "habit.water"
    HABIT_LOG_CODE        = "habit.code"
    HABIT_SUMMARY         = "habit.summary"
    EXECUTIVE_BRIEFING    = "system.briefing"

    # Display & Desktop Tweaks
    NIGHT_LIGHT_ON        = "display.night_on"
    NIGHT_LIGHT_OFF       = "display.night_off"
    DESKTOP_VIRTUAL_NEW   = "desktop.vnew"
    DESKTOP_VIRTUAL_NEXT  = "desktop.vnext"
    DESKTOP_VIRTUAL_PREV  = "desktop.vprev"

    # Security & DevOps
    DOCKER_SUMMARY        = "devops.docker"
    SECURITY_IDS_AUDIT    = "security.ids"
    SECURITY_WIFI_AUDIT   = "security.wifi"

    # Ambient Soundscapes
    AMBIENT_RAIN          = "ambient.rain"
    AMBIENT_BINAURAL      = "ambient.binaural"
    AMBIENT_STOP          = "ambient.stop"

    # Fallback to LLM
    LLM_QUERY             = "llm.query"


class IntentParser:
    """Parses raw spoken text into structured intents and payload parameters."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.state = get_state_manager()
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex pattern matching rules for rapid intent detection."""
        self.patterns: List[Tuple[re.Pattern, IntentType, Dict[str, Any]]] = [
            # ──────────────── Exit & Shutdown ────────────────
            (re.compile(r"\b(exit|quit|band ho ja|bye|shutdown jarvis|close jarvis|alvida)\b", re.I),
             IntentType.GENERAL_EXIT, {}),
            (re.compile(r"\b(cancel shutdown|shutdown cancel karo|rok do shutdown)\b", re.I),
             IntentType.SYSTEM_CANCEL_SHUTDOWN, {}),
            (re.compile(r"\b(shutdown pc|turn off computer|pc band kar do|system band karo)\b", re.I),
             IntentType.SYSTEM_SHUTDOWN, {}),
            (re.compile(r"\b(restart pc|computer restart karo|system restart)\b", re.I),
             IntentType.SYSTEM_RESTART, {}),
            (re.compile(r"\b(sleep mode|pc ko sula do|computer sleep)\b", re.I),
             IntentType.SYSTEM_SLEEP, {}),
            (re.compile(r"\b(lock computer|pc lock karo|screen lock|lock screen)\b", re.I),
             IntentType.SYSTEM_LOCK, {}),

            # ──────────────── Screenshot & Clean ────────────────
            (re.compile(r"\b(screenshot|capture screen|screen photo)\b", re.I),
             IntentType.SYSTEM_TAKE_SCREENSHOT, {}),
            (re.compile(r"\b(empty recycle bin|kachra saaf karo|recycle bin khali karo)\b", re.I),
             IntentType.SYSTEM_EMPTY_RECYCLE, {}),

            # ──────────────── Hardware Diagnostics ────────────────
            (re.compile(r"\b(battery|charge kitna hai|battery percentage|kitni charging hai)\b", re.I),
             IntentType.SYSTEM_BATTERY, {}),
            (re.compile(r"\b(cpu usage|ram usage|hardware status|system health|performance batao)\b", re.I),
             IntentType.SYSTEM_METRICS, {}),

            # ──────────────── Volume Controls ────────────────
            (re.compile(r"\b(mute karo|sound band|chup ho ja|awaz band)\b", re.I),
             IntentType.VOLUME_MUTE, {}),
            (re.compile(r"\b(unmute karo|sound chalu karo|awaz kholo)\b", re.I),
             IntentType.VOLUME_UNMUTE, {}),
            (re.compile(r"\b(volume badhao|volume up|awaz tezz karo|louder)\b", re.I),
             IntentType.VOLUME_UP, {}),
            (re.compile(r"\b(volume kam karo|volume down|awaz dheemi karo|quieter)\b", re.I),
             IntentType.VOLUME_DOWN, {}),
            (re.compile(r"\b(?:volume|awaz)\s+(?:to\s+)?(\d{1,3})\s*(?:percent|%)?\b", re.I),
             IntentType.VOLUME_SET, {"extract_num": 1}),

            # ──────────────── Window Management ────────────────
            (re.compile(r"\b(minimize all|sab minimize kar do|desktop dikhao|show desktop)\b", re.I),
             IntentType.WINDOW_MINIMIZE_ALL, {}),
            (re.compile(r"\b(maximize window|fullscreen|badi screen karo)\b", re.I),
             IntentType.WINDOW_MAXIMIZE, {}),
            (re.compile(r"\b(close window|ye band karo|close this|active window band karo)\b", re.I),
             IntentType.WINDOW_CLOSE_ACTIVE, {}),
            (re.compile(r"\b(snap left|left side karo|screen split left)\b", re.I),
             IntentType.WINDOW_SNAP_LEFT, {}),
            (re.compile(r"\b(snap right|right side karo|screen split right)\b", re.I),
             IntentType.WINDOW_SNAP_RIGHT, {}),

            # ──────────────── Media Controls ────────────────
            (re.compile(r"\b(play music|gaana chalao|song play karo|resume music)\b", re.I),
             IntentType.MEDIA_PLAY_PAUSE, {}),
            (re.compile(r"\b(pause music|gaana roko|pause karo)\b", re.I),
             IntentType.MEDIA_PLAY_PAUSE, {}),
            (re.compile(r"\b(next track|next song|agla gaana)\b", re.I),
             IntentType.MEDIA_NEXT, {}),
            (re.compile(r"\b(previous track|previous song|pichhla gaana)\b", re.I),
             IntentType.MEDIA_PREVIOUS, {}),

            # ──────────────── Web & YouTube Searches ────────────────
            (re.compile(r"\b(?:youtube par|on youtube|youtube search)\s+(.+)", re.I),
             IntentType.WEB_SEARCH_YOUTUBE, {"group": 1}),
            (re.compile(r"\b(?:google search|google par search karo|search for|search google)\s+(.+)", re.I),
             IntentType.WEB_SEARCH_GOOGLE, {"group": 1}),
            (re.compile(r"\b(?:github par search karo|search github for)\s+(.+)", re.I),
             IntentType.WEB_SEARCH_GITHUB, {"group": 1}),
            (re.compile(r"\b(?:stackoverflow search|error search karo)\s+(.+)", re.I),
             IntentType.WEB_STACKOVERFLOW, {"group": 1}),

            # ──────────────── Direct App Launching ────────────────
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+(chrome|browser|google chrome)\b", re.I),
             IntentType.APP_LAUNCH, {"app": "chrome"}),
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+(vs code|code|visual studio)\b", re.I),
             IntentType.APP_LAUNCH, {"app": "code"}),
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+(terminal|powershell|cmd|command prompt)\b", re.I),
             IntentType.APP_LAUNCH, {"app": "terminal"}),
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+(notepad|note pad)\b", re.I),
             IntentType.APP_LAUNCH, {"app": "notepad"}),
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+(calculator|calc|hisab)\b", re.I),
             IntentType.APP_LAUNCH, {"app": "calculator"}),
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+(spotify|music player)\b", re.I),
             IntentType.APP_LAUNCH, {"app": "spotify"}),
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+(task manager|taskmanager)\b", re.I),
             IntentType.APP_LAUNCH, {"app": "task_manager"}),
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+(discord)\b", re.I),
             IntentType.APP_LAUNCH, {"app": "discord"}),
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+(file explorer|my computer|this pc)\b", re.I),
             IntentType.APP_LAUNCH, {"app": "file_explorer"}),

            # Generic app launcher fallback: "open <any_name>"
            (re.compile(r"\b(?:open|launch|kholo|chalao)\s+([a-zA-Z0-9_\-\.\s]+)\b", re.I),
             IntentType.APP_LAUNCH, {"group": 1}),

            # ──────────────── Productivity & Notes ────────────────
            (re.compile(r"\b(?:note down|note karo|likh lo|take note)\s+(.+)", re.I),
             IntentType.NOTE_TAKE, {"group": 1}),
            (re.compile(r"\b(read my notes|mere notes padho|show notes|kya likha tha)\b", re.I),
             IntentType.NOTE_READ, {}),
            (re.compile(r"\b(?:to do add karo|add todo|task add karo)\s+(.+)", re.I),
             IntentType.TODO_ADD, {"group": 1}),
            (re.compile(r"\b(show todo|my tasks|list todo|mere kaam kya hai)\b", re.I),
             IntentType.TODO_LIST, {}),
            (re.compile(r"\b(?:timer lagao|set timer for)\s+(\d+)\s*(?:minute|minutes|min)\b", re.I),
             IntentType.TIMER_SET, {"extract_num": 1}),

            # ──────────────── Developer Utilities ────────────────
            (re.compile(r"\b(git status|git check karo)\b", re.I),
             IntentType.DEV_GIT_STATUS, {}),
            (re.compile(r"\b(ping test|check internet ping|latency check)\b", re.I),
             IntentType.DEV_NETWORK_PING, {}),
            (re.compile(r"\b(speed test|check internet speed|net speed)\b", re.I),
             IntentType.DEV_NETWORK_SPEED, {}),
            (re.compile(r"\b(organize desktop|desktop organize karo)\b", re.I),
             IntentType.DEV_ORGANIZE_DESKTOP, {}),
            (re.compile(r"\b(undo desktop|desktop restore|undo organize|desktop wapas karo)\b", re.I),
             IntentType.DEV_UNDO_DESKTOP, {}),
            (re.compile(r"\b(organize downloads|downloads folder organize karo)\b", re.I),
             IntentType.DEV_ORGANIZE_DOWNLOADS, {}),

            # ──────────────── Weather, News, Crypto ────────────────
            (re.compile(r"\b(?:weather in|mausam kaisa hai|weather report|temperature)\s*([a-zA-Z\s]*)?", re.I),
             IntentType.PLUGIN_WEATHER, {"city_group": 1}),
            (re.compile(r"\b(crypto price|bitcoin price|btc rate|ethereum)\b", re.I),
             IntentType.PLUGIN_CRYPTO, {}),
            (re.compile(r"\b(latest news|samachar sunao|khabrein|breaking news)\b", re.I),
             IntentType.PLUGIN_NEWS, {}),

            # ──────────────── Trivia & Fun ────────────────
            (re.compile(r"\b(tell me a joke|chutkula sunao|hasao|joke sunao)\b", re.I),
             IntentType.PLUGIN_JOKE, {}),
            (re.compile(r"\b(flip a coin|coin toss|sikka uchhalo|heads or tails)\b", re.I),
             IntentType.PLUGIN_COIN_FLIP, {}),
            (re.compile(r"\b(roll a dice|roll dice|pasa phenko)\b", re.I),
             IntentType.PLUGIN_DICE_ROLL, {}),

            # ──────────────── Time & Date ────────────────
            (re.compile(r"\b(what time is it|samay kya hua|kitne baje hai|current time)\b", re.I),
             IntentType.GENERAL_TIME, {}),
            (re.compile(r"\b(what date is today|aaj konsi date hai|today's date|konsa din hai)\b", re.I),
             IntentType.GENERAL_DATE, {}),

            # ──────────────── Voice Auth Commands ────────────────
            (re.compile(r"\b(enroll my voice|meri awaz save karo|register voice profile)\b", re.I),
             IntentType.AUTH_ENROLL, {}),
            (re.compile(r"\b(toggle voice lock|voice lock enable karo|voice lock band karo)\b", re.I),
             IntentType.AUTH_TOGGLE, {}),
            (re.compile(r"\b(voice security status|voice lock check karo)\b", re.I),
             IntentType.AUTH_STATUS, {}),

            # ──────────────── Facial Biometrics ────────────────
            (re.compile(r"\b(enroll my face|register face|face save karo)\b", re.I),
             IntentType.FACE_ENROLL, {}),
            (re.compile(r"\b(verify my face|check my face|chehra pehchano)\b", re.I),
             IntentType.FACE_VERIFY, {}),

            # ──────────────── Interactive RPG & Pomodoro ────────────────
            (re.compile(r"\b(start rpg|play rpg|cyberpunk game|start game)\b", re.I),
             IntentType.INTERACTIVE_RPG, {}),
            (re.compile(r"\b(start pomodoro|pomodoro shuru karo|focus session)\b", re.I),
             IntentType.POMODORO_START, {}),
            (re.compile(r"\b(stop pomodoro|pomodoro band karo)\b", re.I),
             IntentType.POMODORO_STOP, {}),

            # ──────────────── Habits & Daily Wellness ────────────────
            (re.compile(r"\b(?:drank water|water log karo|paani piya)\s*([0-9\.]*)?", re.I),
             IntentType.HABIT_LOG_WATER, {}),
            (re.compile(r"\b(?:logged coding|code kiya|coding hours)\s*([0-9\.]*)?", re.I),
             IntentType.HABIT_LOG_CODE, {}),
            (re.compile(r"\b(habit summary|aaj ka progress|wellness report)\b", re.I),
             IntentType.HABIT_SUMMARY, {}),
            (re.compile(r"\b(daily briefing|morning briefing|give me briefing|aaj ka overview)\b", re.I),
             IntentType.EXECUTIVE_BRIEFING, {}),

            # ──────────────── Display Night Light & Virtual Desktops ────────────────
            (re.compile(r"\b(night light on|warm light|amber light|peeli light)\b", re.I),
             IntentType.NIGHT_LIGHT_ON, {}),
            (re.compile(r"\b(night light off|cool light|daylight mode)\b", re.I),
             IntentType.NIGHT_LIGHT_OFF, {}),
            (re.compile(r"\b(new virtual desktop|naya desktop|create desktop)\b", re.I),
             IntentType.DESKTOP_VIRTUAL_NEW, {}),
            (re.compile(r"\b(next desktop|agla desktop)\b", re.I),
             IntentType.DESKTOP_VIRTUAL_NEXT, {}),
            (re.compile(r"\b(previous desktop|pichhla desktop)\b", re.I),
             IntentType.DESKTOP_VIRTUAL_PREV, {}),

            # ──────────────── Security & DevOps ────────────────
            (re.compile(r"\b(docker status|check docker|containers list)\b", re.I),
             IntentType.DOCKER_SUMMARY, {}),
            (re.compile(r"\b(security audit|check intrusions|hids audit|scan threats)\b", re.I),
             IntentType.SECURITY_IDS_AUDIT, {}),
            (re.compile(r"\b(wifi audit|wifi security check|check wifi cipher)\b", re.I),
             IntentType.SECURITY_WIFI_AUDIT, {}),

            # ──────────────── Ambient Soundscapes ────────────────
            (re.compile(r"\b(play rain sounds|baarish ki aawaz|rain soundscape)\b", re.I),
             IntentType.AMBIENT_RAIN, {}),
            (re.compile(r"\b(play binaural beats|alpha waves|focus drone)\b", re.I),
             IntentType.AMBIENT_BINAURAL, {}),
            (re.compile(r"\b(stop ambient sound|soundscape band karo|stop noise)\b", re.I),
             IntentType.AMBIENT_STOP, {}),
        ]

    def parse(self, text: str) -> Tuple[IntentType, Dict[str, Any]]:
        """
        Parse raw user utterance into structured IntentType and payload arguments.
        Falls back to IntentType.LLM_QUERY if no explicit native intent triggers.
        """
        clean = text.strip()
        if not clean:
            return IntentType.LLM_QUERY, {"query": ""}

        # Test against deterministic patterns
        for pattern, intent, params in self.patterns:
            match = pattern.search(clean)
            if match:
                payload: Dict[str, Any] = {"raw_text": clean}
                if "group" in params:
                    payload["query"] = match.group(params["group"]).strip()
                if "app" in params:
                    payload["app"] = params["app"]
                if "extract_num" in params:
                    try:
                        payload["value"] = int(match.group(params["extract_num"]))
                    except Exception:
                        payload["value"] = 50
                if "city_group" in params:
                    try:
                        city = match.group(params["city_group"]).strip()
                        payload["city"] = city if city else "Delhi"
                    except Exception:
                        payload["city"] = "Delhi"

                return intent, payload

        # Mathematical expressions ("54 * 23", "square root of 144")
        if re.search(r"\b(\d+[\s\+\-\*\/\^]+\d+|\bcalculate\b)", clean):
            return IntentType.PLUGIN_CALCULATOR, {"expression": clean}

        # No native intent matched: route to high-level Gemini cognitive brain
        return IntentType.LLM_QUERY, {"query": clean}


def get_intent_parser() -> IntentParser:
    return IntentParser()
