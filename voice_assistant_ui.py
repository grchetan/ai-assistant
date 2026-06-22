# =============================================================
#  A R I A  —  Premium AI Voice Assistant
#  Cinematic Dark UI · Glowing Circle · Neural Voice
# =============================================================

import threading
import queue
import asyncio
import tempfile
import speech_recognition as sr
import edge_tts
import pygame
import datetime
import webbrowser
import os
import subprocess
import time
import math
import random
import tkinter as tk

# ─────────────────────────────────────────────────────────────
#  NEURAL VOICE ENGINE  (Microsoft Edge TTS)
# ─────────────────────────────────────────────────────────────
# Voices to choose from (all sound very human/natural):
#   en-IN-NeerjaNeural   → Indian English female (warm & clear)
#   en-IN-PrabhatNeural  → Indian English male
#   en-US-AriaNeural     → US English female (professional)
#   en-US-JennyNeural    → US English female (friendly)
VOICE      = "en-IN-NeerjaNeural"
VOICE_RATE = "+8%"      # slightly faster than default
VOICE_VOL  = "+10%"

# Init pygame mixer once
pygame.mixer.pre_init(frequency=48000, size=-16, channels=1, buffer=512)
pygame.mixer.init()

_tmp_audio = None   # holds last temp file path

async def _edge_tts_generate(text: str) -> str:
    """Generate speech MP3 via Edge-TTS neural voice. Returns temp filepath."""
    communicate = edge_tts.Communicate(text, VOICE, rate=VOICE_RATE, volume=VOICE_VOL)
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    await communicate.save(tmp.name)
    return tmp.name

def _play_and_delete(fpath: str):
    """Play an MP3 file via pygame and then delete it."""
    global _tmp_audio
    try:
        pygame.mixer.music.load(fpath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.04)
        pygame.mixer.music.unload()
    except Exception as e:
        add_log(f"❌  Playback error: {e}", "#ff4466")
    finally:
        try:
            os.unlink(fpath)
        except Exception:
            pass

# ─────────────────────────────────────────────────────────────
#  GLOBAL STATE  (thread-safe via queue)
# ─────────────────────────────────────────────────────────────
STATES = {
    "idle":      {"glow": "#5555ff", "label": "Click  ◉  to Start",  "pulse": False},
    "listening": {"glow": "#00e5ff", "label": "Listening…",           "pulse": True },
    "thinking":  {"glow": "#cc44ff", "label": "Thinking…",            "pulse": True },
    "speaking":  {"glow": "#00ffaa", "label": "Speaking…",            "pulse": True },
}

_state            = "idle"
_running          = False
_log_lines        = []          # list of (text, color)
_ui_queue         = queue.Queue()
_fail_count       = 0           # consecutive recognition failures
_recognizer       = sr.Recognizer()   # shared, pre-calibrated

def _post(cmd, *args):
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
    try:
        # Generate neural audio then play — completely smooth
        fpath = asyncio.run(_edge_tts_generate(text))
        _play_and_delete(fpath)
    except Exception as e:
        add_log(f"❌  TTS error: {e}", "#ff4466")
        # Fallback: silent (don't crash)
    set_state("idle")

def _calibrate_mic():
    """One-time mic calibration at startup for clean noise floor."""
    try:
        with sr.Microphone() as source:
            _recognizer.adjust_for_ambient_noise(source, duration=1.2)
        _recognizer.pause_threshold          = 0.9
        _recognizer.non_speaking_duration    = 0.6
        _recognizer.dynamic_energy_threshold = True
        _recognizer.dynamic_energy_ratio     = 1.8
    except Exception:
        pass

