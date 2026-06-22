# =============================================================
#  A R I A  —  Premium AI Voice Assistant
#  Cinematic Dark UI · Glowing Circle · Smooth Animations
# =============================================================

import threading
import queue
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import subprocess
import time
import math
import random
import tkinter as tk

# ─────────────────────────────────────────────────────────────
#  VOICE ENGINE
# ─────────────────────────────────────────────────────────────
engine = pyttsx3.init()
voices = engine.getProperty("voices")
if len(voices) > 1:
    engine.setProperty("voice", voices[1].id)   # female voice
engine.setProperty("rate", 162)
engine.setProperty("volume", 1.0)

# ─────────────────────────────────────────────────────────────
#  GLOBAL STATE  (thread-safe via queue)
# ─────────────────────────────────────────────────────────────
STATES = {
    "idle":      {"glow": "#5555ff", "label": "Click  ◉  to Start",  "pulse": False},
    "listening": {"glow": "#00e5ff", "label": "Listening…",           "pulse": True },
    "thinking":  {"glow": "#cc44ff", "label": "Thinking…",            "pulse": True },
    "speaking":  {"glow": "#00ffaa", "label": "Speaking…",            "pulse": True },
}

_state       = "idle"
_running     = False
_log_lines   = []          # list of (text, color)
_ui_queue    = queue.Queue()   # commands from threads → UI

def _post(cmd, *args):
    """Thread-safe message to UI."""
    _ui_queue.put((cmd, args))

def set_state(s):
    global _state
    _state = s
    _post("state", s)

def add_log(msg, color="#aaaacc"):
    _log_lines.append((msg, color))
    if len(_log_lines) > 80:
        _log_lines.pop(0)
    _post("log")

# ─────────────────────────────────────────────────────────────
#  SPEAK / LISTEN
# ─────────────────────────────────────────────────────────────
def speak(text):
    set_state("speaking")
    add_log(f"🔊  {text}", "#00ffaa")
    engine.say(text)
    engine.runAndWait()
    set_state("idle")

def listen():
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    set_state("listening")
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.4)
            audio = r.listen(source, timeout=7, phrase_time_limit=9)
    except sr.WaitTimeoutError:
        set_state("idle")
        return ""
    except Exception:
        set_state("idle")
        return ""

    set_state("thinking")
    try:
        command = r.recognize_google(audio, language="en-in")
        add_log(f"🎙  You: {command}", "#00e5ff")
        return command.lower()
    except sr.UnknownValueError:
        add_log("❌  Samajh nahi aaya", "#ff4466")
        speak("Clear nahi aaya, dobara bolo.")
        return ""
    except Exception as e:
        add_log(f"❌  Error: {e}", "#ff4466")
        return ""

# ─────────────────────────────────────────────────────────────
#  COMMANDS
# ─────────────────────────────────────────────────────────────
def _close_browsers():
    speak("Saare browsers band kar raha hoon.")
    for exe in ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"]:
        os.system(f"taskkill /f /im {exe} >nul 2>&1")
    speak("Saare browsers band ho gaye.")

def _tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"Ab time hai {now}")

def _tell_date():
    today = datetime.datetime.now().strftime("%d %B %Y")
    speak(f"Aaj ki date hai {today}")

def _screenshot():
    try:
        import pyautogui
        pyautogui.screenshot().save("screenshot.png")
        speak("Screenshot save ho gaya.")
    except Exception:
        speak("Screenshot nahi le saka.")

