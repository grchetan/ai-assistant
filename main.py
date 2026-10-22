"""
================================================================================
                    J.A.R.V.I.S. QUANTUM OS ENTRY POINT
================================================================================
Unified runtime bootstrap for GUI and CLI environments with self-diagnostic
test suite, secure credential management, and argument parsing.
================================================================================
"""

import os
import sys
import argparse
import threading
from pathlib import Path

# Ensure workspace root is in sys.path
WORKSPACE_DIR = Path(__file__).resolve().parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from jarvis.core.logger import get_logger
from jarvis.core.config import get_config
from jarvis.core.security import SecurityVault
from jarvis.orchestrator import get_orchestrator
from jarvis.ui.gui import JarvisHUD


def run_self_diagnostics() -> bool:
    """Run integrity and dependency checks across all subsystems."""
    logger = get_logger()
    logger.info("Starting JARVIS Hardware & Module Self-Diagnostics...", "TEST")

    all_passed = True
    tests = [
        ("Core Configuration", lambda: get_config() is not None),
        ("Security Vault", lambda: SecurityVault() is not None),
        ("Sound Synthesizer", lambda: __import__("jarvis.audio.sound_fx").audio.sound_fx.get_sound_fx() is not None),
        ("Biometric Engine", lambda: __import__("jarvis.audio.voice_auth").audio.voice_auth.get_voice_auth() is not None),
        ("Cognitive Memory", lambda: __import__("jarvis.brain.memory").brain.memory.get_memory() is not None),
        ("Hardware Telemetry", lambda: __import__("jarvis.system.hardware_monitor").system.hardware_monitor.get_hardware_monitor() is not None),
        ("Desktop Automation", lambda: __import__("jarvis.automation.app_launcher").automation.app_launcher.get_app_launcher() is not None),
        ("Plugin Ecosystem", lambda: len(__import__("jarvis.plugins.plugin_manager").plugins.plugin_manager.get_plugin_manager()._plugins) > 0),
    ]

    for name, test_fn in tests:
        try:
            res = test_fn()
            if res:
                logger.success(f"PASSED: {name}", "TEST")
            else:
                logger.error(f"FAILED: {name}", "TEST")
                all_passed = False
        except Exception as e:
            logger.error(f"ERROR: {name} - {e}", "TEST")
            all_passed = False

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Quantum AI Operating System")
    parser.add_argument("--cli", action="store_true", help="Launch in headless terminal CLI mode")
    parser.add_argument("--test", action="store_true", help="Run system diagnostics self-test")
    parser.add_argument("--enroll", action="store_true", help="Launch biometric voice enrollment wizard")
    parser.add_argument("--set-key", type=str, help="Save Google Gemini API key into secure vault")
    parser.add_argument("--theme", type=str, help="Select active theme (ARC_REACTOR, IRON_MAN, CYBERPUNK, MATRIX, MIDNIGHT_STEALTH)")

    args = parser.parse_args()
    logger = get_logger()
    config = get_config()

    if args.set_key:
        vault = SecurityVault()
        vault.set_secret("GEMINI_API_KEY", args.set_key)
        logger.success("Gemini API key encrypted and saved successfully!", "VAULT")
        return

    if args.theme:
        config.set("system", "active_theme", args.theme.upper())
        logger.info(f"Theme set to: {args.theme.upper()}", "CONFIG")

    if args.test:
        success = run_self_diagnostics()
        sys.exit(0 if success else 1)

    # Initialize master orchestrator
    orchestrator = get_orchestrator()

    if args.enroll:
        orchestrator.enroll_voice_wizard()
        return

    if args.cli:
        # CLI Headless Mode
        logger.info("Starting JARVIS in Headless CLI Mode...", "KERNEL")
        orchestrator.bootstrap()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            orchestrator.shutdown()
            logger.info("Exiting CLI mode.", "KERNEL")
    else:
        # Full High-Tech HUD GUI Mode
        logger.info("Launching JARVIS High-Tech HUD Graphical User Interface...", "GUI")
        
        # Start orchestrator in background thread
        threading.Thread(target=orchestrator.bootstrap, daemon=True).start()

        # Launch Tkinter GUI on main thread
        app = JarvisHUD(command_handler=orchestrator.execute_command)
        
        def _on_close():
            orchestrator.shutdown()
            app.destroy()

        app.protocol("WM_DELETE_WINDOW", _on_close)
        app.mainloop()


if __name__ == "__main__":
    main()
