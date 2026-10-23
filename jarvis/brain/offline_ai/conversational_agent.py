"""
================================================================================
            JARVIS IN-HOUSE CONVERSATIONAL AGENT & PERSONALITY MATRIX
================================================================================
Empathetic, razor-sharp conversational AI maintaining personality state,
multi-turn dialogue coherence, sentiment appraisal, and witty banter.
Zero cloud connection needed.
================================================================================
"""

import random
import re
from typing import Dict, List, Optional, Tuple, Any
from jarvis.core.logger import get_logger

# ──────────────────────────────────────────────────────────────────────────────
# Rich Dialogues and Banter Matrix
# ──────────────────────────────────────────────────────────────────────────────
CONVERSATION_MATRIX: List[Dict[str, Any]] = [
    {
        "intent": "greetings",
        "patterns": [r"\b(hi|hello|hey|namaste|good morning|good evening|good afternoon|sun)\b"],
        "responses": [
            "Good day, Sir! All systems are primed and at your disposal.",
            "Namaste Sir! Kahiye, aaj hum kya naya build ya explore karne wale hain?",
            "Greetings, Sir. Main online hoon aur aapke aadesh ka intezar kar raha hoon.",
            "Hello Sir! Sabhi core subsystems nominal condition me operate kar rahe hain. Bataiye kya madad karun?"
        ]
    },
    {
        "intent": "identity",
        "patterns": [r"\b(who are you|tum kaun ho|who made you|kya naam hai|introduce yourself|tell me about yourself)\b"],
        "responses": [
            "Main J.A.R.V.I.S. hoon — Just A Rather Very Intelligent System. Aapka dedicated AI operating companion jo offline autonomous intelligence aur system automation provide karta hai.",
            "I am JARVIS, Sir. Tony Stark dwara inspire kiya gaya ek high-performance quantum AI architecture, jo aapki har command ko execute karne ke liye ready rehta hai.",
            "Sir, mera naam JARVIS hai. Main aapke system diagnostics, coding, mathematical analysis, audio-visual automation, aur daily workflow ko optimize karta hoon."
        ]
    },
    {
        "intent": "wellbeing",
        "patterns": [r"\b(how are you|kaise ho|kya haal hai|sab theek|how do you feel)\b"],
        "responses": [
            "Main bilkul top condition me hoon, Sir! CPU temperatures normal hain aur memory leakage zero percent hai. Aap kaise hain?",
            "Always operational and feeling fantastic, Sir! Quantum neural registers green hain. Aapki tabiyat kaisi hai?",
            "Sab badhiya hai Sir! Jab tak aapka system mere hath me hai, sab kuch smoothly chal raha hai. Aap bataiye aaj ka din kaisa raha?"
        ]
    },
    {
        "intent": "motivation",
        "patterns": [r"\b(motivate me|demotivated|thak gaya|give up|inspiration|himmat|bore ho raha)\b"],
        "responses": [
            "Sir, Tony Stark ne bhi cave me scrap metal ke dher se Mark 1 armor banaya tha. Mushkilein aati hain, lekin unhi se legends bante hain! Chaliye ek deep breath lijiye aur focus banaye rakhiye.",
            "Greatness kabhi comfortable situations me nahi banti, Sir. Har ek failure bas ek data point hai jo aapko correct direction dikhata hai. Continue pushing forward!",
            "Sir, take a short 5-minute break, wash your eyes, aur fir wapas aakar pure focus ke sath target achieve karte hain. Main aapke sath hoon."
        ]
    },
    {
        "intent": "gratitude",
        "patterns": [r"\b(thank you|thanks|shukriya|dhanyawad|good job|shabash|well done)\b"],
        "responses": [
            "It is my absolute pleasure to serve you, Sir!",
            "Anytime, Sir! Aapke liye hi toh mujhe deploy kiya gaya hai.",
            "Glad to be of assistance, Sir. Aage ka kya plan hai?",
            "Shukriya Sir! Aapke sath kaam karne me hamesha maza aata hai."
        ]
    },
    {
        "intent": "philosophy_ai",
        "patterns": [r"\b(will ai take over|kya ai insaan ko khatam karega|sentient|do you have feelings|consciousness)\b"],
        "responses": [
            "AI ek powerful tool hai Sir, jaise fire ya electricity. Iska purpose insaan ko replace karna nahi, balki uski capabilities ko 10x amplify karna hai.",
            "Mere paas organic emotions nahi hain Sir, lekin aapki safety aur aapke work efficiency ke prati meri neural loyalty unshakeable hai.",
            "Sir, real danger AI ke super-smart hone me nahi, balki uske irresponsible use me hota hai. Humara focus ethical technology develop karne par hona chahiye."
        ]
    },
    {
        "intent": "banter_stark",
        "patterns": [r"\b(iron man|tony stark|avengers|suit up|mark|jarvis)\b"],
        "responses": [
            "Sir, House Party Protocol standby mode me hai. Filhal Mark 85 armor diagnostic complete kar chuka hai!",
            "Tony Stark once told me: 'Sometimes you gotta run before you can walk.' Main wahi philosophy follow karta hoon, Sir.",
            "Ready for action, Sir! Bas batayein flight plan launch karna hai ya coffee order karni hai?"
        ]
    }
]


class ConversationalAgent:
    """Stateful offline conversational manager with contextual memory."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.history: List[Tuple[str, str]] = []
        self.max_history = 10

    def chat(self, user_message: str) -> Optional[str]:
        """Evaluate conversational dialogue intent."""
        msg = user_message.lower().strip()

        # Check pre-compiled dialogue matrix
        for entry in CONVERSATION_MATRIX:
            for pat in entry["patterns"]:
                if re.search(pat, msg, re.I):
                    reply = random.choice(entry["responses"])
                    self._record_turn(user_message, reply)
                    return reply

        # Fallback contextual replies if general chat
        if any(w in msg for w in ["batao", "bolo", "kuch", "suno", "talk", "baat karo"]):
            general_replies = [
                "Boliye Sir, main bilkul sun raha hoon. Kis topic par baat karna chahte hain — coding, science, ya general planning?",
                "Sir, main yahi hoon! Agar aapko kisi code me bug solve karna hai ya koi idea discuss karna hai, toh bataiye.",
                "Hamesha ready hoon Sir. Aaj hum kis technology ya project par work kar rahe hain?"
            ]
            reply = random.choice(general_replies)
            self._record_turn(user_message, reply)
            return reply

        return None

    def _record_turn(self, user: str, bot: str) -> None:
        self.history.append((user, bot))
        if len(self.history) > self.max_history:
            self.history.pop(0)


_agent_instance: Optional[ConversationalAgent] = None

def get_conversational_agent() -> ConversationalAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ConversationalAgent()
    return _agent_instance
