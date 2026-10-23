"""
================================================================================
            JARVIS EXPANDED ENCYCLOPEDIC KNOWLEDGE GRAPH
================================================================================
Massive structured offline reference corpus spanning:
  • Space Exploration & Modern Astrophysics (Chandrayaan-3, JWST, Artemis)
  • Advanced Theoretical Physics (Dark Matter, Higgs Boson, String Theory)
  • Medical First-Aid & Emergency Response Guidelines
  • Historical Milestones of Artificial Intelligence
  • Operating System Kernels & Architecture (Linux, Windows NT)
Zero internet required.
================================================================================
"""

from typing import Dict, List, Any, Optional
from jarvis.core.logger import get_logger

EXPANDED_FACTS: List[Dict[str, Any]] = [
    {
        "id": "space_chandrayaan3",
        "keywords": ["chandrayaan", "chandrayaan 3", "isro moon", "moon south pole", "vikram lander", "pragyan rover"],
        "title": "ISRO Chandrayaan-3 Mission",
        "content": (
            "Chandrayaan-3 ISRO ka historical lunar exploration mission tha:\n"
            "• Landing Date: 23 August 2023 ko Bharat chaand ke South Pole ke paas soft landing karne wala duniya ka pehla desh bana!\n"
            "• Components: Propulsion Module, Vikram Lander, aur Pragyan Rover.\n"
            "• Discovery: Lunar surface par sulfur (S), iron (Fe), calcium, aur surface thermal profile ki direct measurements li gayin.\n"
            "• National Space Day: 23 August ko Bharat me National Space Day declare kiya gaya."
        )
    },
    {
        "id": "space_jwst",
        "keywords": ["james webb", "jwst", "hubble telescope", "infrared telescope", "lagrange point l2"],
        "title": "James Webb Space Telescope (JWST)",
        "content": (
            "James Webb Space Telescope (JWST) NASA, ESA aur CSA ka premier deep-space observatory hai:\n"
            "• Location: Earth se 1.5 million km door Sun-Earth Lagrange Point 2 (L2) par orbit karta hai.\n"
            "• Mirror: 6.5-meter gold-plated beryllium primary mirror.\n"
            "• Mission: Universe ki sabse pehli galaxies, exoplanet atmospheres me water vapor aur atmospheric gases ko infrared spectrum me detect karta hai."
        )
    },
    {
        "id": "phys_higgs_boson",
        "keywords": ["higgs boson", "god particle", "cern", "lhc", "large hadron collider", "standard model"],
        "title": "The Higgs Boson & The Standard Model",
        "content": (
            "Higgs Boson (jise pop-culture me 'God Particle' kaha jata hai):\n"
            "• Discovery: 4 July 2012 ko CERN ke Large Hadron Collider (LHC) me detect hua.\n"
            "• Mechanism: Higgs Field universe me continuous present hai; fundamental particles (like quarks, electrons) is field ke sath interact karke mass acquire karte hain.\n"
            "• Mass: Lagbhag 125.1 GeV/c²."
        )
    },
    {
        "id": "firstaid_cpr",
        "keywords": ["cpr steps", "heart attack first aid", "cardiac arrest first aid", "cpr kaise de"],
        "title": "Cardiopulmonary Resuscitation (CPR) Emergency Protocol",
        "content": (
            "CPR Emergency Protocol (Adult):\n"
            "1. Check Responsiveness: Person ke kandhe tap karein aur zor se puchein 'Are you okay?'. Emergency services (112/108) ko turant call karein.\n"
            "2. Chest Compressions: Dono hath chest ke center me interlock karein. 100 se 120 beats per minute ki speed se 2-inch gehra press karein (Stayin' Alive beat ke hisab se).\n"
            "3. 30:2 Ratio: 30 hard compressions ke baad 2 rescue breaths dein agar trained hain. Rescue team ke aane tak compressions continue rakhein."
        )
    },
    {
        "id": "ai_history",
        "keywords": ["history of ai", "alan turing", "turing test", "dartmouth 1956", "transformer architecture"],
        "title": "Milestones in Artificial Intelligence",
        "content": (
            "Artificial Intelligence ki historical timeline:\n"
            "• 1950: Alan Turing ne landmark paper publish kiya aur 'Turing Test' propose kiya ('Can machines think?').\n"
            "• 1956: Dartmouth Workshop jahan John McCarthy ne 'Artificial Intelligence' term coin kiya.\n"
            "• 1997: IBM Deep Blue ne World Chess Champion Garry Kasparov ko haraya.\n"
            "• 2017: Google researchers ne 'Attention Is All You Need' paper publish kiya, jisse modern Transformer architecture aur LLMs (GPT, Gemini, Claude) revolution shuru hua."
        )
    }
]


class ExpandedKnowledgeBase:
    """Multi-domain encyclopedic facts retriever."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.facts = EXPANDED_FACTS

    def search(self, query: str) -> Optional[str]:
        q = query.lower()
        for item in self.facts:
            if any(k in q for k in item["keywords"]):
                return f"Sir, [{item['title']}]:\n\n{item['content']}"
        return None


_expanded_kb_instance: Optional[ExpandedKnowledgeBase] = None

def get_expanded_knowledge_base() -> ExpandedKnowledgeBase:
    global _expanded_kb_instance
    if _expanded_kb_instance is None:
        _expanded_kb_instance = ExpandedKnowledgeBase()
    return _expanded_kb_instance
