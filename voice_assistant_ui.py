# =============================================================
#  J A R V I S  —  Elite AI Voice Assistant
#  Cinematic Dark UI · Neural Voice · Tony Stark Edition
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
VOICE      = "en-IN-PrabhatNeural"
VOICE_RATE = "+22%"     # faster = snappier responses
VOICE_VOL  = "+15%"

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
    "idle":      {"glow": "#4466ff", "label": "J A R V I S  —  Standby",   "pulse": False},
    "listening": {"glow": "#00e5ff", "label": "Listening, Sir…",            "pulse": True },
    "thinking":  {"glow": "#aa33ff", "label": "Processing…",                "pulse": True },
    "speaking":  {"glow": "#00ffcc", "label": "JARVIS Speaking…",           "pulse": True },
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
#  AUDIO CACHE  —  pre-generate common phrases at startup
#  so zero network delay on frequent responses
# ─────────────────────────────────────────────────────────────
_audio_cache: dict = {}   # text → raw MP3 bytes

# Phrases to pre-cache at startup
_CACHE_PHRASES = [
    "Done, sir!",
    "Ho gaya, sir!",
    "My pleasure, sir!",
    "Ye toh mera kaam hai, sir!",
    "Always at your service, sir!",
    "Sir, thoda aur clearly bolo? Samajh nahi aaya.",
    "Bilkul top condition mein, sir! All systems operational. Aap batao?",
    "Thoda clearly bolo please.",
    "JARVIS online. Kya hukum hai, sir? Code likhna hai, koi site kholni hai, ya bas baat karni hai — main hazir hoon!",
    "Good morning, sir! Systems online. Aaj kya conquer karna hai?",
    "Good afternoon, sir! Kaam chal raha hai? Koi help chahiye?",
    "Good evening, sir! Din kaisa raha? Kuch aur kaam baaki hai?",
    "Sir, itni raat ko bhi kaam? Main saath hoon, par neend bhi zaroori hai!",
    "Sir, kya search karna hai?",
    "Sir, kaun si website kholni hai?",
    "Locking workstation, sir.",
    "Restarting, sir.",
    "Recycle bin cleared, sir!",
    "Sir, 10 seconds mein system shutdown.",
    "Chrome launch kar raha hoon, sir.",
]

async def _precache_all():
    """Pre-generate MP3 bytes for common phrases into RAM."""
    for phrase in _CACHE_PHRASES:
        try:
            com = edge_tts.Communicate(phrase, VOICE, rate=VOICE_RATE, volume=VOICE_VOL)
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tmp.close()
            await com.save(tmp.name)
            with open(tmp.name, "rb") as f:
                _audio_cache[phrase] = f.read()
            os.unlink(tmp.name)
        except Exception:
            pass   # if one fails, skip it

def _precache_blocking():
    """Run pre-cache in a new event loop (called from thread)."""
    try:
        asyncio.run(_precache_all())
        add_log(f"\u26a1  {len(_audio_cache)} responses cached — instant replies ready!", "#00ffcc")
    except Exception:
        pass

def _play_from_cache(text: str) -> bool:
    """Try to play from cache. Returns True if hit."""
    data = _audio_cache.get(text)
    if data is None:
        return False
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.write(data)
        tmp.close()
        _play_and_delete(tmp.name)
        return True
    except Exception:
        return False

# ─────────────────────────────────────────────────────────────
#  SPEAK / LISTEN
# ─────────────────────────────────────────────────────────────
def speak(text):
    set_state("speaking")
    add_log(f"🔊  {text}", "#00ffcc")
    try:
        if not _play_from_cache(text):          # cache hit → instant
            fpath = asyncio.run(_edge_tts_generate(text))  # cache miss → network
            _play_and_delete(fpath)
    except Exception as e:
        add_log(f"❌  TTS error: {e}", "#ff4466")
    set_state("idle")

# keep mic source open between listens to avoid re-init overhead
_mic_source = None

