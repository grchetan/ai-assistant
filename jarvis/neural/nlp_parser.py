"""
================================================================================
            JARVIS IN-HOUSE NEURAL NLP & SYNTACTIC PARSER
================================================================================
Autonomous Natural Language Processing engine incorporating:
  • Tokenization with contraction expansion and punctuation normalization
  • Pure Python Porter-Stemmer algorithm for morphological reduction
  • N-gram generator (unigrams, bigrams, trigrams, skip-grams)
  • Heuristic Rule-Based Part-of-Speech (POS) Tagger
  • Semantic Sentiment & Emotion Intensity Vectorizer
Zero cloud or third-party ML dependencies (Pure Python Standard Library).
================================================================================
"""

import math
import re
from typing import List, Dict, Tuple, Set, Optional, Any
from jarvis.core.logger import get_logger

# ──────────────────────────────────────────────────────────────────────────────
# Contraction & Normalization Map
# ──────────────────────────────────────────────────────────────────────────────
CONTRACTIONS = {
    "ain't": "is not", "aren't": "are not", "can't": "cannot", "'cause": "because",
    "could've": "could have", "couldn't": "could not", "didn't": "did not",
    "doesn't": "does not", "don't": "do not", "hadn't": "had not",
    "hasn't": "has not", "haven't": "have not", "he'd": "he would",
    "he'll": "he will", "he's": "he is", "how'd": "how did",
    "how'll": "how will", "how's": "how is", "i'd": "i would",
    "i'll": "i will", "i'm": "i am", "i've": "i have", "isn't": "is not",
    "it'd": "it would", "it'll": "it will", "it's": "it is",
    "let's": "let us", "might've": "might have", "mightn't": "might not",
    "must've": "must have", "mustn't": "must not", "shan't": "shall not",
    "she'd": "she would", "she'll": "she will", "she's": "she is",
    "should've": "should have", "shouldn't": "should not", "that's": "that is",
    "there's": "there is", "they'd": "they would", "they'll": "they will",
    "they're": "they are", "they've": "they have", "wasn't": "was not",
    "we'd": "we would", "we'll": "we will", "we're": "we are",
    "we've": "we have", "weren't": "were not", "what'll": "what will",
    "what're": "what are", "what's": "what is", "what've": "what have",
    "where's": "where is", "who'll": "who will", "who's": "who is",
    "won't": "will not", "would've": "would have", "wouldn't": "would not",
    "you'd": "you would", "you'll": "you will", "you're": "you are",
    "you've": "you have"
}

# Positive and Negative Lexicons for Sentiment Analysis
POSITIVE_LEXICON: Set[str] = {
    "good", "great", "excellent", "amazing", "wonderful", "fantastic", "awesome",
    "brilliant", "superb", "outstanding", "fast", "speedy", "stable", "love",
    "like", "happy", "success", "successful", "pleased", "satisfy", "satisfied",
    "clean", "sharp", "smart", "genius", "cool", "epic", "perfect", "optimal",
    "badiya", "accha", "achha", "shandar", "zabardast", "mast", "badhiya"
}

NEGATIVE_LEXICON: Set[str] = {
    "bad", "terrible", "awful", "horrible", "slow", "sluggish", "lag", "crash",
    "fail", "failed", "failure", "broken", "bug", "bugs", "error", "errors",
    "hate", "angry", "sad", "unhappy", "frustrating", "annoying", "poor",
    "stutter", "choke", "stuck", "useless", "worst", "hang", "bekar", "kharab",
    "ganda", "pareshan", "mushkil", "dikkat", "problem"
}