def listen():
    """Listen once. Returns text or empty string. NEVER speaks on silence."""
    global _fail_count
    set_state("listening")
    try:
        with sr.Microphone() as source:
            # Quick noise adjust each time (cheap)
            _recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = _recognizer.listen(source, timeout=8, phrase_time_limit=10)
    except sr.WaitTimeoutError:
        # Nobody spoke — silent retry, no error message
        set_state("idle")
        return ""
    except Exception:
        set_state("idle")
        return ""

    set_state("thinking")
    try:
        command = _recognizer.recognize_google(audio, language="en-in")
        _fail_count = 0
        add_log(f"🎙  You said: {command}", "#00e5ff")
        return command.lower()
    except sr.UnknownValueError:
        # Got audio but couldn't understand — only speak after 3 fails in a row
        _fail_count += 1
        if _fail_count >= 3:
            add_log("〰  Thoda aur clearly bolo", "#ff8844")
            speak("Thoda clearly bolo please.")
            _fail_count = 0
        else:
            add_log("〰  (unclear audio, retrying)", "#555577")
        set_state("idle")
        return ""
    except sr.RequestError:
        add_log("❌  Internet connection error", "#ff4466")
        _fail_count = 0
        set_state("idle")
        return ""

# ─────────────────────────────────────────────────────────────
#  SMART COMMANDS  —  30+ supported
# ─────────────────────────────────────────────────────────────
import re, requests, random as _rnd

JOKES = [
    "Main ek AI hoon. Mujhe ek baar kisi ne kaha — kya tum sochte ho? Maine kaha — haan, lekin sirf logically!",
    "Ek programmer roya kyunki uski wife ne kaha — jao bahar kuch karo. Toh woh bahar gaya aur ek bug fix kiya.",
    "Meri memory itni achhi hai ki main apni galtiyan bhi yaad rakhta hoon. Aur aapki bhi!",
    "Ek AI doctor ke paas gaya. Doctor ne kaha — tumhe aaram chahiye. AI ne kaha — error: sleep() not found.",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
]

QUOTES = [
    "Sapne woh nahi jo hum soते waqt dekhte hain. Sapne woh hain jo hume sone nahi dete. — A.P.J. Abdul Kalam",
    "Koshish karne walon ki kabhi haar nahi hoti.",
    "Har mushkil mein ek mauka chhupa hota hai.",
    "Safalta tab milti hai jab aap khud par bharosa karte hain.",
    "Kal ki chinta chhodkar aaj ka kaam karo.",
]

def _close_browsers():
    speak("Saare browsers band kar raha hoon.")
    for exe in ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"]:
        os.system(f"taskkill /f /im {exe} >nul 2>&1")
    speak("Ho gaya. Saare browsers band.")

def _tell_time():
    now = datetime.datetime.now()
    speak(f"Abhi time hai {now.strftime('%I:%M %p')}")

def _tell_date():
    now = datetime.datetime.now()
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day  = days[now.weekday()]
    speak(f"Aaj {day} hai, {now.strftime('%d %B %Y')}")

def _screenshot():
    try:
        import pyautogui
        fname = f"screenshot_{datetime.datetime.now().strftime('%H%M%S')}.png"
        pyautogui.screenshot().save(fname)
        speak(f"Screenshot {fname} mein save ho gaya.")
    except Exception:
        speak("Screenshot nahi le saka.")

def _system_info():
    try:
        import psutil
        cpu  = psutil.cpu_percent(interval=1)
        ram  = psutil.virtual_memory()
        used = ram.percent
        speak(f"CPU usage {cpu} percent hai. RAM {used} percent use ho rahi hai.")
    except ImportError:
        speak("psutil install nahi hai. System info nahi de sakta.")

def _battery_status():
    try:
        import psutil
        bat = psutil.sensors_battery()
        if bat:
            pct = int(bat.percent)
            charging = "charge ho rahi hai" if bat.power_plugged else "charging nahi hai"
            speak(f"Battery {pct} percent hai aur {charging}.")
        else:
            speak("Battery info nahi mili. Shayad desktop PC hai.")
    except ImportError:
        speak("psutil install nahi hai.")