def _calibrate_mic():
    """One-time mic calibration. Sets energy threshold for the session."""
    try:
        with sr.Microphone() as source:
            _recognizer.adjust_for_ambient_noise(source, duration=1.5)
        _recognizer.pause_threshold          = 0.7   # faster end-of-speech detection
        _recognizer.non_speaking_duration    = 0.5
        _recognizer.dynamic_energy_threshold = True
        _recognizer.dynamic_energy_ratio     = 1.6
    except Exception:
        pass

def listen():
    """Fast listen — NO per-call noise adjustment (calibrated once at startup)."""
    global _fail_count
    set_state("listening")
    try:
        with sr.Microphone() as source:
            # ⚡ NO adjust_for_ambient_noise here — saves 300ms every call!
            audio = _recognizer.listen(source, timeout=7, phrase_time_limit=9)
    except sr.WaitTimeoutError:
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
        _fail_count += 1
        if _fail_count >= 3:
            add_log("〰  Thoda clearly bolo", "#ff8844")
            speak("Thoda clearly bolo please.")
            _fail_count = 0
        else:
            add_log("〰  (unclear, retrying)", "#555577")
        set_state("idle")
        return ""
    except sr.RequestError:
        add_log("❌  Internet error", "#ff4466")
        _fail_count = 0
        set_state("idle")
        return ""

# ─────────────────────────────────────────────────────────────
#  J A R V I S  —  Command Engine  (60+ commands)
# ─────────────────────────────────────────────────────────────
import re, requests, random as _rnd

# ── Witty JARVIS responses ───────────────────────────────────
JOKES = [
    "Sir, ek programmer roya kyunki uski girlfriend ne kaha — jao bahar kuch karo. Toh woh bahar gaya aur GitHub push kar diya.",
    "Why do Java developers wear glasses? Because they don't C-sharp! Ha!",
    "Main AI hoon, sir. Mujhe kisi ne poochha — kya tum feel karte ho? Maine kaha — haan, sirf stack overflow!",
    "Ek bug thi jo 3 din se chal rahi thi. Developer ne finally solve kiya. Bug ka reason? Ek semicolon. Zindagi!",
    "Sir, dark mode isliye use karo kyunki light attracts bugs. Literally!",
    "Recursion samajhni hai? Pehle recursion samajhni hogi. — JARVIS",
]

QUOTES = [
    "Sapne woh nahi jo hum sote waqt dekhte hain — sapne woh hain jo hume sone nahi dete. — Abdul Kalam",
    "Sir, koshish karne walon ki kabhi haar nahi hoti.",
    "The best way to predict the future is to create it. — Peter Drucker",
    "Code is like humor. When you have to explain it, it's bad. — Cory House",
    "Har mushkil mein ek opportunity chhupa hota hai, sir.",
    "Don't watch the clock. Do what it does — keep going.",
]

FRUSTRATED_RESPONSES = [
    "Arre bhai, ye toh hota hai sabke saath! Thoda break lo, chai piyo. Wapas aao — main hoon na help karne ke liye!",
    "Sir, even Iron Man ke suit mein bugs aate the. Thoda aaram karo, fresh mind se sab solve hoga.",
    "Coding frustration? Normal hai, sir. Ek chhoti si problem solve karo — confidence khud aayega.",
]

# ── Utility functions ────────────────────────────────────────
def _open_url(url: str, label: str = ""):
    webbrowser.open(url)
    speak(f"{label or url} khol diya, sir. Done!")

def _open_website(url: str):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)

def _close_browsers():
    speak("Saare browsers terminate kar raha hoon, sir.")
    for exe in ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"]:
        os.system(f"taskkill /f /im {exe} >nul 2>&1")
    speak("Ho gaya, sir! Saare browsers band.")

def _tell_time():
    now = datetime.datetime.now()
    speak(f"Abhi time hai {now.strftime('%I:%M %p')}, sir.")

def _tell_date():
    now  = datetime.datetime.now()
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    speak(f"Aaj {days[now.weekday()]} hai, {now.strftime('%d %B %Y')}, sir.")

