"""
================================================================================
                    JARVIS TRIVIA, JOKES & ENTERTAINMENT PLUGIN
================================================================================
Lighthearted interactive games, riddles, coin flips, dice rolls, and jokes.
================================================================================
"""

import random
from typing import Dict, Any, Tuple, List

from jarvis.plugins.plugin_base import JarvisPlugin

JOKES: List[str] = [
    "Programmer ne apni biwi se pucha: 'Market jaa raha hoon, kya lau?' Biwi ne kaha: '1 packet doodh lao, aur agar ande mile toh 10 le aana.' Programmer 10 packet doodh le aaya... kyunki ande mil gaye the!",
    "Software testers walk into a bar. Runs into a bar. Crawls into a bar. Dances into a bar. Orders 1 beer. Orders 0 beers. Orders 9999 beers. Orders a lizard. Everything works fine. Real customer enters and asks where the bathroom is... Bar catches fire!",
    "Doctor: 'Aapko resting ki zaroorat hai.' Programmer: 'Can I do that in async mode?'",
    "Ek computer ne dusre computer se pucha: 'Tumhe garmi lag rahi hai kya?' Dusra bola: 'Nahi, main toh fan chala raha hoon!'"
]


class TriviaGamesPlugin(JarvisPlugin):
    """Provides jokes, coin flips, and dice rolls."""

    @property
    def name(self) -> str:
        return "trivia_games"

    @property
    def description(self) -> str:
        return "Tells jokes, tosses coins, and rolls dice."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["joke", "chutkula", "coin", "toss", "dice", "pasa"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        t = text.lower()
        if "joke" in t or "chutkula" in t:
            return True, random.choice(JOKES)
        elif "coin" in t or "toss" in t:
            res = random.choice(["Heads aaya hai sir!", "Tails aaya hai sir!"])
            return True, res
        elif "dice" in t or "pasa" in t:
            num = random.randint(1, 6)
            return True, f"Dice par number {num} aaya hai sir!"
        return False, "Unknown entertainment request."
