"""
JARVIS In-House Neural & Cognitive Subsystems.
Deep local AI modules for intent classification, entity recognition,
symbolic calculus, matrix math, code synthesis, and advanced knowledge representation.
"""

from jarvis.neural.nlp_parser import get_neural_parser
from jarvis.neural.entity_recognizer import get_entity_recognizer
from jarvis.neural.classifier import get_intent_classifier
from jarvis.neural.symbolic_calculus import get_calculus_engine
from jarvis.neural.code_synthesis_library import get_code_library
from jarvis.neural.knowledge_base_expanded import get_expanded_knowledge_base

__all__ = [
    "get_neural_parser",
    "get_entity_recognizer",
    "get_intent_classifier",
    "get_calculus_engine",
    "get_code_library",
    "get_expanded_knowledge_base",
]
