"""
JARVIS Autonomous Offline AI Subsystem.
Zero-dependency in-house intelligence providing knowledge graphs, symbolic mathematics,
code synthesis, conversational agents, semantic indexing, and expert troubleshooting.
"""

from jarvis.brain.offline_ai.knowledge_engine import get_knowledge_engine
from jarvis.brain.offline_ai.symbolic_math import get_math_engine
from jarvis.brain.offline_ai.code_generator import get_code_engine
from jarvis.brain.offline_ai.conversational_agent import get_conversational_agent
from jarvis.brain.offline_ai.semantic_engine import get_semantic_engine
from jarvis.brain.offline_ai.system_troubleshooter import get_troubleshooter
from jarvis.brain.offline_ai.macro_automator import get_macro_automator
from jarvis.brain.offline_ai.master_offline_brain import get_offline_brain

__all__ = [
    "get_knowledge_engine",
    "get_math_engine",
    "get_code_engine",
    "get_conversational_agent",
    "get_semantic_engine",
    "get_troubleshooter",
    "get_macro_automator",
    "get_offline_brain",
]