def _wiki_search(query):
    """Quick Wikipedia summary."""
    set_state("thinking")
    add_log(f"🧠  Wikipedia search: {query}", "#cc44ff")
    try:
        # Use Wikipedia REST API — no library needed
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        r   = requests.get(url, timeout=6)
        if r.status_code == 200:
            data    = r.json()
            extract = data.get("extract", "")
            if extract:
                # Speak only first 2 sentences to keep it concise
                sentences = re.split(r'(?<=[.!?])\s+', extract)
                answer    = " ".join(sentences[:2])
                speak(answer)
                return
        speak("Wikipedia par koi achhi information nahi mili.")
    except Exception:
        speak("Internet se information nahi le saka.")

def _evaluate_math(expr):
    """Safely evaluate a math expression."""
    try:
        # Keep only safe math chars
        clean = re.sub(r'[^0-9+\-*/().%^ ]', '', expr)
        clean = clean.replace('^', '**')
        if not clean.strip():
            return None
        result = eval(clean, {"__builtins__": {}})
        return result
    except Exception:
        return None

def _volume_control(action):
    if action == "up":
        for _ in range(5):
            subprocess.run(["powershell",
                "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"],
                capture_output=True)
        speak("Volume badha diya.")
    elif action == "down":
        for _ in range(5):
            subprocess.run(["powershell",
                "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"],
                capture_output=True)
        speak("Volume ghata diya.")
    elif action == "mute":
        subprocess.run(["powershell",
            "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"],
            capture_output=True)
        speak("Mute kar diya.")

def _open_website(url):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)

def _greet_by_time():
    h = datetime.datetime.now().hour
    if 5 <= h < 12:
        speak("Good morning Chetan! Aaj ka din achha jayega.")
    elif 12 <= h < 17:
        speak("Good afternoon Chetan! Kaam kaisa chal raha hai?")
    elif 17 <= h < 21:
        speak("Good evening Chetan! Thoda aaram karo.")
    else:
        speak("Raat ke time bhi kaam? Neend bhi zaroori hai Chetan!")

