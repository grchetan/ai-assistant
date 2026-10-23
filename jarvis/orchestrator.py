"""
================================================================================
                    JARVIS MASTER SYSTEM ORCHESTRATOR
================================================================================
The central brain and runtime coordinator binding Audio Pipelines, Neural LLMs,
Intent Engine, Biometric Voiceprint Verification, Desktop Automation, Hardware
Telemetry, and Graphical User Interface into a unified autonomous system.
================================================================================
"""

import os
import sys
import time
import random
import threading
from typing import Optional, Any
import numpy as np

from jarvis.core.config import get_config
from jarvis.core.events import get_event_bus, EventType, Priority
from jarvis.core.state import get_state_manager, AssistantMode
from jarvis.core.logger import get_logger
from jarvis.core.security import SecurityVault

from jarvis.audio.sound_fx import get_sound_fx
from jarvis.audio.recorder import get_audio_recorder
from jarvis.audio.stt_engine import get_stt_engine
from jarvis.audio.tts_engine import get_tts_engine
from jarvis.audio.voice_auth import get_voice_auth

from jarvis.brain.llm_manager import get_llm_manager
from jarvis.brain.intent_engine import get_intent_parser, IntentType
from jarvis.brain.memory import get_memory
from jarvis.brain.smalltalk import get_smalltalk_engine

from jarvis.system.hardware_monitor import get_hardware_monitor
from jarvis.system.window_manager import get_window_manager
from jarvis.system.process_manager import get_process_manager
from jarvis.system.power_control import get_power_controller
from jarvis.system.volume_brightness import get_volume_controller
from jarvis.system.clipboard_manager import get_clipboard

from jarvis.automation.app_launcher import get_app_launcher
from jarvis.automation.browser_controller import get_browser_controller
from jarvis.automation.media_player import get_media_player
from jarvis.automation.screen_vision import get_screen_vision
from jarvis.automation.scheduler import get_scheduler
from jarvis.automation.notes_todo import get_notes_manager

from jarvis.plugins.plugin_manager import get_plugin_manager


