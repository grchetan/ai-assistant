"""
================================================================================
                    JARVIS DYNAMIC SMALLTALK & BANTER MATRIX
================================================================================
Context-aware conversational engine delivering time-sensitive greetings,
ambient idle banter, coding check-ins, and witty Hinglish responses without
repetitive patterns.
================================================================================
"""

import time
import random
from typing import List, Optional

from jarvis.core.state import get_state_manager

# ─────────────────────────────────────────────────────────────
#  IDLE CHAT PHRASES (PROACTIVE INITIATION)
# ─────────────────────────────────────────────────────────────
PROACTIVE_IDLE_MESSAGES: List[str] = [
    "Sir, main yahan hoon — koi kaam ho toh bas ek aawaz dijiyega!",
    "Bhai, coding chal rahi hai kya? Koi bug fas gaya toh batao, solve karte hain.",
    "Sir, kaafi der se shanti hai. Kuch music play karoon ya news sunna chahenge?",
    "Aap busy lag rahe hain sir. Main background systems monitor kar raha hoon.",
    "Sir, thoda paani pi lijiye! Hydration zaroori hai.",
    "PC ke saare core bilkul normal chal rahe hain sir. Koi task assign karna hai?",
    "Sir, agar koi research karni ho ya YouTube pe kuch dekhna ho toh boliyega.",
    "Main full active mode me hoon sir, jab bhi zaroorat ho bataiye.",
    "Bhai thoda break le lo, screen continuously dekhna aankhon ke liye thik nahi.",
    "Sir, koi new project start kar rahe hain kya? Main ready hoon assist karne ko."
]

# ─────────────────────────────────────────────────────────────
#  RANDOM TECH TRIVIA & FUN FACTS
# ─────────────────────────────────────────────────────────────
TECH_FACTS: List[str] = [
    "Kya aapko pata hai sir? Pehla computer mouse lakdi (wood) ka bana tha 1964 me Doug Engelbart dwara.",
    "Sir, Python language ka naam kisi saamp par nahi, balki Monty Python comedy group par rakha gaya tha!",
    "Duniya ka pehla 1 GB hard drive 1980 me IBM ne banaya tha, aur uska wazan lagbhag 250 kilo tha!",
    "Sir, NASA ke Apollo 11 computer se lakhon guna zyada compute power aaj aapke is laptop me hai.",
    "Domain name 'symbolics.com' internet ka sabse pehla registered domain tha, 15 March 1985 ko."
]

# ─────────────────────────────────────────────────────────────
#  TIME-SENSITIVE GREETINGS
# ─────────────────────────────────────────────────────────────
def get_time_aware_greeting(user_name: str = "Sir") -> str:
    hour = time.localtime().tm_hour
    if 4 <= hour < 12:
        return f"Good morning {user_name}! JARVIS online hai, aaj ka din productive banate hain!"
    elif 12 <= hour < 17:
        return f"Good afternoon {user_name}! Sabhi systems operational hain. Kya madad karoon?"
    elif 17 <= hour < 22:
        return f"Good evening {user_name}! Shaam ho gayi hai. Kya hukum hai aapka?"
    else:
        return f"Late night coding session chal raha hai {user_name}? Main poori tarah active hoon, bataiye kya karna hai."


class SmallTalkEngine:
    """Manages proactive conversation without repetitions."""

    def __init__(self) -> None:
        self.state = get_state_manager()
        self._idle_deck = PROACTIVE_IDLE_MESSAGES.copy()
        random.shuffle(self._idle_deck)
        self._facts_deck = TECH_FACTS.copy()
        random.shuffle(self._facts_deck)

    def get_proactive_idle_message(self) -> str:
        """Fetch a fresh idle conversation starter."""
        if not self._idle_deck:
            self._idle_deck = PROACTIVE_IDLE_MESSAGES.copy()
            random.shuffle(self._idle_deck)
        return self._idle_deck.pop(0)

    def get_random_fact(self) -> str:
        """Fetch an interesting tech or science fact."""
        if not self._facts_deck:
            self._facts_deck = TECH_FACTS.copy()
            random.shuffle(self._facts_deck)
        return self._facts_deck.pop(0)

    def get_greeting(self, user_name: str = "Sir") -> str:
        return get_time_aware_greeting(user_name)


def get_smalltalk_engine() -> SmallTalkEngine:
    return SmallTalkEngine()