def _search(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")

def process_command(command):
    if not command:
        return None

    c = command.strip()

    if   "time"       in c: _tell_time()
    elif "date"       in c: _tell_date()
    elif "hello" in c or "hi" in c:
        speak("Hello Chetan! Kya kar sakta hoon aapke liye?")
    elif "who are you" in c or "kaun ho" in c:
        speak("Main ARIA hoon — Aapka personal AI Voice Assistant.")

    elif "notepad"          in c: speak("Notepad open."); os.system("notepad")
    elif "word"             in c: speak("Word open."); os.system("start winword")
    elif "excel"            in c: speak("Excel open."); os.system("start excel")
    elif "powerpoint" in c or "ppt" in c: speak("PowerPoint open."); os.system("start powerpnt")
    elif "calculator"       in c: speak("Calculator open."); os.system("calc")
    elif "file explorer"    in c or "explorer" in c: speak("File Explorer open."); os.system("explorer")

    elif "youtube"          in c: speak("YouTube open kar raha hoon."); webbrowser.open("https://youtube.com")
    elif "google"           in c and "search" not in c: speak("Google open."); webbrowser.open("https://google.com")
    elif "github"           in c: speak("GitHub open."); webbrowser.open("https://github.com")
    elif "stackoverflow"    in c: speak("Stack Overflow open."); webbrowser.open("https://stackoverflow.com")
    elif "chrome"           in c: speak("Chrome open."); os.system("start chrome")

    elif "vscode" in c or "vs code" in c or "code editor" in c:
        speak("VS Code open."); os.system("code")
    elif "cmd" in c or "command prompt" in c:
        speak("Command Prompt open."); os.system("start cmd")

    elif "search"           in c:
        speak("Kya search karna hai?")
        q = listen()
        if q:
            _search(q)
            speak(f"Searching: {q}")

    elif "screenshot"       in c: _screenshot()
    elif "wifi"             in c: subprocess.run("start cmd /k netsh wlan show profile key=clear", shell=True)
    elif "close" in c and ("browser" in c or "tab" in c): _close_browsers()

    elif "shutdown"         in c: speak("System shutdown ho raha hai."); os.system("shutdown /s /t 10")
    elif "restart"          in c: speak("System restart ho raha hai.");  os.system("shutdown /r /t 10")

    elif "exit" in c or "quit" in c or "band" in c or "stop" in c:
        speak("Goodbye Chetan! Phir milenge.")
        return "EXIT"

    else:
        speak("Ye command samajh nahi aayi. Kuch aur try karo.")

    return None

# ─────────────────────────────────────────────────────────────
#  ASSISTANT LOOP  (background thread)
# ─────────────────────────────────────────────────────────────
def _assistant_loop():
    global _running
    speak("Hello Chetan! Main ARIA hoon, aapka AI voice assistant. Hukum karo.")
    while _running:
        cmd = listen()
        if not _running:
            break
        result = process_command(cmd)
        if result == "EXIT":
            _running = False
            _post("stopped")
            break

# ─────────────────────────────────────────────────────────────
#  PREMIUM  UI
# ─────────────────────────────────────────────────────────────
class ARIAApp:
    W, H = 520, 740
    CX, CY, R = 160, 160, 108   # canvas center & base radius

    def __init__(self, root: tk.Tk):
        self.root = root
        self._setup_window()
        self._anim  = {"angle": 0.0, "pulse": 0.0, "pulse_dir": 1,
                       "ring": 0.0, "wave": 0.0}
        self._particles = []
        self._last_state = None
        self._log_rev   = -1
        self._build()
        self._spawn_particles()
        self._tick()
        self._drain_queue()

    # ── WINDOW ──────────────────────────────────────────────
    def _setup_window(self):
        r = self.root
        r.title("ARIA — AI Voice Assistant")
        r.configure(bg="#080814")
        r.resizable(False, False)
        sw, sh = r.winfo_screenwidth(), r.winfo_screenheight()
        r.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")
        r.bind("<space>",   lambda e: self._toggle())
        r.bind("<Escape>",  lambda e: self._stop())
        # make window draggable
        r.bind("<ButtonPress-1>",   self._drag_start)
        r.bind("<B1-Motion>",       self._drag_move)
        self._drag_x = self._drag_y = 0

    def _drag_start(self, e):
        self._drag_x, self._drag_y = e.x_root, e.y_root

    def _drag_move(self, e):
        dx = e.x_root - self._drag_x
        dy = e.y_root - self._drag_y
        x  = self.root.winfo_x() + dx
        y  = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")
        self._drag_x, self._drag_y = e.x_root, e.y_root

    # ── BUILD WIDGETS ───────────────────────────────────────
    def _build(self):
        BG = "#080814"

        # ---- close button (top-right) ----
        close_btn = tk.Label(self.root, text="✕", bg=BG, fg="#444466",
                             font=("Courier New", 12), cursor="hand2")
        close_btn.place(x=self.W-32, y=12)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())
        close_btn.bind("<Enter>",    lambda e: close_btn.config(fg="#ff4466"))
        close_btn.bind("<Leave>",    lambda e: close_btn.config(fg="#444466"))

        # ---- title ----
        tk.Label(self.root, text="A  R  I  A", bg=BG, fg="#ffffff",
                 font=("Courier New", 24, "bold")).pack(pady=(22, 0))
        tk.Label(self.root, text="AI  VOICE  ASSISTANT", bg=BG, fg="#33335a",
                 font=("Courier New", 8)).pack()

        # ---- canvas ----
        self.canvas = tk.Canvas(self.root, width=320, height=320,
                                bg=BG, highlightthickness=0)
        self.canvas.pack(pady=(10, 0))
        self.canvas.bind("<Button-1>", lambda e: self._toggle())

        # ---- status label ----
        self.sv = tk.StringVar(value="Click  ◉  to Start")
        self.sl = tk.Label(self.root, textvariable=self.sv,
                           bg=BG, fg="#5555ff",
                           font=("Courier New", 12, "bold"))
        self.sl.pack(pady=(4, 0))

        # ---- start/stop button ----
        self.bv = tk.StringVar(value="▶  START")
        btn = tk.Button(self.root, textvariable=self.bv,
                        command=self._toggle,
                        bg="#11112a", fg="#5555ff",
                        activebackground="#0a0a20", activeforeground="#7777ff",
                        font=("Courier New", 11, "bold"),
                        relief="flat", bd=0, cursor="hand2",
                        padx=30, pady=10)
        btn.pack(pady=(8, 4))
        self._btn = btn

        # Shortcut hint
        tk.Label(self.root, text="[Space] toggle  ·  [Esc] stop",
                 bg=BG, fg="#222240", font=("Courier New", 7)).pack()

        # ---- log frame ----
        lf = tk.Frame(self.root, bg="#0b0b1e", bd=0)
        lf.pack(fill="both", expand=True, padx=16, pady=(6, 16))

        tk.Label(lf, text=" ◈  CONVERSATION LOG",
                 bg="#0b0b1e", fg="#33335a",
                 font=("Courier New", 7), anchor="w").pack(fill="x", padx=6, pady=(5, 0))

        self.log = tk.Text(lf, bg="#0b0b1e", fg="#8888aa",
                           font=("Courier New", 9),
                           relief="flat", bd=0, state="disabled",
                           wrap="word", selectbackground="#1a1a40",
                           cursor="arrow")
        self.log.pack(fill="both", expand=True, padx=6, pady=(2, 6))
        self.log.tag_configure("green",  foreground="#00ffaa")
        self.log.tag_configure("cyan",   foreground="#00e5ff")
        self.log.tag_configure("red",    foreground="#ff4466")
        self.log.tag_configure("purple", foreground="#cc44ff")
        self.log.tag_configure("dim",    foreground="#8888aa")

    # ── PARTICLES ───────────────────────────────────────────
    def _spawn_particles(self):
        for _ in range(28):
            self._particles.append({
                "angle": random.uniform(0, 360),
                "orbit": random.uniform(self.R + 25, self.R + 65),
                "speed": random.uniform(0.3, 1.1) * random.choice([-1, 1]),
                "size":  random.uniform(1, 3),
                "alpha": random.uniform(0.2, 0.8),
            })

    # ── TOGGLE ──────────────────────────────────────────────
    def _toggle(self):
        global _running
        if not _running:
            _running = True
            self.bv.set("■  STOP")
            self._btn.config(fg="#ff4466", activeforeground="#ff6688")
            threading.Thread(target=_assistant_loop, daemon=True).start()
        else:
            self._stop()

    def _stop(self):
        global _running
        _running = False
        set_state("idle")
        self.bv.set("▶  START")
        self._btn.config(fg="#5555ff", activeforeground="#7777ff")

    # ── QUEUE DRAIN ─────────────────────────────────────────
    def _drain_queue(self):
        try:
            while True:
                cmd, args = _ui_queue.get_nowait()
                if cmd == "state":
                    pass   # drawn live in _tick
                elif cmd == "log":
                    self._refresh_log()
                elif cmd == "stopped":
                    self.bv.set("▶  START")
                    self._btn.config(fg="#5555ff", activeforeground="#7777ff")
        except queue.Empty:
            pass
        self.root.after(40, self._drain_queue)

    # ── LOG ─────────────────────────────────────────────────
    def _refresh_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        for msg, color in _log_lines[-22:]:
            tag = ("green"  if "🔊" in msg else
                   "cyan"   if "🎙" in msg else
                   "red"    if "❌" in msg else
                   "purple" if "🧠" in msg else "dim")
            self.log.insert("end", msg + "\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    # ── ANIMATION ───────────────────────────────────────────
    def _tick(self):
        a   = self._anim
        st  = _state
        si  = STATES.get(st, STATES["idle"])
        g   = si["glow"]
        pul = si["pulse"]

        # Update anim values
        a["angle"]  = (a["angle"] + 1.4) % 360
        a["ring"]   = (a["ring"]  + 2.5) % 360
        a["wave"]   = (a["wave"]  + 0.12) % (2 * math.pi)

        if pul:
            a["pulse"] += 1.6 * a["pulse_dir"]
            if a["pulse"] >= 22:  a["pulse_dir"] = -1
            if a["pulse"] <= 0:   a["pulse_dir"] =  1
        else:
            a["pulse"] = max(0, a["pulse"] - 2)

        # Update particles
        for p in self._particles:
            p["angle"] = (p["angle"] + p["speed"]) % 360

        self._draw(g, pul, a, st)

        # Update label color to match glow
        if st != self._last_state:
            self.sv.set(si["label"])
            self.sl.config(fg=g)
            self._last_state = st

        self.root.after(28, self._tick)

    def _draw(self, glow, pul, a, state):
        c   = self.canvas
        cx, cy, R = self.CX, self.CY, self.R
        c.delete("all")

        # ── background subtle gradient rings ──
        for i in range(6, 0, -1):
            rr = R + 30 + i * 8
            opacity = int(18 * (i / 6))
            col = self._blend("#080814", glow, opacity / 255)
            c.create_oval(cx-rr, cy-rr, cx+rr, cy+rr, outline=col, width=1)

        # ── pulse glow halo ──
        pr = a["pulse"]
        for layer in range(4, 0, -1):
            hr  = R + 10 + pr * 0.55 + layer * 6
            alp = int(60 * (layer / 4))
            col = self._blend("#080814", glow, alp / 255)
            c.create_oval(cx-hr, cy-hr, cx+hr, cy+hr, outline=col, width=3-layer//2)

        # ── particles (orbiting dots) ──
        for p in self._particles:
            if pul or p["orbit"] < R + 40:
                ar = math.radians(p["angle"] + a["angle"] * 0.5)
                px = cx + p["orbit"] * math.cos(ar)
                py = cy + p["orbit"] * math.sin(ar)
                sz = p["size"]
                col = self._blend("#080814", glow, p["alpha"])
                c.create_oval(px-sz, py-sz, px+sz, py+sz, fill=col, outline="")

        # ── rotating sci-fi arc segments ──
        if pul:
            for seg in range(6):
                start_a = a["ring"] + seg * 60
                c.create_arc(cx-(R+6), cy-(R+6), cx+(R+6), cy+(R+6),
                             start=start_a, extent=22,
                             outline=glow, width=2, style="arc")
            # second counter-rotating
            for seg in range(4):
                start_a = -a["ring"] * 0.7 + seg * 90
                c.create_arc(cx-(R+14), cy-(R+14), cx+(R+14), cy+(R+14),
                             start=start_a, extent=14,
                             outline=self._blend("#080814", glow, 0.5), width=1, style="arc")

        # ── main circle border (layered glow) ──
        for w, al in [(12, 0.08), (7, 0.18), (4, 0.45), (2, 0.85), (1, 1.0)]:
            col = self._blend("#080814", glow, al)
            r2  = R + w // 2
            c.create_oval(cx-r2, cy-r2, cx+r2, cy+r2, outline=col, width=w)

        # ── inner dark fill ──
        ir = R - 14
        c.create_oval(cx-ir, cy-ir, cx+ir, cy+ir, fill="#080814", outline=glow, width=1)

        # ── waveform (speaking) or idle cross-hairs ──
        if state == "speaking":
            bars = 14
            bw   = 4
            total_w = bars * (bw + 4)
            sx   = cx - total_w // 2
            for i in range(bars):
                h = int(8 + 26 * abs(math.sin(a["wave"] * 2.5 + i * 0.55 + a["angle"] * 0.05)))
                bx = sx + i * (bw + 4)
                c.create_rectangle(bx, cy - h, bx + bw, cy + h,
                                   fill=glow, outline="")
        elif state == "listening":
            # ripple rings inside circle
            for ri in range(1, 5):
                phase = (a["wave"] + ri * 0.4) % (2 * math.pi)
                rr2   = (ir - 10) * (0.3 + 0.15 * ri) + 6 * math.sin(phase)
                al2   = 0.6 - ri * 0.12
                col2  = self._blend("#080814", glow, al2)
                c.create_oval(cx-rr2, cy-rr2, cx+rr2, cy+rr2, outline=col2, width=1)
        elif state == "thinking":
            # spinning dashed ring inside
            for d in range(12):
                ang = math.radians(a["angle"] * 2 + d * 30)
                dx  = cx + (ir - 20) * math.cos(ang)
                dy  = cy + (ir - 20) * math.sin(ang)
                sz  = 3 if d % 3 == 0 else 2
                c.create_oval(dx-sz, dy-sz, dx+sz, dy+sz, fill=glow, outline="")
        else:
            # idle: subtle cross
            for ang_off in [0, 90]:
                ar = math.radians(ang_off + a["angle"] * 0.2)
                llen = ir - 30
                c.create_line(cx - llen*math.cos(ar), cy - llen*math.sin(ar),
                              cx + llen*math.cos(ar), cy + llen*math.sin(ar),
                              fill=self._blend("#080814", glow, 0.3), width=1)

        # ── center icon ──
        icon = {"idle": "⊙", "listening": "◉", "thinking": "⊗", "speaking": "♪"}.get(state, "⊙")
        c.create_text(cx, cy, text=icon, fill=glow,
                      font=("Segoe UI Symbol", 32))

        # ── outer tick marks ──
        for i in range(48):
            ar     = math.radians(i * 7.5 + a["angle"] * 0.25)
            r_in   = R + 18
            r_out  = R + 26 if i % 4 == 0 else (R + 22 if i % 2 == 0 else R + 20)
            x1 = cx + r_in  * math.cos(ar)
            y1 = cy + r_in  * math.sin(ar)
            x2 = cx + r_out * math.cos(ar)
            y2 = cy + r_out * math.sin(ar)
            tick_col = glow if i % 4 == 0 else self._blend("#080814", glow, 0.25)
            c.create_line(x1, y1, x2, y2, fill=tick_col, width=1)

    # ── COLOR BLEND ─────────────────────────────────────────
    @staticmethod
    def _blend(base_hex, glow_hex, alpha):
        """Blend glow_hex into base_hex by alpha (0-1)."""
        def parse(h):
            h = h.lstrip("#")
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        br, bg, bb = parse(base_hex)
        gr, gg, gb = parse(glow_hex)
        r = int(br + (gr - br) * alpha)
        g = int(bg + (gg - bg) * alpha)
        b = int(bb + (gb - bb) * alpha)
        return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = ARIAApp(root)
    root.mainloop()
