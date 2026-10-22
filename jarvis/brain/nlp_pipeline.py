"""
================================================================================
                    JARVIS NATURAL LANGUAGE & SENTIMENT PIPELINE
================================================================================
Comprehensive linguistic engine providing text tokenization, stopword removal,
Hinglish vocabulary normalization, intent entity extraction, and sentiment
analysis for empathetic personality adaptation.
================================================================================
"""

import re
from typing import List, Dict, Tuple, Optional, Any

# Hinglish stop words that can be ignored for core intent extraction
HINGLISH_STOPWORDS = {
    "hai", "ho", "hoon", "tha", "the", "thi", "ka", "ke", "ki", "ko",
    "se", "me", "mein", "par", "pe", "aur", "ya", "bhi", "toh", "kya",
    "kyun", "kaisa", "kaise", "kaisi", "mera", "meri", "mere", "aapka",
    "aapki", "aapke", "tumhara", "tumhari", "karo", "karna", "kar", "do",
    "de", "dijiye", "batao", "batayein", "sunao", "please", "sir", "bhai",
    "jarvis", "the", "a", "an", "is", "are", "was", "were", "to", "for"
}

# Positive and negative lexical polarity dictionaries
POSITIVE_LEXICON = {
    "good", "great", "excellent", "awesome", "fantastic", "amazing", "badiya",
    "shandaar", "zabardast", "mast", "badhiya", "perfect", "nice", "love",
    "happy", "khush", "dhanyawad", "thanks", "thank", "shukriya", "smart", "genius"
}

NEGATIVE_LEXICON = {
    "bad", "terrible", "horrible", "worst", "fail", "error", "kharab",
    "bakwaas", "ganda", "slow", "problem", "issue", "sad", "angry", "gussa",
    "annoyed", "frustrated", "bug", "fault", "useless", "bekaar"
}


class NLPPipeline:
    """Pre-processes spoken text and evaluates emotional sentiment."""

    @classmethod
    def clean_text(cls, raw_text: str) -> str:
        """Strip punctuation and non-alphanumeric noise."""
        cleaned = re.sub(r"[^\w\s]", " ", raw_text.lower())
        return re.sub(r"\s+", " ", cleaned).strip()

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        """Split clean text into word tokens."""
        return cls.clean_text(text).split()

    @classmethod
    def remove_stopwords(cls, tokens: List[str]) -> List[str]:
        """Filter out common particles and conversational filler words."""
        return [t for t in tokens if t not in HINGLISH_STOPWORDS]

    @classmethod
    def analyze_sentiment(cls, text: str) -> Dict[str, Any]:
        """
        Evaluate emotional polarity of user query.
        Returns: { 'polarity': float, 'label': 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' }
        """
        tokens = cls.tokenize(text)
        if not tokens:
            return {"polarity": 0.0, "label": "NEUTRAL"}

        pos_count = sum(1 for t in tokens if t in POSITIVE_LEXICON)
        neg_count = sum(1 for t in tokens if t in NEGATIVE_LEXICON)

        total = pos_count + neg_count
        if total == 0:
            return {"polarity": 0.0, "label": "NEUTRAL"}

        polarity = (pos_count - neg_count) / total
        if polarity > 0.2:
            label = "POSITIVE"
        elif polarity < -0.2:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"

        return {
            "polarity": round(polarity, 2),
            "label": label,
            "positive_words": pos_count,
            "negative_words": neg_count
        }

    @classmethod
    def extract_time_entities(cls, text: str) -> Optional[int]:
        """Extract duration values in minutes from phrases like '5 minute', '10 mins'."""
        match = re.search(r"\b(\d+)\s*(?:minute|minutes|min|ghante|hours?)\b", text.lower())
        if match:
            num = int(match.group(1))
            if "ghante" in text or "hour" in text:
                num *= 60
            return num
        return None
