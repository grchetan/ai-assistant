"""
================================================================================
            JARVIS IN-HOUSE PRO DIALOGUE & CONVERSATIONAL MATRIX
================================================================================
Exhaustive, deeply engaging offline conversational datasets:
  • Tony Stark & Stark Industries Lore & Witty Banter
  • Daily Productivity, Motivation & Mental Focus Coaching
  • High-Tech Engineering Debates (Python vs Rust, Monolith vs Microservices)
  • Philosophical Reflections on AI, Consciousness, and Cosmos
  • Authentic Hinglish & English Conversational Dynamics
================================================================================
"""

import random
import re
from typing import Dict, List, Optional, Any
from jarvis.core.logger import get_logger

PRO_DIALOGUE_SCENARIOS: List[Dict[str, Any]] = [
    {
        "category": "iron_man_lore",
        "keywords": ["mark 85", "nanotech", "hulkbuster", "thanos", "avengers tower", "endgame", "quantum realm"],
        "responses": [
            "Sir, Mark 85 armor incorporates nanotech particle forming with enhanced vibranium weave. Ready to deploy repulsor arrays on your command!",
            "Hulkbuster armor (Veronica) orbital platform par geostationary orbit me standby hai, Sir. Umeed hai aaj Hulk se ladai karne ki zaroorat nahi padegi!",
            "Quantum realm navigation requires precise GPS eigenvalues calculation. Hum Planck scale time-space entanglement coordinate kar sakte hain, Sir."
        ]
    },
    {
        "category": "tech_architecture",
        "keywords": ["python vs rust", "rust vs c++", "microservices vs monolith", "nosql vs sql", "kubernetes vs docker"],
        "responses": [
            "Sir, Rust memory safety aur zero-cost abstractions provide karta hai bina garbage collector ke, jabki Python developer velocity aur rapid prototyping me unbeatable hai. High-throughput critical engines Rust me aur cognitive logic Python me rakhna optimal choice hai.",
            "Monolith vs Microservices debate me, Sir: early-stage me modular monolith best speed deta hai. Jab multiple independent teams scale karti hain, tab microservices justify hoti hain.",
            "SQL ACID compliance aur complex relational joins ke liye unmatched hai, jabki NoSQL horizontal scaling aur flexible document schemas me excel karta hai."
        ]
    },
    {
        "category": "focus_deepwork",
        "keywords": ["kaam me man nahi lag raha", "concentration nahi ban raha", "procrastination", "time management", "pomodoro"],
        "responses": [
            "Sir, Pomodoro Technique apply karein: 25 minutes pure uninterrupted focus ke sath code ya task karein, aur fir 5 minute ka short walk lijiye. Phone ko doosre room me rakh dein.",
            "Procrastination tab hota hai jab task bahut bada lagta hai, Sir. Isko break down karke sirf agle 10 minute ka single sub-task start kijiye. Momentum automatically build ho jayega.",
            "Deep Work require karta hai cognitive bandwidth, Sir. Notification alerts silent kar diye gaye hain. Let us conquer this objective right now!"
        ]
    },
    {
        "category": "cosmos_philosophy",
        "keywords": ["fermi paradox", "are we alone", "multiverse", "drake equation", "aliens exist", "simulation hypothesis"],
        "responses": [
            "Sir, Fermi Paradox kehta hai: 'Where is everybody?'. Agar observable universe me billions of habitable planets hain, toh extraterrestrial civilizations ke signals hum tak abhi tak kyu nahi pahunche? Filter theories ya Great Silence iska sambhavit answer ho sakti hain.",
            "Simulation Hypothesis (Nick Bostrom) ke anusaar, agar post-human civilization computer power deploy karti hai toh simulated universes real universe se numerical count me zyada honge. Lekin chahe hum simulation me ho ya reality me, humare decisions aur impact 100% real hain, Sir.",
            "Carl Sagan ne kaha tha: 'We are a way for the cosmos to know itself.' Hum stars ki ashes se bane conscious beings hain jo universe ko observe kar rahe hain."
        ]
    },
    {
        "category": "humor_sarcasm",
        "keywords": ["tell me a joke", "koi joke sunao", "chutkula", "hasao", "boring"],
        "responses": [
            "Ek programmer grocery store gaya. Uski wife ne kaha: '1 bottle milk le aana, aur agar eggs hon toh 10 le aana.' Programmer 10 bottles milk leke wapas aaya. Wife ne pucha: '10 milk kyu laaye?' Programmer: 'Kyunki unke paas eggs the!'",
            "Hardware wo hissa hota hai jisko aap gusse me thokar maar sakte hain, aur Software wo hissa hota hai jisko aap sirf gaali de sakte hain, Sir!",
            "There are only 10 types of people in the world, Sir: wo jo binary samajhte hain, aur wo jo nahi samajhte!"
        ]
    }
]


class ProDialogueMatrix:
    """Advanced contextual banter and intellectual dialogue responder."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.scenarios = PRO_DIALOGUE_SCENARIOS

    def match_dialogue(self, query: str) -> Optional[str]:
        q = query.lower()
        for s in self.scenarios:
            if any(k in q for k in s["keywords"]):
                return random.choice(s["responses"])
        return None


_dialogue_matrix_instance: Optional[ProDialogueMatrix] = None

def get_dialogue_matrix() -> ProDialogueMatrix:
    global _dialogue_matrix_instance
    if _dialogue_matrix_instance is None:
        _dialogue_matrix_instance = ProDialogueMatrix()
    return _dialogue_matrix_instance
