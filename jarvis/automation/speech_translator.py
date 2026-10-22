"""
================================================================================
                    JARVIS POLYGLOT SPEECH TRANSLATOR
================================================================================
Multi-language translation engine providing phonetic dictionary conversions
and localized greeting dictionaries between English, Hindi, Spanish, French,
German, Japanese, and Russian.
================================================================================
"""

from typing import Dict, Tuple, Optional
from jarvis.core.logger import get_logger

# Multilingual common phrasebook
PHRASEBOOK: Dict[str, Dict[str, str]] = {
    "hello": {
        "hindi": "Namaste (नमस्ते)",
        "spanish": "Hola",
        "french": "Bonjour",
        "german": "Hallo / Guten Tag",
        "japanese": "Konnichiwa (こんにちは)",
        "russian": "Privet (Привет)"
    },
    "thank you": {
        "hindi": "Dhanyawad (धन्यवाद)",
        "spanish": "Gracias",
        "french": "Merci",
        "german": "Danke",
        "japanese": "Arigatou (ありがとう)",
        "russian": "Spasibo (Спасибо)"
    },
    "how are you": {
        "hindi": "Aap kaise hain? (आप कैसे हैं?)",
        "spanish": "¿Cómo estás?",
        "french": "Comment allez-vous?",
        "german": "Wie geht es dir?",
        "japanese": "Ogenki desu ka? (お元気ですか)",
        "russian": "Kak dela? (Как дела?)"
    },
    "good morning": {
        "hindi": "Shubh Prabhat (शुभ प्रभात)",
        "spanish": "Buenos días",
        "french": "Bonjour",
        "german": "Guten Morgen",
        "japanese": "Ohayou gozaimasu (おはようございます)",
        "russian": "Dobroye utro (Доброе утро)"
    },
    "good night": {
        "hindi": "Shubh Ratri (शुभ रात्रि)",
        "spanish": "Buenas noches",
        "french": "Bonne nuit",
        "german": "Gute Nacht",
        "japanese": "Oyasuminasai (おやすみなさい)",
        "russian": "Spokoynoy nochi (Спокойной ночи)"
    }
}


class PolyglotTranslator:
    """Provides translation across major world languages."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def translate_phrase(self, phrase: str, target_language: str = "hindi") -> Tuple[bool, str]:
        """Translate common phrase into target language."""
        p_clean = phrase.lower().strip()
        lang_clean = target_language.lower().strip()

        if p_clean in PHRASEBOOK:
            translations = PHRASEBOOK[p_clean]
            if lang_clean in translations:
                translated = translations[lang_clean]
                return True, f"'{phrase}' ko {target_language.capitalize()} me '{translated}' bolte hain sir."

        return False, f"Phrase '{phrase}' ka translation {target_language} me abhi offline dictionary me nahi mila."


def get_translator() -> PolyglotTranslator:
    return PolyglotTranslator()
