"""
================================================================================
                    JARVIS AUTOMATED SYSTEM TEST SUITE
================================================================================
Comprehensive unit and integration test suite verifying core configuration,
event broker dispatch, state machines, audio synthesis, intent parsing,
biometrics, and hardware telemetry.
================================================================================
"""

import os
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

import unittest
import numpy as np
import time

from jarvis.core.config import get_config
from jarvis.core.events import get_event_bus, EventType, Priority
from jarvis.core.state import get_state_manager, AssistantMode
from jarvis.core.security import SecurityVault, SafetyGuard
from jarvis.core.logger import get_logger

from jarvis.audio.sound_fx import get_sound_fx
from jarvis.audio.voice_auth import get_voice_auth

from jarvis.brain.intent_engine import get_intent_parser, IntentType
from jarvis.brain.knowledge_base import KnowledgeBase
from jarvis.brain.nlp_pipeline import NLPPipeline
from jarvis.brain.memory import get_memory

from jarvis.system.hardware_monitor import get_hardware_monitor
from jarvis.plugins.plugin_manager import get_plugin_manager


class TestJarvisCore(unittest.TestCase):
    """Test core configuration, state, and event dispatch."""

    def test_config_manager(self):
        config = get_config()
        self.assertIsNotNone(config)
        app_name = config.get("system", "app_name")
        self.assertTrue(len(app_name) > 0)
        theme = config.get_theme("ARC_REACTOR")
        self.assertIn("accent", theme)

    def test_event_bus(self):
        bus = get_event_bus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe(EventType.UI_LOG_MESSAGE, handler)
        bus.publish(EventType.UI_LOG_MESSAGE, {"msg": "test"}, sync=True)
        self.assertTrue(len(received) > 0)
        bus.unsubscribe(EventType.UI_LOG_MESSAGE, handler)

    def test_state_manager(self):
        state = get_state_manager()
        state.set_mode(AssistantMode.PROCESSING)
        self.assertEqual(state.mode, AssistantMode.PROCESSING)
        state.set_mode(AssistantMode.IDLE)
        snap = state.get_telemetry_snapshot()
        self.assertEqual(snap["mode"], "IDLE")

    def test_security_vault(self):
        vault = SecurityVault()
        vault.set_secret("TEST_SECRET_KEY", "quantum_pass_123")
        val = vault.get_secret("TEST_SECRET_KEY")
        self.assertEqual(val, "quantum_pass_123")
        vault.delete_secret("TEST_SECRET_KEY")

    def test_safety_guard(self):
        self.assertTrue(SafetyGuard.is_command_safe("python --version"))
        self.assertFalse(SafetyGuard.is_command_safe("format c:"))


class TestJarvisAudio(unittest.TestCase):
    """Test audio synthesis and biometric math."""

    def test_sound_fx_synthesis(self):
        sfx = get_sound_fx()
        self.assertIsNotNone(sfx)

    def test_biometric_feature_extraction(self):
        auth = get_voice_auth()
        # Synthetic sine wave simulating 1 second of speech at 16000Hz
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)

        feat = auth.extract_features(audio, sr)
        self.assertIsNotNone(feat)
        self.assertEqual(len(feat), 28)


class TestJarvisBrain(unittest.TestCase):
    """Test Intent classification and NLP processing."""

    def setUp(self):
        self.parser = get_intent_parser()

    def test_shutdown_intent(self):
        intent, _ = self.parser.parse("pc band kar do")
        self.assertEqual(intent, IntentType.SYSTEM_SHUTDOWN)

    def test_cancel_shutdown(self):
        intent, _ = self.parser.parse("cancel shutdown")
        self.assertEqual(intent, IntentType.SYSTEM_CANCEL_SHUTDOWN)

    def test_screenshot_intent(self):
        intent, _ = self.parser.parse("take a screenshot please")
        self.assertEqual(intent, IntentType.SYSTEM_TAKE_SCREENSHOT)

    def test_volume_intent(self):
        intent, payload = self.parser.parse("volume 70 percent karo")
        self.assertEqual(intent, IntentType.VOLUME_SET)
        self.assertEqual(payload.get("value"), 70)

    def test_app_launch_intent(self):
        intent, payload = self.parser.parse("open chrome")
        self.assertEqual(intent, IntentType.APP_LAUNCH)
        self.assertEqual(payload.get("app"), "chrome")

    def test_youtube_search_intent(self):
        intent, payload = self.parser.parse("youtube par lofi hip hop chalao")
        self.assertEqual(intent, IntentType.WEB_SEARCH_YOUTUBE)
        self.assertIn("lofi", payload.get("query", ""))

    def test_weather_intent(self):
        intent, payload = self.parser.parse("weather in Mumbai")
        self.assertEqual(intent, IntentType.PLUGIN_WEATHER)
        self.assertEqual(payload.get("city"), "Mumbai")

    def test_sentiment_analysis(self):
        res_pos = NLPPipeline.analyze_sentiment("JARVIS you are awesome and fantastic!")
        self.assertEqual(res_pos["label"], "POSITIVE")

        res_neg = NLPPipeline.analyze_sentiment("This is a horrible bug and error")
        self.assertEqual(res_neg["label"], "NEGATIVE")

    def test_knowledge_base(self):
        ans = KnowledgeBase.lookup("capital of Japan")
        self.assertIsNotNone(ans)
        self.assertIn("Tokyo", ans)


class TestJarvisPlugins(unittest.TestCase):
    """Test plugin registration and execution."""

    def test_plugin_manager(self):
        mgr = get_plugin_manager()
        self.assertTrue(len(mgr._plugins) >= 5)
        self.assertIn("weather", mgr._plugins)
        self.assertIn("calculator", mgr._plugins)

    def test_calculator_plugin(self):
        mgr = get_plugin_manager()
        success, speech = mgr.execute_plugin("calculator", "calculate 25 * 4", {"expression": "25 * 4"})
        self.assertTrue(success)
        self.assertIn("100", speech)


if __name__ == "__main__":
    unittest.main()