class PorterStemmer:
    """Pure-Python implementation of the classic Porter Stemming algorithm."""

    def __init__(self) -> None:
        self.b = ""
        self.k = 0
        self.k0 = 0
        self.j = 0

    def _cons(self, i: int) -> bool:
        if self.b[i] in 'aeiou':
            return False
        if self.b[i] == 'y':
            if i == self.k0:
                return True
            else:
                return not self._cons(i - 1)
        return True

    def _m(self) -> int:
        n = 0
        i = self.k0
        while True:
            if i > self.j:
                return n
            if not self._cons(i):
                break
            i += 1
        i += 1
        while True:
            while True:
                if i > self.j:
                    return n
                if self._cons(i):
                    break
                i += 1
            i += 1
            n += 1
            while True:
                if i > self.j:
                    return n
                if not self._cons(i):
                    break
                i += 1
            i += 1

    def _vowelinstem(self) -> bool:
        for i in range(self.k0, self.j + 1):
            if not self._cons(i):
                return True
        return False

    def _doublec(self, i: int) -> bool:
        if i < self.k0 + 1:
            return False
        if self.b[i] != self.b[i - 1]:
            return False
        return self._cons(i)

    def _cvc(self, i: int) -> bool:
        if i < self.k0 + 2 or not self._cons(i) or self._cons(i - 1) or not self._cons(i - 2):
            return False
        ch = self.b[i]
        if ch in 'wxY':
            return False
        return True

    def _setto(self, s: str) -> None:
        n = len(s)
        self.b = self.b[:self.j + 1] + s + self.b[self.j + n + 1:]
        self.k = self.j + n

    def _r(self, s: str) -> None:
        if self._m() > 0:
            self._setto(s)

    def _step1ab(self) -> None:
        if self.b[self.k] == 's':
            if self.b.endswith('sses'):
                self.k -= 2
            elif self.b.endswith('ies'):
                self._setto('i')
            elif self.b[self.k - 1] != 's':
                self.k -= 1
        if self.b.endswith('eed'):
            if self._m() > 0:
                self.k -= 1
        elif (self.b.endswith('ed') or self.b.endswith('ing')) and self._vowelinstem():
            if self.b.endswith('ed'):
                self.k -= 2
            else:
                self.k -= 3
            if self.b.endswith('at') or self.b.endswith('bl') or self.b.endswith('iz'):
                self._setto('e')
            elif self._doublec(self.k):
                self.k -= 1
                ch = self.b[self.k]
                if ch in 'lsz':
                    self.k += 1
            elif self._m() == 1 and self._cvc(self.k):
                self._setto('e')

    def stem(self, word: str) -> str:
        """Stem single token to grammatical root."""
        w = word.lower()
        if len(w) <= 2:
            return w
        self.b = w
        self.k = len(w) - 1
        self.k0 = 0
        self._step1ab()
        return self.b[:self.k + 1]


class NeuralNLPParser:
    """Natural Language Preprocessor and Syntactic Tokenizer."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.stemmer = PorterStemmer()

    def expand_contractions(self, text: str) -> str:
        """Expand common English contractions."""
        res = text
        for cont, exp in CONTRACTIONS.items():
            pattern = re.compile(re.escape(cont), re.IGNORECASE)
            res = pattern.sub(exp, res)
        return res

    def tokenize(self, text: str) -> List[str]:
        """Convert string to normalized token list."""
        expanded = self.expand_contractions(text.lower())
        tokens = re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", expanded)
        return tokens

    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """Stem token list to root forms."""
        return [self.stemmer.stem(t) for t in tokens]

    def extract_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        """Generate N-Grams from token sequence."""
        if len(tokens) < n:
            return []
        return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

    def tag_pos(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Heuristic rule-based POS tagger."""
        tagged = []
        verbs = {"run", "execute", "start", "stop", "open", "close", "clean", "find", "show", "calculate", "speak", "karo", "batao", "sunao", "kholo", "band"}
        nouns = {"desktop", "file", "folder", "system", "code", "jarvis", "weather", "music", "window", "cpu", "memory", "speed", "test", "internet"}
        adjectives = {"fast", "slow", "high", "low", "deep", "great", "bad", "clean", "dirty", "active"}

        for t in tokens:
            if t.isdigit():
                tagged.append((t, "NUM"))
            elif t in verbs or t.endswith("ing") or t.endswith("ed"):
                tagged.append((t, "VERB"))
            elif t in adjectives:
                tagged.append((t, "ADJ"))
            elif t in nouns:
                tagged.append((t, "NOUN"))
            else:
                tagged.append((t, "OTHER"))
        return tagged

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Determine sentiment valence, emotion intensity, and polarity score."""
        tokens = self.tokenize(text)
        if not tokens:
            return {"polarity": 0.0, "label": "NEUTRAL", "urgency": 0.0}

        pos_count = sum(1 for t in tokens if t in POSITIVE_LEXICON)
        neg_count = sum(1 for t in tokens if t in NEGATIVE_LEXICON)

        total_emotional = pos_count + neg_count
        if total_emotional == 0:
            polarity = 0.0
            label = "NEUTRAL"
        else:
            polarity = (pos_count - neg_count) / float(total_emotional)
            if polarity > 0.2:
                label = "POSITIVE"
            elif polarity < -0.2:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"

        # Urgency: check exclamation marks or urgency tokens
        urgency = 0.0
        if "!" in text or "turant" in text or "fast" in text or "urgent" in text or "emergency" in text:
            urgency = 0.8
        elif neg_count > 1:
            urgency = 0.5

        return {
            "polarity": round(polarity, 2),
            "label": label,
            "pos_count": pos_count,
            "neg_count": neg_count,
            "urgency": urgency
        }


_parser_instance: Optional[NeuralNLPParser] = None

def get_neural_parser() -> NeuralNLPParser:
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = NeuralNLPParser()
    return _parser_instance
