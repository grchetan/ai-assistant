# =========================
# MEGA VOICE ASSISTANT
# =========================

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import subprocess
import pyautogui
from plyer import notification
from plyer import notification
import time

# ---------------- VOICE ENGINE SETUP ----------------
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)   # Female clear voice
engine.setProperty("rate", 170)
engine.setProperty("volume", 1)

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# ---------------- LISTEN FUNCTION ----------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)

    try:
        print("🧠 Recognizing...")
        command = r.recognize_google(audio, language="en-in")
        print("You said:", command)
        return command.lower()
    except:
        speak("Clear nahi aaya, dubara bolo.")
        return ""

# ---------------- CLOSE ALL BROWSERS EXCEPT VS CODE ----------------
def close_all_tabs_except_vscode():
    speak("Saare browser band kar raha hoon, VS code chalu rahega.")

    # Chrome, Edge, Firefox close
    os.system("taskkill /f /im chrome.exe")
    os.system("taskkill /f /im msedge.exe")
    os.system("taskkill /f /im firefox.exe")
    os.system("taskkill /f /im brave.exe")
    os.system("taskkill /f /im opera.exe")

    speak("Saare tabs band ho gaye. VS Code safe hai.")

# ---------------- BASIC INFO ----------------
def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"Ab time hai {now}")

def tell_date():
    today = datetime.datetime.now().strftime("%d %B %Y")
    speak(f"Aaj ki date hai {today}")

# ---------------- OPEN APPLICATIONS ----------------
def open_notepad(): os.system("notepad")
def open_word(): os.system("start winword")
def open_excel(): os.system("start excel")
def open_ppt(): os.system("start powerpnt")
def open_cmd(): os.system("start cmd")
def open_vscode(): os.system("code")
def open_calculator(): os.system("calc")
def open_explorer(): os.system("explorer")
def open_chrome(): os.system("start chrome")

# ---------------- WEB ----------------
def open_google(): webbrowser.open("https://www.google.com")
def open_youtube(): webbrowser.open("https://www.youtube.com")
def open_github(): webbrowser.open("https://github.com")
def open_stackoverflow(): webbrowser.open("https://stackoverflow.com")

def google_search(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")

# ---------------- SYSTEM CONTROLS ----------------
def wifi_password():
    command = "start cmd /k netsh wlan show profile key=clear"
    subprocess.run(command, shell=True)

def shutdown_pc():
    speak("System 10 seconds me shutdown hoga.")
    os.system("shutdown /s /t 10")

def restart_pc():
    speak("System restart ho raha hai.")
    os.system("shutdown /r /t 10")

# ---------------- SCREENSHOT ----------------
def take_screenshot():
    image = pyautogui.screenshot()
    filename = "screenshot.png"
    image.save(filename)
    speak("Screenshot save ho gaya.")

# ---------------- REMINDER ----------------
def set_reminder(rem_time, msg):
    speak("Reminder set ho gaya.")
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now == rem_time:
            notification.notify(
                title="IMPORTANT REMINDER",
                message=msg,
                timeout=10
            )
            speak(msg)
            break
        time.sleep(20)

# ---------------- MAIN AI BRAIN ----------------
def main():
    speak("Hello Chetan, main tumhara mega voice assistant hoon. Command bolo.")

    while True:
        command = listen()

        if command == "":
            continue

        # -------- BASIC --------
        if "time" in command:
            tell_time()

        elif "date" in command:
            tell_date()

        # -------- STUDENT --------
        elif "open notepad" in command:
            speak("Notepad open kar raha hoon.")
            open_notepad()

        elif "open word" in command:
            speak("Microsoft Word open kar raha hoon.")
            open_word()

        elif "open calculator" in command:
            open_calculator()

        elif "open youtube" in command:
            open_youtube()

        elif "screenshot" in command:
            take_screenshot()

        # -------- PROFESSIONAL --------
        elif "open excel" in command:
            open_excel()

        elif "open powerpoint" in command:
            open_ppt()

        elif "open file explorer" in command:
            open_explorer()
        
        

        elif "shutdown" in command:
            shutdown_pc()

        elif "restart" in command:
            restart_pc()

        # -------- DEVELOPER --------
        elif "open vscode" in command or "open code editor" in command:
            open_vscode()

        elif "open cmd" in command or "open command prompt" in command:
            open_cmd()

        elif "open github" in command:
            open_github()

        elif "open stackoverflow" in command:
            open_stackoverflow()

        elif "search" in command:
            speak("Kya search karna hai?")
            query = listen()
            if query:
                google_search(query)

        elif "wifi" in command:
            wifi_password()
        

        elif "close all tabs" in command or "close all browser" in command:
         close_all_tabs_except_vscode()

        # -------- EXIT --------
        elif "exit" in command or "quit" in command or "band" in command:
            speak("Goodbye Chetan. Mein band ho raha hoon.")
            break

        else:
            speak("Ye command mujhe samajh nahi aayi.")

        

# ---------------- START PROGRAM ----------------
if __name__ == "__main__":
    main()
