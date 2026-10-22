"""
================================================================================
                    JARVIS VOICE-DRIVEN CYBERPUNK RPG
================================================================================
Interactive voice text adventure role-playing game:
  - Branching cyber narrative in Neo-Tokyo 2099
  - Character stats (Health, Energy, Credits, Inventory)
  - Dice combat engine with procedural loot drops
  - Full voice-driven input handling
================================================================================
"""

import random
from typing import Dict, List, Any, Tuple, Optional

from jarvis.core.logger import get_logger


class CyberpunkRPG:
    """Voice-driven interactive adventure engine."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.is_active = False
        self.player_hp = 100
        self.player_energy = 50
        self.credits = 100
        self.inventory: List[str] = ["Cyberdeck", "Health Stim"]
        self.current_location = "Hacker_Den"

    def start_game(self) -> str:
        """Initialize new adventure session."""
        self.is_active = True
        self.player_hp = 100
        self.player_energy = 50
        self.credits = 100
        self.inventory = ["Cyberdeck", "Health Stim"]
        self.current_location = "Hacker_Den"

        intro = (
            "Welcome to Neo-Tokyo 2099, Operative! "
            "Aap ek underground Hacker Den me khade hain. Rain bahar gir rahi hai. "
            "Samne ek encrypted server terminal hai, aur right side me ek dark alley exit hai. "
            "Kya karenge aap? 'Hack terminal' bolein ya 'go to alley'?"
        )
        self.logger.info("Started Cyberpunk RPG adventure session.", "RPG")
        return intro

    def process_player_action(self, action_text: str) -> str:
        """Evaluate player voice choice."""
        if not self.is_active:
            return "Sir, RPG game abhi start nahi hua hai. 'Start game' bolein shuru karne ke liye."

        act = action_text.lower().strip()

        # Terminal hack branch
        if "hack" in act or "terminal" in act:
            roll = random.randint(1, 20)
            if roll >= 10:
                reward = random.randint(50, 150)
                self.credits += reward
                return f"Hack Successful! (Dice roll: {roll}). Aapne corporate firewall bypass karke {reward} credits loot liye!"
            else:
                damage = random.randint(10, 20)
                self.player_hp -= damage
                return f"Firewall Counter-Attack! (Dice roll: {roll}). Security pulse ne aapko shock diya. {damage} HP lost! Current HP: {self.player_hp}."

        # Alleyway branch
        elif "alley" in act or "exit" in act or "bahar" in act:
            self.current_location = "Neon_Alley"
            return (
                "Aap Neon Alley me enter karte hain. Ek rogue security cyborg aapka rasta block kar raha hai! "
                "Fight karein ya evade? 'Fight cyborg' ya 'use stim'?"
            )

        # Combat branch
        elif "fight" in act or "attack" in act:
            roll = random.randint(1, 20)
            if roll >= 12:
                self.inventory.append("EMP Grenade")
                return f"Victory! (Dice roll: {roll}). Aapne cyborg ko neutralize kar diya! Loot me 'EMP Grenade' mila!"
            else:
                self.player_hp -= 30
                if self.player_hp <= 0:
                    self.is_active = False
                    return "Critical Damage! Cyborg ne aapko overpower kar diya. Game Over sir! Phir se khelne ke liye 'start game' bolein."
                return f"Cyborg counter-attack! Aapko 30 damage mila. Current HP: {self.player_hp}."

        # Inventory check
        elif "inventory" in act or "items" in act:
            items_str = ", ".join(self.inventory)
            return f"Operative Inventory: {items_str}. Credits: {self.credits}, HP: {self.player_hp}."

        # Quit
        elif "quit" in act or "exit game" in act:
            self.is_active = False
            return "RPG session concluded sir. Systems returning to normal assistant mode."

        return "Command samajh nahi aayi operative. 'Hack terminal', 'go to alley', 'check inventory' ya 'quit' bolein."


def get_rpg_game() -> CyberpunkRPG:
    return CyberpunkRPG()