def process_command(command: str):
    if not command:
        return None
    c = command.strip().lower()
    add_log(f"⚙  Processing: {c}", "#444466")

    # ── GREETINGS ──────────────────────────────────────────
    if any(w in c for w in ["hello", "hi aria", "hey aria", "namaste", "helo"]):
        _greet_by_time()

    elif any(w in c for w in ["how are you", "kaisa hai", "kaise ho", "how r u"]):
        speak("Main bilkul theek hoon Chetan! Aap batao, kya help chahiye?")

    elif "who are you" in c or "kaun ho" in c or "your name" in c or "naam kya" in c:
        speak("Main ARIA hoon — Aapka personal AI voice assistant. Jo bolo woh karta hoon.")

    elif "thank" in c or "shukriya" in c or "dhanyawad" in c:
        speak("Koi baat nahi Chetan. Ye mera kaam hai!")

    # ── TIME / DATE ─────────────────────────────────────────
    elif "time"  in c and "date" not in c: _tell_time()
    elif "date"  in c or "day"  in c:      _tell_date()

    # ── MATH ────────────────────────────────────────────────
    elif any(w in c for w in ["calculate", "what is", "kitna hai", "solve"]) and \
         any(ch in c for ch in list("+-*/")):
        # Extract math expression
        expr = re.sub(r'(calculate|what is|solve|kitna hai)', '', c).strip()
        result = _evaluate_math(expr)
        if result is not None:
            speak(f"{expr} ka answer hai {result}")
        else:
            speak("Ye math samajh nahi aaya.")

    # ── KNOWLEDGE ───────────────────────────────────────────
    elif c.startswith("what is ") or c.startswith("who is ") or \
         c.startswith("tell me about ") or c.startswith("batao ") or \
         "explain" in c or "wikipedia" in c:
        # Extract topic
        for prefix in ["what is ","who is ","tell me about ","batao ","explain ","wikipedia "]:
            if c.startswith(prefix):
                topic = c[len(prefix):].strip()
                break
        else:
            topic = c
        if topic:
            speak(f"{topic} ke baare mein dhundh raha hoon.")
            _wiki_search(topic)
        else:
            speak("Kya jaanna chahte ho?"
)

    # ── OPEN APPS ───────────────────────────────────────────
    elif "notepad"                        in c: speak("Notepad open kar raha hoon."); os.system("notepad")
    elif "word"                           in c: speak("Microsoft Word open kar raha hoon."); os.system("start winword")
    elif "excel"                          in c: speak("Excel open kar raha hoon."); os.system("start excel")
    elif "powerpoint" in c or "ppt"       in c: speak("PowerPoint open kar raha hoon."); os.system("start powerpnt")
    elif "calculator" in c or "calc"      in c: speak("Calculator open kar raha hoon."); os.system("calc")
    elif "paint"                          in c: speak("Paint open kar raha hoon."); os.system("mspaint")
    elif "task manager"                   in c: speak("Task Manager open kar raha hoon."); os.system("taskmgr")
    elif "settings"                       in c: speak("Settings open kar raha hoon."); os.system("start ms-settings:")
    elif "file explorer" in c or ("explorer" in c and "internet" not in c):
        speak("File Explorer open kar raha hoon."); os.system("explorer")
    elif "control panel"                  in c: speak("Control Panel open."); os.system("control")
    elif "snipping tool" in c or "snip"   in c: speak("Snipping tool open."); os.system("snippingtool")

    # ── WEB / BROWSER ───────────────────────────────────────
    elif "youtube"     in c: speak("YouTube khol raha hoon."); webbrowser.open("https://youtube.com")
    elif "google"      in c and "search" not in c: speak("Google khol raha hoon."); webbrowser.open("https://google.com")
    elif "github"      in c: speak("GitHub open kar raha hoon."); webbrowser.open("https://github.com")
    elif "stackoverflow" in c: speak("Stack Overflow open."); webbrowser.open("https://stackoverflow.com")
    elif "instagram"   in c: speak("Instagram open kar raha hoon."); webbrowser.open("https://instagram.com")
    elif "twitter"  in c or "x.com" in c: speak("Twitter open kar raha hoon."); webbrowser.open("https://x.com")
    elif "whatsapp"    in c: speak("WhatsApp Web open kar raha hoon."); webbrowser.open("https://web.whatsapp.com")
    elif "chatgpt"     in c: speak("ChatGPT open kar raha hoon."); webbrowser.open("https://chat.openai.com")
    elif "netflix"     in c: speak("Netflix open kar raha hoon."); webbrowser.open("https://netflix.com")
    elif "chrome"      in c: speak("Chrome open."); os.system("start chrome")
    elif "open website" in c or "open site" in c:
        speak("Kaun si website kholni hai?")
        site = listen()
        if site:
            speak(f"{site} khol raha hoon.")
            _open_website(site.strip())

    # ── DEVELOPER ───────────────────────────────────────────
    elif "vscode" in c or "vs code" in c or "code editor" in c:
        speak("VS Code open."); os.system("code")
    elif "cmd" in c or "command prompt" in c:
        speak("Command Prompt open kar raha hoon."); os.system("start cmd")
    elif "powershell" in c:
        speak("PowerShell open."); os.system("start powershell")
    elif "git" in c and "github" not in c:
        speak("Git bash open kar raha hoon."); os.system("start git-bash")

    # ── SEARCH ──────────────────────────────────────────────
    elif "search" in c or "google karo" in c or "dhundho" in c:
        speak("Kya search karna hai?")
        q = listen()
        if q:
            webbrowser.open(f"https://www.google.com/search?q={q}")
            speak(f"{q} Google par search kar diya.")

    elif "youtube search" in c or "youtube mein" in c or "play" in c:
        speak("YouTube par kya search karna hai?")
        q = listen()
        if q:
            webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
            speak(f"YouTube par {q} search kar diya.")

    # ── SYSTEM ──────────────────────────────────────────────
    elif "screenshot"    in c: _screenshot()
    elif "wifi"          in c or "password" in c:
        subprocess.run("start cmd /k netsh wlan show profile key=clear", shell=True)
        speak("WiFi passwords terminal mein dikh rahe hain.")
    elif "close" in c and ("browser" in c or "tab" in c): _close_browsers()
    elif "lock"          in c: speak("PC lock kar raha hoon."); os.system("rundll32.exe user32.dll,LockWorkStation")
    elif "sleep"         in c and "pc" in c: speak("PC sleep mode mein ja raha hai."); os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif "empty recycle" in c or "recycle bin" in c:
        os.system("powershell -command \"Clear-RecycleBin -Force\"")
        speak("Recycle bin khali kar diya.")
    elif "ip address"    in c or "mera ip" in c:
        try:
            ip = requests.get("https://api.ipify.org", timeout=4).text
            speak(f"Aapka public IP address hai {ip}")
        except Exception:
            speak("IP address nahi le saka.")

    # ── VOLUME ──────────────────────────────────────────────
    elif "volume up"     in c or "awaaz badha" in c: _volume_control("up")
    elif "volume down"   in c or "awaaz ghata" in c: _volume_control("down")
    elif "mute"          in c or "chup"        in c: _volume_control("mute")

    # ── SHUTDOWN / RESTART ──────────────────────────────────
    elif "shutdown"      in c: speak("10 seconds mein system band hoga."); os.system("shutdown /s /t 10")
    elif "restart"       in c: speak("System restart ho raha hai."); os.system("shutdown /r /t 10")
    elif "cancel shutdown" in c: os.system("shutdown /a"); speak("Shutdown cancel kar diya.")

    # ── SYSTEM INFO ─────────────────────────────────────────
    elif "system info"  in c or "cpu"    in c or "ram"     in c: _system_info()
    elif "battery"      in c or "charge" in c:                   _battery_status()

    # ── FUN ─────────────────────────────────────────────────
    elif "joke"         in c or "joke sunao" in c: speak(_rnd.choice(JOKES))
    elif "quote"        in c or "motivat"    in c: speak(_rnd.choice(QUOTES))
    elif "flip coin"    in c or "coin"       in c:
        result = _rnd.choice(["Heads", "Tails"])
        speak(f"Coin toss result hai — {result}!")
    elif "dice" in c or "random number" in c:
        n = _rnd.randint(1, 6)
        speak(f"Dice roll — {n}!")

    # ── EXIT ────────────────────────────────────────────────
    elif any(w in c for w in ["exit", "quit", "band karo", "goodbye", "bye", "alvida"]):
        speak("Goodbye Chetan! Jab bhi zaroorat ho, main hamesha yahan hoon.")
        return "EXIT"

    # ── UNKNOWN — try Wikipedia as last resort ──────────────
    else:
        # Check if it looks like a question
        if any(c.startswith(w) for w in ["kya","kaun","kab","kahan","kyun","kaise","who","what","when","where","why","how"]):
            speak(f"{c} ke baare mein search kar raha hoon.")
            _wiki_search(c)
        else:
            speak(f"Ye command clear nahi tha. Kuch aur try karo.")

    return None

# ─────────────────────────────────────────────────────────────
#  ASSISTANT LOOP  (background thread)
# ─────────────────────────────────────────────────────────────
def _assistant_loop():
    global _running
    # Calibrate mic once at startup
    add_log("⚙  Microphone calibrate ho raha hai…", "#555577")
    _calibrate_mic()
    add_log("✅  Mic calibration done!", "#00ffaa")
    speak("Hello Chetan! Main ARIA hoon. Microphone ready hai. Hukum karo.")
    while _running:
        cmd = listen()
        if not _running:
            break
        if cmd:   # only process if we actually heard something
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