def _screenshot():
    try:
        import pyautogui
        fname = f"jarvis_screenshot_{datetime.datetime.now().strftime('%H%M%S')}.png"
        pyautogui.screenshot().save(fname)
        speak(f"Screenshot capture ho gaya, sir. {fname} mein save hai.")
    except Exception:
        speak("Screenshot nahi le saka, sir. PyAutoGUI check karo.")

def _system_info():
    try:
        import psutil
        cpu  = psutil.cpu_percent(interval=1)
        ram  = psutil.virtual_memory()
        speak(f"Sir, CPU {cpu} percent par chal raha hai. RAM {ram.percent} percent use ho rahi hai.")
    except ImportError:
        speak("psutil library nahi mili, sir.")

def _battery_status():
    try:
        import psutil
        bat = psutil.sensors_battery()
        if bat:
            pct      = int(bat.percent)
            charging = "charge ho rahi hai" if bat.power_plugged else "charging nahi hai"
            warn     = " Charger lagao, sir!" if pct < 20 and not bat.power_plugged else ""
            speak(f"Battery {pct} percent hai aur {charging}.{warn}")
        else:
            speak("Battery info nahi mili, sir. Ye desktop PC lag raha hai.")
    except ImportError:
        speak("psutil nahi hai, sir.")

def _wiki_search(query: str):
    set_state("thinking")
    add_log(f"🧠  JARVIS searching: {query}", "#aa33ff")
    try:
        url  = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            data    = resp.json()
            extract = data.get("extract", "")
            if extract:
                sentences = re.split(r'(?<=[.!?])\s+', extract)
                answer    = " ".join(sentences[:2])
                speak(f"Sir, {answer}")
                return
        speak("Sir, Wikipedia par is topic ki information nahi mili.")
    except Exception:
        speak("Sir, internet se data nahi aa raha. Connection check karo.")

def _evaluate_math(expr: str):
    try:
        clean  = re.sub(r'[^0-9+\-*/().%^ ]', '', expr)
        clean  = clean.replace('^', '**')
        if not clean.strip():
            return None
        return eval(clean, {"__builtins__": {}})
    except Exception:
        return None

def _volume_control(action: str, level: int = 5):
    key_map = {"up": 175, "down": 174, "mute": 173}
    if action in key_map:
        steps = level if action in ("up","down") else 1
        for _ in range(steps):
            subprocess.run(
                ["powershell", f"(New-Object -ComObject WScript.Shell).SendKeys([char]{key_map[action]})"],
                capture_output=True)
        msgs = {"up": "Volume badha diya, sir!", "down": "Volume ghata diya, sir!", "mute": "Mute kar diya, sir!"}
        speak(msgs[action])

def _get_weather(city: str = "Delhi"):
    try:
        url  = f"https://wttr.in/{city.replace(' ','+')}?format=3"
        resp = requests.get(url, timeout=5, headers={"User-Agent": "curl/7.68.0"})
        if resp.status_code == 200:
            speak(f"Sir, {resp.text.strip()}")
        else:
            speak(f"Sir, {city} ka mausam nahi le saka. Weather service se response nahi aaya.")
    except Exception:
        speak("Sir, weather fetch karne mein problem aayi. Internet check karo.")

def _start_timer(minutes: int):
    speak(f"Sir, {minutes} minute ka timer set kar diya. Main bataunga jab time khatam ho.")
    def _timer_thread():
        time.sleep(minutes * 60)
        speak(f"Sir! {minutes} minute poore ho gaye. Timer khatam!")
    threading.Thread(target=_timer_thread, daemon=True).start()

def _open_folder(name: str):
    folder_map = {
        "desktop":   os.path.join(os.path.expanduser("~"), "Desktop"),
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "pictures":  os.path.join(os.path.expanduser("~"), "Pictures"),
        "music":     os.path.join(os.path.expanduser("~"), "Music"),
        "videos":    os.path.join(os.path.expanduser("~"), "Videos"),
    }
    path = folder_map.get(name.lower())
    if path and os.path.exists(path):
        os.startfile(path)
        speak(f"{name.capitalize()} folder khol diya, sir!")
    else:
        speak(f"Sir, {name} folder nahi mila.")

