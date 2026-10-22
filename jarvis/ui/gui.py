"""
================================================================================
                    JARVIS ADVANCED HUD DESKTOP GUI
================================================================================
High-Tech Cyberpunk & Iron Man Graphical User Interface built with pure
Tkinter featuring live animated Arc Reactor canvas, real-time hardware gauges,
streaming color terminal, quick action buttons, and configuration modals.
================================================================================
"""

import time
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Callable, Dict, Any

from jarvis.core.config import get_config
from jarvis.core.events import get_event_bus, EventType, Event
from jarvis.core.state import get_state_manager, AssistantMode
from jarvis.core.logger import get_logger
from jarvis.ui.hud_canvas import ArcReactorHUD
from jarvis.core.security import SecurityVault


class JarvisHUD(tk.Tk):
    """Main Application GUI Window."""

    def __init__(self, command_handler: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.config = get_config()
        self.bus = get_event_bus()
        self.state = get_state_manager()
        self.logger = get_logger()
        self.vault = SecurityVault()
        self.command_handler = command_handler

        self.title("J.A.R.V.I.S. • Quantum Cognitive AI System")
        self.geometry("1100x720")
        self.minsize(980, 640)

        # Theme
        self.theme = self.config.get_theme()
        self.configure(bg=self.theme["bg_primary"])

        self._log_queue: queue.Queue = queue.Queue()
        self._setup_styles()
        self._build_ui()
        self._subscribe_events()
        self._start_gui_loops()

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=8, troughcolor=self.theme["bg_secondary"],
                        background=self.theme["accent"], borderwidth=0)

    def _build_ui(self) -> None:
        # ──────────────── TOP STATUS HEADER ────────────────
        header = tk.Frame(self, bg=self.theme["bg_secondary"], height=52)
        header.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(10, 6))

        title_lbl = tk.Label(
            header,
            text="J.A.R.V.I.S.  //  QUANTUM OS",
            font=("Segoe UI", 14, "bold"),
            fg=self.theme["accent"],
            bg=self.theme["bg_secondary"]
        )
        title_lbl.pack(side=tk.LEFT, padx=16, pady=8)

        self.lbl_mode_badge = tk.Label(
            header,
            text="[ STANDBY ]",
            font=("Consolas", 11, "bold"),
            fg=self.theme["success"],
            bg=self.theme["bg_secondary"]
        )
        self.lbl_mode_badge.pack(side=tk.LEFT, padx=12)

        # Theme selector dropdown
        theme_names = self.config.get_available_themes()
        self.theme_var = tk.StringVar(value=self.config.get("system", "active_theme", "ARC_REACTOR"))
        theme_menu = ttk.Combobox(
            header,
            textvariable=self.theme_var,
            values=theme_names,
            state="readonly",
            width=14
        )
        theme_menu.pack(side=tk.RIGHT, padx=12, pady=10)
        theme_menu.bind("<<ComboboxSelected>>", self._on_theme_changed)

        theme_lbl = tk.Label(header, text="THEME:", font=("Consolas", 9, "bold"),
                             fg=self.theme["text_secondary"], bg=self.theme["bg_secondary"])
        theme_lbl.pack(side=tk.RIGHT, padx=4)

        # ──────────────── MAIN CONTENT (3 COLUMNS) ────────────────
        content_frame = tk.Frame(self, bg=self.theme["bg_primary"])
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=6)

        # LEFT: Arc Reactor & Audio
        left_col = tk.Frame(content_frame, bg=self.theme["bg_secondary"], width=350)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_col.pack_propagate(False)

        self.hud_canvas = ArcReactorHUD(
            left_col,
            width=340,
            height=340,
            bg=self.theme["bg_secondary"]
        )
        self.hud_canvas.set_theme_colors(
            ring_color=self.theme["canvas_ring"],
            core_color=self.theme["canvas_core"],
            bg_color=self.theme["bg_secondary"]
        )
        self.hud_canvas.pack(side=tk.TOP, pady=10)

        # Audio telemetry metrics
        self.lbl_audio_rms = tk.Label(
            left_col,
            text="MIC ENERGY: 0.0 RMS",
            font=("Consolas", 10),
            fg=self.theme["text_secondary"],
            bg=self.theme["bg_secondary"]
        )
        self.lbl_audio_rms.pack(pady=4)

        # Voice auth status pill
        self.lbl_voice_auth = tk.Label(
            left_col,
            text="VOICE LOCK: DISABLED",
            font=("Consolas", 9, "bold"),
            fg=self.theme["text_dim"],
            bg=self.theme["bg_secondary"]
        )
        self.lbl_voice_auth.pack(pady=4)

        # Left action buttons
        btn_frame_left = tk.Frame(left_col, bg=self.theme["bg_secondary"])
        btn_frame_left.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=16)

        btn_enroll = tk.Button(
            btn_frame_left,
            text="🔐 Enroll Voice",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_card"],
            fg=self.theme["accent"],
            activebackground=self.theme["accent"],
            activeforeground="#000000",
            relief=tk.FLAT,
            command=self._open_enrollment_dialog
        )
        btn_enroll.pack(fill=tk.X, pady=3)

        btn_api_key = tk.Button(
            btn_frame_left,
            text="⚙ Gemini API Key",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_card"],
            fg=self.theme["text_primary"],
            relief=tk.FLAT,
            command=self._open_api_key_dialog
        )
        btn_api_key.pack(fill=tk.X, pady=3)

        # CENTER: Terminal Log Stream
        center_col = tk.Frame(content_frame, bg=self.theme["bg_secondary"])
        center_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        term_header = tk.Frame(center_col, bg=self.theme["bg_card"])
        term_header.pack(fill=tk.X, padx=2, pady=2)
        tk.Label(term_header, text="SYSTEM TERMINAL FEED", font=("Consolas", 10, "bold"),
                 fg=self.theme["accent"], bg=self.theme["bg_card"]).pack(side=tk.LEFT, padx=8, pady=4)

        # Terminal scroll text
        self.term_text = tk.Text(
            center_col,
            bg=self.theme["bg_primary"],
            fg=self.theme["text_primary"],
            font=("Consolas", 10),
            wrap=tk.WORD,
            bd=0,
            padx=10,
            pady=10
        )
        self.term_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Command input bar at bottom of center
        input_bar = tk.Frame(center_col, bg=self.theme["bg_card"])
        input_bar.pack(fill=tk.X, padx=4, pady=(0, 4))

        self.cmd_entry = tk.Entry(
            input_bar,
            font=("Consolas", 11),
            bg=self.theme["bg_primary"],
            fg=self.theme["text_primary"],
            insertbackground=self.theme["accent"],
            bd=0
        )
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)
        self.cmd_entry.bind("<Return>", self._on_manual_command)

        btn_send = tk.Button(
            input_bar,
            text="EXECUTE",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["accent"],
            fg="#000000",
            relief=tk.FLAT,
            command=self._on_manual_command
        )
        btn_send.pack(side=tk.RIGHT, padx=8, pady=6)

        # RIGHT: Telemetry Gauges & Quick Actions
        right_col = tk.Frame(content_frame, bg=self.theme["bg_secondary"], width=230)
        right_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        right_col.pack_propagate(False)

        telemetry_title = tk.Label(
            right_col,
            text="HARDWARE TELEMETRY",
            font=("Consolas", 10, "bold"),
            fg=self.theme["accent"],
            bg=self.theme["bg_secondary"]
        )
        telemetry_title.pack(pady=10)

        # CPU Meter
        self.lbl_cpu = tk.Label(right_col, text="CPU: 0%", font=("Segoe UI", 9, "bold"),
                                fg=self.theme["text_primary"], bg=self.theme["bg_secondary"])
        self.lbl_cpu.pack(anchor="w", padx=16, pady=(6, 2))
        self.prog_cpu = ttk.Progressbar(right_col, length=195, mode="determinate")
        self.prog_cpu.pack(padx=16, pady=(0, 8))

        # RAM Meter
        self.lbl_ram = tk.Label(right_col, text="RAM: 0%", font=("Segoe UI", 9, "bold"),
                                fg=self.theme["text_primary"], bg=self.theme["bg_secondary"])
        self.lbl_ram.pack(anchor="w", padx=16, pady=(6, 2))
        self.prog_ram = ttk.Progressbar(right_col, length=195, mode="determinate")
        self.prog_ram.pack(padx=16, pady=(0, 8))

        # Battery Meter
        self.lbl_battery = tk.Label(right_col, text="BATTERY: 100%", font=("Segoe UI", 9, "bold"),
                                    fg=self.theme["text_primary"], bg=self.theme["bg_secondary"])
        self.lbl_battery.pack(anchor="w", padx=16, pady=(6, 2))
        self.prog_bat = ttk.Progressbar(right_col, length=195, mode="determinate")
        self.prog_bat.pack(padx=16, pady=(0, 16))

        # Quick action buttons
        actions_title = tk.Label(
            right_col,
            text="QUICK COMMANDS",
            font=("Consolas", 10, "bold"),
            fg=self.theme["accent"],
            bg=self.theme["bg_secondary"]
        )
        actions_title.pack(pady=(12, 6))

        quick_actions = [
            ("📸 Screenshot", "screenshot"),
            ("🧹 Clean Desktop", "organize desktop"),
            ("⛅ Weather", "weather report"),
            ("🎵 Play/Pause Music", "play music"),
            ("⚡ Speed Test", "speed test"),
            ("🛑 Clear Logs", "CLEAR_LOGS"),
        ]

        for label, cmd in quick_actions:
            b = tk.Button(
                right_col,
                text=label,
                font=("Segoe UI", 9),
                bg=self.theme["bg_card"],
                fg=self.theme["text_primary"],
                relief=tk.FLAT,
                command=lambda c=cmd: self._on_quick_action(c)
            )
            b.pack(fill=tk.X, padx=16, pady=2)

    def _subscribe_events(self) -> None:
        self.logger.add_ui_sink(self._enqueue_log)

    def _enqueue_log(self, timestamp: str, message: str, color_hex: str) -> None:
        self._log_queue.put((timestamp, message, color_hex))

    def _start_gui_loops(self) -> None:
        # Check logs queue
        self._drain_logs()
        # Telemetry refresh timer
        self._refresh_telemetry()

    def _drain_logs(self) -> None:
        while not self._log_queue.empty():
            try:
                ts, msg, col = self._log_queue.get_nowait()
                tag_name = f"col_{col.replace('#', '')}"
                self.term_text.tag_configure(tag_name, foreground=col)
                self.term_text.insert(tk.END, f"[{ts}] {msg}\n", tag_name)
                self.term_text.see(tk.END)
            except queue.Empty:
                break
        self.after(50, self._drain_logs)

    def _refresh_telemetry(self) -> None:
        snap = self.state.get_telemetry_snapshot()

        # Update mode badge
        mode = snap.get("mode", "STANDBY")
        self.lbl_mode_badge.config(text=f"[ {mode} ]")

        # Update HUD canvas
        rms = snap.get("rms_energy", 0.0)
        self.hud_canvas.update_telemetry(rms, AssistantMode(mode))
        self.lbl_audio_rms.config(text=f"MIC ENERGY: {rms:.1f} RMS")

        # Voice auth status
        auth_on = snap.get("voice_auth_enabled", False)
        auth_col = self.theme["success"] if auth_on else self.theme["text_dim"]
        self.lbl_voice_auth.config(
            text=f"VOICE LOCK: {'ACTIVE 🔐' if auth_on else 'OFF'}",
            fg=auth_col
        )

        # Hardware meters
        cpu = snap.get("cpu_percent", 0)
        ram = snap.get("ram_percent", 0)
        bat = snap.get("battery_percent", 100) or 100

        self.lbl_cpu.config(text=f"CPU: {cpu}%")
        self.prog_cpu['value'] = cpu
        self.lbl_ram.config(text=f"RAM: {ram}%")
        self.prog_ram['value'] = ram
        self.lbl_battery.config(text=f"BATTERY: {bat}%")
        self.prog_bat['value'] = bat

        self.after(500, self._refresh_telemetry)

    def _on_manual_command(self, event=None) -> None:
        text = self.cmd_entry.get().strip()
        if not text:
            return
        self.cmd_entry.delete(0, tk.END)
        self.logger.info(f"Manual input: '{text}'", "USER", "#00ffcc")
        if self.command_handler:
            threading.Thread(target=self.command_handler, args=(text,), daemon=True).start()

    def _on_quick_action(self, cmd: str) -> None:
        if cmd == "CLEAR_LOGS":
            self.term_text.delete("1.0", tk.END)
            return
        if self.command_handler:
            threading.Thread(target=self.command_handler, args=(cmd,), daemon=True).start()

    def _on_theme_changed(self, event=None) -> None:
        selected = self.theme_var.get()
        self.config.set("system", "active_theme", selected)
        self.theme = self.config.get_theme(selected)
        # Apply theme colors
        self.configure(bg=self.theme["bg_primary"])
        self.hud_canvas.set_theme_colors(
            ring_color=self.theme["canvas_ring"],
            core_color=self.theme["canvas_core"],
            bg_color=self.theme["bg_secondary"]
        )

    def _open_api_key_dialog(self) -> None:
        key = simpledialog.askstring("Gemini API Key", "Enter your Google Gemini API Key:", parent=self)
        if key:
            self.vault.set_secret("GEMINI_API_KEY", key.strip())
            messagebox.showinfo("Success", "Gemini API key saved into secure vault!", parent=self)

    def _open_enrollment_dialog(self) -> None:
        if self.command_handler:
            self.command_handler("enroll my voice")