class JarvisOrchestrator:
    """Master controller coordinating all system processes."""

    _instance: Optional["JarvisOrchestrator"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "JarvisOrchestrator":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JarvisOrchestrator, cls).__new__(cls)
                cls._instance._init_orchestrator()
            return cls._instance

    def _init_orchestrator(self) -> None:
        self.config = get_config()
        self.bus = get_event_bus()
        self.state = get_state_manager()
        self.logger = get_logger()
        self.vault = SecurityVault()

        # Audio
        self.sfx = get_sound_fx()
        self.recorder = get_audio_recorder()
        self.stt = get_stt_engine()
        self.tts = get_tts_engine()
        self.auth = get_voice_auth()

        # Brain
        self.llm = get_llm_manager()
        self.intent_parser = get_intent_parser()
        self.memory = get_memory()
        self.smalltalk = get_smalltalk_engine()

        # System & Automation
        self.hardware = get_hardware_monitor()
        self.window = get_window_manager()
        self.process = get_process_manager()
        self.power = get_power_controller()
        self.volume = get_volume_controller()
        self.clipboard = get_clipboard()
        self.apps = get_app_launcher()
        self.browser = get_browser_controller()
        self.media = get_media_player()
        self.vision = get_screen_vision()
        self.scheduler = get_scheduler()
        self.notes = get_notes_manager()
        self.plugins = get_plugin_manager()

        self._running = False
        self._loop_thread: Optional[threading.Thread] = None
        self._idle_interval = self.config.get("llm", "idle_interval_seconds", 45)

    def bootstrap(self) -> None:
        """Start all subsystem background engines."""
        self.logger.info("Bootstrap sequence initiated...", "KERNEL")
        self.sfx.play_boot()

        # 1. Start hardware telemetry polling
        self.hardware.start(interval=2.0)

        # 2. Calibrate audio in background
        threading.Thread(target=self.stt.calibrate, kwargs={"duration": 1.0}, daemon=True).start()

        # 3. Live RMS monitoring stream
        self.recorder.start_monitoring_stream()

        # 4. Spoken greeting
        user_name = self.config.get("system", "user_name", "Sir")
        greeting = self.smalltalk.get_greeting(user_name)
        self.speak(greeting)

        # 5. Start main conversation loop
        self._running = True
        self._loop_thread = threading.Thread(
            target=self._assistant_loop,
            name="JarvisMasterLoop",
            daemon=True
        )
        self._loop_thread.start()
        self.logger.success("JARVIS Online — All systems operational!", "KERNEL")

    def speak(self, text: str, block: bool = False) -> None:
        """Central spoken output helper logging to terminal and TTS."""
        self.logger.info(f'JARVIS: "{text}"', "SPEECH", "#00ff99")
        self.tts.speak(text, block=block)

    def _assistant_loop(self) -> None:
        """Continuous background listening and decision loop."""
        time.sleep(1.0) # allow initial greeting
        while self._running:
            try:
                # Do NOT listen while the assistant is speaking through the speakers!
                while self.tts.is_busy() and self._running:
                    time.sleep(0.12)

                # Acoustic decay buffer so speaker audio echo doesn't trigger the mic
                time.sleep(0.35)

                if not self._running:
                    break

                # Listen for user speech
                text, audio_data = self.stt.listen_and_transcribe(timeout=3.5, phrase_limit=12.0)

                if not self._running:
                    break

                # 1. User said something
                if text:
                    self.execute_command(text, audio_data)
                    continue

                # 2. Pure silence or ambient room sound:
                # Do NOT nag the user. Stay quietly in listening standby.
                time.sleep(0.1)

                # 3. Check proactive idle conversation timer (45 seconds)
                if self.config.get("llm", "proactive_idle_chat", True):
                    idle_secs = self.state.idle_time
                    if idle_secs > self._idle_interval and not self.tts.is_busy():
                        idle_msg = self.smalltalk.get_proactive_idle_message()
                        self.logger.info(f"Proactive chat triggered: {idle_msg}", "BRAIN")
                        self.speak(idle_msg)

            except Exception as e:
                self.logger.error(f"Error in main assistant loop: {e}", "KERNEL")
                time.sleep(0.5)

    def execute_command(self, raw_command: str, audio_data: Optional[Any] = None) -> str:
        """Process and execute any user command (spoken or typed)."""
        cmd = raw_command.strip()
        if not cmd:
            return ""

        # Stop old speech before processing new command
        self.tts.stop()
        self.state.set_mode(AssistantMode.PROCESSING)
        self.logger.info(f'Processing command: "{cmd}"', "ORCH")

        # 1. Voice biometric authorization check (if audio data supplied)
        if audio_data and self.auth.enabled:
            # Convert audio raw frames to numpy array
            try:
                raw_bytes = audio_data.get_raw_data()
                pcm = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                verified, score = self.auth.verify_speaker(pcm, audio_data.sample_rate)
                if not verified:
                    rejection_msg = "Sir, aapki aawaz recognize nahi hui. Voice security lock active hai!"
                    self.speak(rejection_msg)
                    return rejection_msg
            except Exception as e:
                self.logger.warning(f"Voice auth check failed: {e}", "AUTH")

        # 2. Parse command into structured intent
        intent, payload = self.intent_parser.parse(cmd)
        self.logger.info(f"Matched Intent: {intent.value}", "BRAIN")

        response_text = ""

        # ──────────────── INTENT EXECUTION MATRIX ────────────────
        if intent == IntentType.GENERAL_EXIT:
            response_text = "Good bye sir! Systems shutting down."
            self.speak(response_text, block=True)
            self.shutdown()
            return response_text

        elif intent == IntentType.SYSTEM_SHUTDOWN:
            _, response_text = self.power.shutdown(30)
            self.speak(response_text)

        elif intent == IntentType.SYSTEM_CANCEL_SHUTDOWN:
            _, response_text = self.power.cancel_shutdown()
            self.speak(response_text)

        elif intent == IntentType.SYSTEM_RESTART:
            _, response_text = self.power.restart(5)
            self.speak(response_text)

        elif intent == IntentType.SYSTEM_SLEEP:
            _, response_text = self.power.sleep()
            self.speak(response_text)

        elif intent == IntentType.SYSTEM_LOCK:
            _, response_text = self.power.lock()
            self.speak(response_text)

        elif intent == IntentType.SYSTEM_TAKE_SCREENSHOT:
            success, msg, _ = self.vision.capture_screenshot()
            response_text = msg
            self.speak(response_text)

        elif intent == IntentType.SYSTEM_METRICS:
            response_text = self.hardware.get_summary_speech()
            self.speak(response_text)

        elif intent == IntentType.SYSTEM_BATTERY:
            snap = self.hardware.collect_snapshot()
            bat = snap.get("battery_percent")
            response_text = f"Sir, battery {bat}% par hai." if bat is not None else "Direct power supply connected hai sir."
            self.speak(response_text)

        elif intent == IntentType.VOLUME_MUTE or intent == IntentType.VOLUME_UNMUTE:
            response_text = self.volume.toggle_mute()
            self.speak(response_text)

        elif intent == IntentType.VOLUME_UP:
            response_text = self.volume.volume_up()
            self.speak(response_text)

        elif intent == IntentType.VOLUME_DOWN:
            response_text = self.volume.volume_down()
            self.speak(response_text)

        elif intent == IntentType.VOLUME_SET:
            target = payload.get("value", 50)
            response_text = self.volume.set_volume_percent(target)
            self.speak(response_text)

        elif intent == IntentType.WINDOW_MINIMIZE_ALL:
            self.window.minimize_all()
            response_text = "Sabhi windows minimize kar di gayi hain sir."
            self.speak(response_text)

        elif intent == IntentType.WINDOW_MAXIMIZE:
            self.window.maximize_active()
            response_text = "Window maximize kar di sir."
            self.speak(response_text)

        elif intent == IntentType.WINDOW_CLOSE_ACTIVE:
            self.window.close_active()
            response_text = "Window close kar di sir."
            self.speak(response_text)

        elif intent == IntentType.WINDOW_SNAP_LEFT:
            self.window.snap_left()
            response_text = "Left side split kar diya sir."
            self.speak(response_text)

        elif intent == IntentType.WINDOW_SNAP_RIGHT:
            self.window.snap_right()
            response_text = "Right side split kar diya sir."
            self.speak(response_text)

        elif intent == IntentType.APP_LAUNCH:
            app_name = payload.get("app") or payload.get("query", "notepad")
            _, response_text = self.apps.launch(app_name)
            self.speak(response_text)

        elif intent == IntentType.WEB_SEARCH_GOOGLE:
            q = payload.get("query", "")
            response_text = self.browser.search_google(q)
            self.speak(response_text)

        elif intent == IntentType.WEB_SEARCH_YOUTUBE:
            q = payload.get("query", "")
            response_text = self.browser.search_youtube(q)
            self.speak(response_text)

        elif intent == IntentType.WEB_SEARCH_GITHUB:
            q = payload.get("query", "")
            response_text = self.browser.search_github(q)
            self.speak(response_text)

        elif intent == IntentType.WEB_STACKOVERFLOW:
            q = payload.get("query", "")
            response_text = self.browser.search_stackoverflow(q)
            self.speak(response_text)

        elif intent == IntentType.MEDIA_PLAY_PAUSE:
            response_text = self.media.play_pause()
            self.speak(response_text)

        elif intent == IntentType.MEDIA_NEXT:
            response_text = self.media.next_track()
            self.speak(response_text)

        elif intent == IntentType.MEDIA_PREVIOUS:
            response_text = self.media.previous_track()
            self.speak(response_text)

        elif intent == IntentType.NOTE_TAKE:
            content = payload.get("query", "")
            response_text = self.notes.add_note(content)
            self.speak(response_text)

        elif intent == IntentType.NOTE_READ:
            response_text = self.notes.read_notes()
            self.speak(response_text)

        elif intent == IntentType.TODO_ADD:
            content = payload.get("query", "")
            response_text = self.notes.add_todo(content)
            self.speak(response_text)

        elif intent == IntentType.TODO_LIST:
            response_text = self.notes.list_todos()
            self.speak(response_text)

        elif intent == IntentType.TIMER_SET:
            mins = payload.get("value", 5)
            self.scheduler.set_timer(mins, label=f"{mins} min timer", callback=lambda: self.speak(f"Sir! Aapka {mins} minute ka timer khatam ho gaya!"))
            response_text = f"{mins} minute ka timer set kar diya sir."
            self.speak(response_text)

        elif intent == IntentType.DEV_GIT_STATUS:
            response_text = self.terminal_runner_git()
            self.speak(response_text)

        elif intent == IntentType.DEV_NETWORK_PING:
            from jarvis.dev.network_tools import get_network_diagnostics
            response_text = get_network_diagnostics().ping_host()
            self.speak(response_text)

        elif intent == IntentType.DEV_NETWORK_SPEED:
            from jarvis.dev.network_tools import get_network_diagnostics
            _, _, response_text = get_network_diagnostics().measure_internet_speed()
            self.speak(response_text)

        elif intent == IntentType.DEV_NETWORK_IP:
            from jarvis.dev.network_tools import get_network_diagnostics
            response_text = get_network_diagnostics().get_ip_summary_speech()
            self.speak(response_text)

        elif intent == IntentType.DEV_ORGANIZE_DESKTOP:
            from jarvis.dev.file_organizer import get_file_organizer
            response_text = get_file_organizer().organize_desktop()
            self.speak(response_text)

        elif intent == IntentType.DEV_UNDO_DESKTOP:
            from jarvis.dev.file_organizer import get_file_organizer
            response_text = get_file_organizer().undo_desktop()
            self.speak(response_text)

        elif intent == IntentType.DEV_ORGANIZE_DOWNLOADS:
            from jarvis.dev.file_organizer import get_file_organizer
            response_text = get_file_organizer().organize_downloads()
            self.speak(response_text)

        elif intent == IntentType.PLUGIN_WEATHER:
            _, response_text = self.plugins.execute_plugin("weather", cmd, payload)
            self.speak(response_text)

        elif intent == IntentType.PLUGIN_CRYPTO:
            _, response_text = self.plugins.execute_plugin("crypto_stocks", cmd, payload)
            self.speak(response_text)

        elif intent == IntentType.PLUGIN_NEWS:
            _, response_text = self.plugins.execute_plugin("news", cmd, payload)
            self.speak(response_text)

        elif intent == IntentType.PLUGIN_CALCULATOR:
            _, response_text = self.plugins.execute_plugin("calculator", cmd, payload)
            self.speak(response_text)

        elif intent == IntentType.PLUGIN_JOKE or intent == IntentType.PLUGIN_COIN_FLIP or intent == IntentType.PLUGIN_DICE_ROLL:
            _, response_text = self.plugins.execute_plugin("trivia_games", cmd, payload)
            self.speak(response_text)

        elif intent == IntentType.GENERAL_TIME:
            t_str = time.strftime("%I:%M %p")
            response_text = f"Sir, abhi ka samay {t_str} hai."
            self.speak(response_text)

        elif intent == IntentType.GENERAL_DATE:
            d_str = time.strftime("%A, %d %B %Y")
            response_text = f"Sir, aaj {d_str} hai."
            self.speak(response_text)

        elif intent == IntentType.AUTH_ENROLL:
            threading.Thread(target=self.enroll_voice_wizard, daemon=True).start()
            return "Voice enrollment started."

        elif intent == IntentType.AUTH_TOGGLE:
            curr = self.auth.enabled
            self.auth.enabled = not curr
            self.config.set("voice_auth", "enabled", self.auth.enabled)
            status_str = "ACTIVE 🔐" if self.auth.enabled else "DISABLED"
            response_text = f"Voice lock ab {status_str} hai sir."
            self.speak(response_text)

        elif intent == IntentType.AUTH_STATUS:
            status_str = "Active hai" if self.auth.enabled else "Disabled hai"
            response_text = f"Sir, voice authentication security abhi {status_str}."
            self.speak(response_text)

        elif intent == IntentType.FACE_ENROLL:
            from jarvis.vision.face_auth import get_face_biometrics
            self.speak("Optical camera sensor activate ho raha hai sir. Camera ki taraf dekhein...", block=True)
            success, msg = get_face_biometrics().enroll_face(sample_count=4)
            response_text = msg
            self.speak(response_text)

        elif intent == IntentType.FACE_VERIFY:
            from jarvis.vision.face_auth import get_face_biometrics
            self.speak("Verifying optical facial biometric identity...", block=True)
            matched, score, msg = get_face_biometrics().verify_live_face()
            response_text = msg
            self.speak(response_text)

        elif intent == IntentType.INTERACTIVE_RPG:
            from jarvis.interactive.interactive_rpg import get_rpg_game
            rpg = get_rpg_game()
            if not rpg.is_active:
                response_text = rpg.start_game()
            else:
                response_text = rpg.process_player_action(cmd)
            self.speak(response_text)

        elif intent == IntentType.POMODORO_START:
            from jarvis.interactive.pomodoro_timer import get_pomodoro_coach
            pomo = get_pomodoro_coach()
            pomo.set_callback(self.speak)
            response_text = pomo.start_session(25)
            self.speak(response_text)

        elif intent == IntentType.POMODORO_STOP:
            from jarvis.interactive.pomodoro_timer import get_pomodoro_coach
            response_text = get_pomodoro_coach().stop_session()
            self.speak(response_text)

        elif intent == IntentType.HABIT_LOG_WATER:
            from jarvis.interactive.habit_tracker import get_habit_tracker
            response_text = get_habit_tracker().log_water(0.5)
            self.speak(response_text)

        elif intent == IntentType.HABIT_LOG_CODE:
            from jarvis.interactive.habit_tracker import get_habit_tracker
            response_text = get_habit_tracker().log_coding_hours(1.0)
            self.speak(response_text)

        elif intent == IntentType.HABIT_SUMMARY:
            from jarvis.interactive.habit_tracker import get_habit_tracker
            response_text = get_habit_tracker().get_today_summary()
            self.speak(response_text)

        elif intent == IntentType.EXECUTIVE_BRIEFING:
            from jarvis.interactive.system_status_announcer import get_executive_briefing
            response_text = get_executive_briefing().generate_full_briefing()
            self.speak(response_text)

        elif intent == IntentType.NIGHT_LIGHT_ON:
            from jarvis.desktop.display_color_calibrator import get_display_calibrator
            _, response_text = get_display_calibrator().set_night_light_warm()
            self.speak(response_text)

        elif intent == IntentType.NIGHT_LIGHT_OFF:
            from jarvis.desktop.display_color_calibrator import get_display_calibrator
            _, response_text = get_display_calibrator().reset_daylight_cool()
            self.speak(response_text)

        elif intent == IntentType.DESKTOP_VIRTUAL_NEW:
            from jarvis.desktop.virtual_desktop_manager import get_virtual_desktop_manager
            response_text = get_virtual_desktop_manager().create_new_desktop()
            self.speak(response_text)

        elif intent == IntentType.DESKTOP_VIRTUAL_NEXT:
            from jarvis.desktop.virtual_desktop_manager import get_virtual_desktop_manager
            response_text = get_virtual_desktop_manager().switch_next_desktop()
            self.speak(response_text)

        elif intent == IntentType.DESKTOP_VIRTUAL_PREV:
            from jarvis.desktop.virtual_desktop_manager import get_virtual_desktop_manager
            response_text = get_virtual_desktop_manager().switch_prev_desktop()
            self.speak(response_text)

        elif intent == IntentType.DOCKER_SUMMARY:
            from jarvis.devops.docker_orchestrator import get_docker_orchestrator
            response_text = get_docker_orchestrator().get_summary_speech()
            self.speak(response_text)

        elif intent == IntentType.SECURITY_IDS_AUDIT:
            from jarvis.security.intrusion_detector import get_intrusion_detector
            anomalies = get_intrusion_detector().audit_active_connections()
            if not anomalies:
                response_text = "Security audit complete sir. Zero unauthorized socket connections or rogue listeners detected!"
            else:
                response_text = f"Security Alert sir! {len(anomalies)} potential suspicious sockets detected."
            self.speak(response_text)

        elif intent == IntentType.SECURITY_WIFI_AUDIT:
            from jarvis.security.wifi_security_auditor import get_wifi_auditor
            response_text = get_wifi_auditor().get_audit_summary_speech()
            self.speak(response_text)

        elif intent == IntentType.AMBIENT_RAIN:
            from jarvis.studio.ambient_soundscape import get_ambient_soundscape
            get_ambient_soundscape().start_rain_soundscape()
            response_text = "Cyberpunk rain ambience started sir. Focus mode active."
            self.speak(response_text)

        elif intent == IntentType.AMBIENT_BINAURAL:
            from jarvis.studio.ambient_soundscape import get_ambient_soundscape
            get_ambient_soundscape().start_binaural_drone()
            response_text = "Alpha wave binaural drone active for deep study."
            self.speak(response_text)

        elif intent == IntentType.AMBIENT_STOP:
            from jarvis.studio.ambient_soundscape import get_ambient_soundscape
            get_ambient_soundscape().stop()
            response_text = "Ambient soundscape halted sir."
            self.speak(response_text)

        else:
            # ──────────────── FALLBACK TO GEMINI LLM BRAIN ────────────────
            response_text = self.llm.generate_response(cmd)
            self.speak(response_text)

        self.state.increment_command_count()
        self.state.set_mode(AssistantMode.IDLE)
        return response_text

    def terminal_runner_git(self) -> str:
        from jarvis.dev.terminal_runner import get_terminal_runner
        return get_terminal_runner().git_status()

    def enroll_voice_wizard(self) -> None:
        """Interactive multi-sample voice enrollment wizard."""
        self.logger.info("Starting voice enrollment wizard...", "AUTH")
        self.speak("Voice registration process shuru ho raha hai sir. Kripya 3 alag-alag baar bolein jab beep sunai de.", block=True)

        samples = []
        prompts = [
            "Pehla sample: Apne normal aawaz me bolein: 'JARVIS activate system'",
            "Dusra sample: Dobara bolein: 'Verify my voice authorization'",
            "Teesra sample: Ek baar aur bolein: 'Access granted JARVIS'"
        ]

        for idx, prompt_text in enumerate(prompts):
            self.speak(prompt_text, block=True)
            time.sleep(0.5)
            self.sfx.play_listening()
            time.sleep(0.3)

            # Record 3.5 seconds
            try:
                audio_np, sr = self.recorder.record_seconds(3.5)
                vec = self.auth.extract_features(audio_np, sr)
                if vec is not None:
                    samples.append(vec)
                    self.logger.success(f"Sample {idx+1} recorded successfully.", "AUTH")
                    self.sfx.play_success()
                else:
                    self.logger.warning(f"Sample {idx+1} unclear, skipping.", "AUTH")
            except Exception as e:
                self.logger.error(f"Error capturing sample: {e}", "AUTH")
            time.sleep(1.0)

        if len(samples) >= 2:
            self.auth.save_enrolled_profile(samples)
            self.speak("Sir, aapka biometric voice profile successfully register ho gaya hai! Voice lock ab active hai.", block=True)
        else:
            self.speak("Sir, sufficient clear audio samples record nahi ho paaye. Kripya dobara try karein.", block=True)

    def shutdown(self) -> None:
        """Graceful shutdown of all subsystems."""
        self._running = False
        self.recorder.stop_monitoring_stream()
        self.hardware.stop()
        self.tts.stop()
        self.logger.info("All JARVIS systems cleanly terminated.", "KERNEL")


def get_orchestrator() -> JarvisOrchestrator:
    return JarvisOrchestrator()
