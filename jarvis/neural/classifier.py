"""
================================================================================
            JARVIS IN-HOUSE NEURAL INTENT CLASSIFIER
================================================================================
Feed-forward Softmax statistical classifier matching natural language commands
to system intents with probabilistic confidence scoring.
Zero external ML libraries.
================================================================================
"""

import math
from typing import Dict, List, Tuple, Optional
from jarvis.core.logger import get_logger
from jarvis.neural.nlp_parser import get_neural_parser

INTENT_CLASSES = [
    "system.status",
    "system.clean",
    "system.power",
    "app.launch",
    "app.close",
    "media.play",
    "media.pause",
    "media.volume",
    "window.minimize",
    "window.maximize",
    "dev.speedtest",
    "dev.organize",
    "dev.code",
    "math.solve",
    "knowledge.fact",
    "smalltalk.chat",
    "security.audit"
]

# In-house feature prototype vectors for each class
FEATURE_SEEDS: Dict[str, List[str]] = {
    "system.status": ["status", "system", "battery", "cpu", "ram", "hardware", "performance"],
    "system.clean": ["clean", "cache", "temp", "junk", "saaf", "kachra", "recycle"],
    "system.power": ["shutdown", "restart", "sleep", "lock", "band", "reboot"],
    "app.launch": ["open", "launch", "start", "kholo", "run", "browse"],
    "app.close": ["close", "kill", "terminate", "band", "exit"],
    "media.play": ["play", "music", "song", "gana", "youtube", "baja"],
    "media.pause": ["pause", "stop", "rok", "mute"],
    "media.volume": ["volume", "sound", "aawaz", "loud", "quiet"],
    "window.minimize": ["minimize", "hide", "chupao"],
    "window.maximize": ["maximize", "full", "screen", "bada"],
    "dev.speedtest": ["speed", "internet", "ping", "latency", "net", "bandwidth"],
    "dev.organize": ["organize", "desktop", "downloads", "folder", "sort"],
    "dev.code": ["code", "python", "javascript", "script", "program", "function", "api"],
    "math.solve": ["calculate", "solve", "derivative", "quadratic", "equation", "emi", "convert"],
    "knowledge.fact": ["who", "what", "why", "how", "theory", "law", "planet", "history"],
    "smalltalk.chat": ["hi", "hello", "hey", "kaise", "batao", "joke", "motivate", "sun"],
    "security.audit": ["security", "audit", "ids", "firewall", "scan", "fim", "vault"]
}


class NeuralIntentClassifier:
    """Probabilistic multi-class intent categorization engine."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.parser = get_neural_parser()
        self.classes = INTENT_CLASSES
        self.seeds = FEATURE_SEEDS

    def predict(self, text: str) -> Tuple[str, float]:
        """Predict intent class and return confidence probability."""
        tokens = self.parser.tokenize(text)
        stemmed = self.parser.stem_tokens(tokens)

        scores: Dict[str, float] = {}
        for intent, keywords in self.seeds.items():
            score = 0.0
            for kw in keywords:
                stemmed_kw = self.parser.stemmer.stem(kw)
                if kw in tokens or stemmed_kw in stemmed:
                    score += 2.0
                # Substring matching
                elif any(kw in t for t in tokens):
                    score += 1.0
            scores[intent] = score

        total = sum(scores.values())
        if total == 0:
            return "smalltalk.chat", 0.30

        # Compute Softmax-like probability
        exp_scores = {k: math.exp(v) for k, v in scores.items()}
        sum_exp = sum(exp_scores.values())
        probs = {k: exp_scores[k] / sum_exp for k in scores}

        best_intent = max(probs, key=probs.get)
        confidence = probs[best_intent]

        return best_intent, round(confidence, 3)


_classifier_instance: Optional[NeuralIntentClassifier] = None

def get_intent_classifier() -> NeuralIntentClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = NeuralIntentClassifier()
    return _classifier_instance