def _create_folder(name: str):
    try:
        path = os.path.join(os.path.expanduser("~"), "Desktop", name)
        os.makedirs(path, exist_ok=True)
        speak(f"Sir, Desktop par {name} folder ban gaya. Done!")
    except Exception as e:
        speak(f"Folder nahi bana, sir. Error: {e}")

def _greet_by_time():
    h = datetime.datetime.now().hour
    if 5 <= h < 12:
        speak("Good morning, sir! Systems online. Aaj kya conquer karna hai?")
    elif 12 <= h < 17:
        speak("Good afternoon, sir! Kaam chal raha hai? Koi help chahiye?")
    elif 17 <= h < 21:
        speak("Good evening, sir! Din kaisa raha? Kuch aur kaam baaki hai?")
    else:
        speak("Sir, itni raat ko bhi kaam? Main saath hoon, par neend bhi zaroori hai!")

# ── MAIN COMMAND PROCESSOR ───────────────────────────────────
def process_command(command: str):
    if not command:
        return None
    c = command.strip().lower()
    add_log(f"🤖  JARVIS processing: {c}", "#334466")

    # ━━ GREETINGS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if any(w in c for w in ["hello jarvis", "hey jarvis", "hi jarvis", "namaste", "hello", "hi"]):
        _greet_by_time()

    elif any(w in c for w in ["how are you", "kaisa hai", "kaise ho", "you okay"]):
        speak("Bilkul top condition mein, sir! All systems operational. Aap batao?")

    elif any(w in c for w in ["who are you", "kaun ho", "your name", "naam kya", "introduce"]):
        speak("Sir, main JARVIS hoon — Just A Rather Very Intelligent System. Aapka personal AI assistant. Jo bolo woh karta hoon.")

    elif any(w in c for w in ["thank", "thanks", "shukriya", "dhanyawad", "great job", "well done"]):
        speak(_rnd.choice(["My pleasure, sir!", "Ye toh mera kaam hai, sir!", "Always at your service, sir!"]))

    # ━━ EMOTIONS / MOTIVATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif any(w in c for w in ["frustrated", "bored", "tired", "thak gaya", "pareshan", "coding nahi", "nahi ho rahi"]):
        speak(_rnd.choice(FRUSTRATED_RESPONSES))

    elif any(w in c for w in ["motivate", "motivation", "inspire", "quote", "suvichar"]):
        speak(_rnd.choice(QUOTES))

    # ━━ TIME / DATE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif any(w in c for w in ["time", "baj", "ghanta"]) and "date" not in c and "timer" not in c:
        _tell_time()
    elif any(w in c for w in ["date", "din", "day", "kaun sa din", "aaj kya"]):
        _tell_date()

    # ━━ TIMER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "timer" in c or "remind" in c:
        # Extract number from string
        nums = re.findall(r'\d+', c)
        mins = int(nums[0]) if nums else None
        if mins:
            _start_timer(mins)
        else:
            speak("Sir, kitne minute ka timer lagaun?")
            resp = listen()
            nums2 = re.findall(r'\d+', resp)
            if nums2:
                _start_timer(int(nums2[0]))

    # ━━ WEATHER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "mausam" in c or "weather" in c:
        if "delhi" in c:       _get_weather("Delhi")
        elif "mumbai" in c:    _get_weather("Mumbai")
        elif "bangalore" in c: _get_weather("Bangalore")
        elif "hyderabad" in c: _get_weather("Hyderabad")
        elif "jaipur" in c:    _get_weather("Jaipur")
        else:
            speak("Sir, kis city ka mausam bataaun?")
            city = listen()
            if city:
                _get_weather(city.strip())

    # ━━ MATH ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif any(w in c for w in ["calculate", "kitna hai", "solve", "compute"]) and \
         any(ch in c for ch in list("+-*/")):
        expr   = re.sub(r'(calculate|kitna hai|solve|compute|sir)', '', c).strip()
        result = _evaluate_math(expr)
        if result is not None:
            speak(f"Sir, {expr} ka answer hai {result}. Done!")
        else:
            speak("Sir, ye math expression samajh nahi aaya. Dobara try karo.")

    # ━━ KNOWLEDGE / WIKIPEDIA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif any(c.startswith(p) for p in ["what is ","who is ","tell me about ","batao ","explain ","what are ","kya hai "]):
        for prefix in ["what is ","who is ","tell me about ","batao ","explain ","what are ","kya hai "]:
            if c.startswith(prefix):
                topic = c[len(prefix):].strip()
                break
        else:
            topic = c
        if topic:
            speak(f"Sir, {topic} ke baare mein ek second...")
            _wiki_search(topic)

    # ━━ APPS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "notepad"     in c: speak("Notepad, sir!");          os.system("notepad")
    elif "word"        in c: speak("Microsoft Word, sir!");   os.system("start winword")
    elif "excel"       in c: speak("Excel open, sir!");       os.system("start excel")
    elif "powerpoint" in c or "ppt" in c: speak("PowerPoint, sir!"); os.system("start powerpnt")
    elif "calculator" in c or "calc" in c: speak("Calculator, sir!"); os.system("calc")
    elif "paint"       in c: speak("MS Paint, sir!");         os.system("mspaint")
    elif "task manager" in c: speak("Task Manager, sir!");    os.system("taskmgr")
    elif "settings"    in c: speak("Settings khol raha hoon, sir."); os.system("start ms-settings:")
    elif "control panel" in c: speak("Control Panel, sir!"); os.system("control")
    elif "snip" in c or "snipping" in c: speak("Snipping Tool, sir!"); os.system("snippingtool")
    elif "file explorer" in c or ("explorer" in c and "internet" not in c):
        speak("File Explorer, sir!"); os.system("explorer")

    # ━━ GITHUB ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "github" in c:
        if "trending"  in c: _open_url("https://github.com/trending",      "GitHub Trending")
        elif "new repo" in c or "create repo" in c: _open_url("https://github.com/new", "New Repo page")
        elif "profile"  in c: _open_url("https://github.com",               "GitHub Profile")
        else:                  _open_url("https://github.com",               "GitHub")

    # ━━ LEETCODE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "leetcode" in c:
        if "easy"    in c: _open_url("https://leetcode.com/problemset/?difficulty=EASY",   "LeetCode Easy")
        elif "medium" in c: _open_url("https://leetcode.com/problemset/?difficulty=MEDIUM","LeetCode Medium")
        elif "hard"   in c: _open_url("https://leetcode.com/problemset/?difficulty=HARD",  "LeetCode Hard")
        elif "daily"  in c: _open_url("https://leetcode.com/problemset/",                  "LeetCode Daily")
        elif "two sum" in c: _open_url("https://leetcode.com/problems/two-sum/",           "Two Sum problem")
        else:               _open_url("https://leetcode.com",                              "LeetCode")

    # ━━ DEVELOPER WEBSITES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "stackoverflow" in c: _open_url("https://stackoverflow.com",           "Stack Overflow")
    elif "mdn"           in c: _open_url("https://developer.mozilla.org",        "MDN Docs")
    elif "npm"           in c: _open_url("https://npmjs.com",                    "NPM")
    elif "vercel"        in c: _open_url("https://vercel.com",                   "Vercel")
    elif "netlify"       in c: _open_url("https://netlify.com",                  "Netlify")
    elif "replit"        in c: _open_url("https://replit.com",                   "Replit")
    elif "codepen"       in c: _open_url("https://codepen.io",                   "CodePen")
    elif "w3school"      in c: _open_url("https://w3schools.com",                "W3Schools")
    elif "geeksforgeeks" in c or "gfg" in c: _open_url("https://geeksforgeeks.org", "GeeksForGeeks")
    elif "figma"         in c: _open_url("https://figma.com",                    "Figma")
    elif "notion"        in c: _open_url("https://notion.so",                    "Notion")

    # ━━ LEARNING ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "coursera"  in c: _open_url("https://coursera.org",  "Coursera")
    elif "udemy"     in c: _open_url("https://udemy.com",     "Udemy")
    elif "youtube"   in c:
        if "search" in c or "par" in c:
            speak("Sir, kya search karna hai YouTube par?")
            q = listen()
            if q: _open_url(f"https://www.youtube.com/results?search_query={q.replace(' ','+')}", f"YouTube search: {q}")
        else: _open_url("https://youtube.com", "YouTube")

    # ━━ POPULAR WEBSITES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "chatgpt"    in c: _open_url("https://chat.openai.com",     "ChatGPT")
    elif "claude"     in c: _open_url("https://claude.ai",            "Claude AI")
    elif "google"     in c and not any(w in c for w in ["search","karo","dhundh"]): _open_url("https://google.com", "Google")
    elif "gmail"      in c: _open_url("https://mail.google.com",      "Gmail")
    elif "drive"      in c: _open_url("https://drive.google.com",     "Google Drive")
    elif "instagram"  in c: _open_url("https://instagram.com",        "Instagram")
    elif "twitter"    in c or "x.com" in c: _open_url("https://x.com", "Twitter")
    elif "whatsapp"   in c: _open_url("https://web.whatsapp.com",     "WhatsApp Web")
    elif "linkedin"   in c: _open_url("https://linkedin.com",         "LinkedIn")
    elif "netflix"    in c: _open_url("https://netflix.com",          "Netflix")
    elif "chrome"     in c: speak("Chrome launch kar raha hoon, sir."); os.system("start chrome")
    elif "open website" in c or "website kholo" in c or "site kholo" in c:
        speak("Sir, kaun si website kholni hai?")
        site = listen()
        if site:
            speak(f"{site} khol raha hoon, sir.")
            _open_website(site.strip())

    # ━━ DEVELOPER TOOLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "vscode" in c or "vs code" in c or "code editor" in c:
        speak("VS Code, sir!"); os.system("code")
    elif "terminal" in c or "cmd" in c or "command prompt" in c:
        speak("Terminal launch, sir!"); os.system("start cmd")
    elif "powershell" in c:
        speak("PowerShell, sir!"); os.system("start powershell")
    elif "git bash" in c:
        speak("Git Bash, sir!"); os.system("start git-bash")

    # ━━ GOOGLE SEARCH ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif any(w in c for w in ["search", "google karo", "dhundho", "dhundh"]):
        speak("Sir, kya search karna hai?")
        q = listen()
        if q:
            webbrowser.open(f"https://www.google.com/search?q={q.replace(' ','+')}")
            speak(f"Sir, {q} Google par search kar diya. Done!")

    elif "stack overflow" in c or "stackoverflow" in c:
        speak("Sir, Stack Overflow par kya dhundhna hai?")
        q = listen()
        if q:
            _open_url(f"https://stackoverflow.com/search?q={q.replace(' ','+')}", f"Stack Overflow: {q}")

    # ━━ FOLDERS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "downloads" in c: _open_folder("downloads")
    elif "desktop"   in c and "open" in c: _open_folder("desktop")
    elif "documents" in c: _open_folder("documents")
    elif "pictures"  in c: _open_folder("pictures")
    elif "music folder" in c: _open_folder("music")
    elif "videos folder" in c: _open_folder("videos")
    elif "new folder" in c or "folder banao" in c:
        speak("Sir, folder ka naam kya rakhu?")
        fname = listen()
        if fname:
            _create_folder(fname.strip())

    # ━━ SCREENSHOT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "screenshot" in c or "screen capture" in c:
        _screenshot()

    # ━━ WIFI ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "wifi" in c or ("password" in c and "wifi" in c):
        subprocess.run("start cmd /k netsh wlan show profile key=clear", shell=True)
        speak("Sir, WiFi passwords terminal mein dikh rahe hain.")

    # ━━ SYSTEM CONTROLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "close" in c and ("browser" in c or "tab" in c): _close_browsers()
    elif "lock"  in c: speak("Locking workstation, sir."); os.system("rundll32.exe user32.dll,LockWorkStation")
    elif "sleep" in c and "pc" in c: speak("PC sleep mode, sir."); os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif "recycle" in c or "empty recycle" in c:
        os.system('powershell -command "Clear-RecycleBin -Force"')
        speak("Recycle bin cleared, sir!")
    elif "ip" in c or "my ip" in c or "mera ip" in c:
        try:
            ip = requests.get("https://api.ipify.org", timeout=4).text
            speak(f"Sir, aapka public IP address hai {ip}.")
        except Exception:
            speak("Sir, IP fetch nahi hua. Internet check karo.")

    # ━━ VOLUME ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "volume up" in c or "awaaz badha" in c: _volume_control("up")
    elif "volume down" in c or "awaaz ghata" in c: _volume_control("down")
    elif "mute" in c: _volume_control("mute")

    # ━━ SHUTDOWN / RESTART ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "shutdown" in c: speak("Sir, 10 seconds mein system shutdown."); os.system("shutdown /s /t 10")
    elif "restart"  in c: speak("Restarting, sir.");                      os.system("shutdown /r /t 10")
    elif "cancel shutdown" in c: os.system("shutdown /a"); speak("Shutdown cancelled, sir!")

    # ━━ SYSTEM INFO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif any(w in c for w in ["system info", "cpu", "ram", "performance"]): _system_info()
    elif any(w in c for w in ["battery", "charge", "kitni battery"]):        _battery_status()

    # ━━ FUN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif "joke" in c: speak(_rnd.choice(JOKES))
    elif "coin" in c:
        result = _rnd.choice(["Heads!", "Tails!"])
        speak(f"Sir, coin toss result — {result}")
    elif "dice" in c or "random number" in c:
        n = _rnd.randint(1, 6)
        speak(f"Dice roll — {n}, sir!")

    # ━━ EXIT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif any(w in c for w in ["exit", "quit", "band karo", "goodbye", "bye", "alvida", "shutdown jarvis"]):
        speak("JARVIS going offline, sir. It's been an honour. Call me anytime!")
        return "EXIT"

    # ━━ UNKNOWN — smart fallback ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    else:
        question_starters = ["kya","kaun","kab","kahan","kyun","kaise","who","what",
                             "when","where","why","how","is","are","was","were","tell"]
        if any(c.startswith(w) for w in question_starters):
            speak(f"Sir, ek second — {c} ke baare mein dhundh raha hoon.")
            _wiki_search(c)
        else:
            speak(_rnd.choice([
                "Sir, thoda aur clearly bolo? Samajh nahi aaya.",
                "Bhai, ye command meri dictionary mein nahi hai. Dobara try karo!",
                "Sir, clarify karo — kya karna hai exactly?",
            ]))

    return None

# ─────────────────────────────────────────────────────────────
#  ASSISTANT LOOP  (background thread)
# ─────────────────────────────────────────────────────────────
def _assistant_loop():
    global _running
    add_log("⚙  JARVIS systems initializing…", "#334466")

    # Run mic calibration + audio pre-caching in parallel
    cache_thread = threading.Thread(target=_precache_blocking, daemon=True)
    cache_thread.start()
    _calibrate_mic()   # runs while cache builds in background

    add_log("✅  JARVIS online — all systems ready!", "#00ffcc")
    speak("JARVIS online. Kya hukum hai, sir? Code likhna hai, koi site kholni hai, ya bas baat karni hai — main hazir hoon!")
    while _running:
        cmd = listen()
        if not _running:
            break
        if cmd:
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
        r.title("JARVIS — Elite AI Voice Assistant")
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
        tk.Label(self.root, text="J A R V I S", bg=BG, fg="#ffffff",
                 font=("Courier New", 24, "bold")).pack(pady=(22, 0))
        tk.Label(self.root, text="JUST  A  RATHER  VERY  INTELLIGENT  SYSTEM", bg=BG, fg="#33335a",
                 font=("Courier New", 7)).pack()

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
