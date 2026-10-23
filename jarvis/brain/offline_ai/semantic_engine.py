"""
================================================================================
            JARVIS IN-HOUSE OFFLINE NLP & SEMANTIC SEARCH ENGINE
================================================================================
Zero-cloud Vector Space Modeling, TF-IDF vectorization, Cosine Similarity,
BM25 Information Retrieval, and Extractive TextRank Summarization.
================================================================================
"""

import math
import re
from collections import Counter
from typing import List, Dict, Tuple, Set, Optional
from jarvis.core.logger import get_logger

STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
    "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only",
    "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
    "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "with", "you",
    "your", "yours", "yourself", "yourselves", "sir", "kya", "hai", "hain", "karo", "batao", "mujhe"
}


class SemanticEngine:
    """In-House NLP vectorizer, semantic document indexer, and summarizer."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def tokenize(self, text: str) -> List[str]:
        """Normalize and tokenize text into clean alpha-numeric terms."""
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        return [w for w in clean.split() if len(w) > 1 and w not in STOP_WORDS]

    def compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute Term Frequency."""
        total = len(tokens)
        if total == 0:
            return {}
        counts = Counter(tokens)
        return {term: count / total for term, count in counts.items()}

    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two sparse term vectors."""
        common = set(vec1.keys()) & set(vec2.keys())
        if not common:
            return 0.0

        dot_product = sum(vec1[t] * vec2[t] for t in common)
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def calculate_bm25_score(
        self,
        query_tokens: List[str],
        doc_tokens: List[str],
        avg_doc_len: float,
        idf_scores: Dict[str, float],
        k1: float = 1.5,
        b: float = 0.75
    ) -> float:
        """BM25 probabilistic relevance score."""
        doc_len = len(doc_tokens)
        doc_counts = Counter(doc_tokens)
        score = 0.0

        for q in query_tokens:
            if q not in doc_counts:
                continue
            tf = doc_counts[q]
            idf = idf_scores.get(q, 1.0)
            numerator = tf * (k1 + 1.0)
            denominator = tf + k1 * (1.0 - b + b * (doc_len / (avg_doc_len if avg_doc_len > 0 else 1.0)))
            score += idf * (numerator / denominator)

        return score

    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """Extractive graph-based TextRank summarization."""
        # Split sentences
        raw_sentences = [s.strip() for s in re.split(r"[.!?\n]+", text) if len(s.strip()) > 15]
        if len(raw_sentences) <= max_sentences:
            return text.strip()

        tokenized_sentences = [self.tokenize(s) for s in raw_sentences]
        sentence_vectors = [self.compute_tf(tokens) for tokens in tokenized_sentences]

        # Calculate sentence importance score based on centrality
        n = len(raw_sentences)
        scores = [0.0] * n

        for i in range(n):
            for j in range(i + 1, n):
                sim = self.cosine_similarity(sentence_vectors[i], sentence_vectors[j])
                scores[i] += sim
                scores[j] += sim

        # Pick top sentences preserving chronological order
        ranked_indices = sorted(range(n), key=lambda idx: scores[idx], reverse=True)[:max_sentences]
        ranked_indices.sort()

        summary = " ".join(raw_sentences[i] for i in ranked_indices)
        return summary

    def extract_keywords(self, text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Extract top representative keywords using TF scoring."""
        tokens = self.tokenize(text)
        if not tokens:
            return []
        tf = self.compute_tf(tokens)
        sorted_kws = sorted(tf.items(), key=lambda x: x[1], reverse=True)
        return sorted_kws[:top_k]


_semantic_instance: Optional[SemanticEngine] = None

def get_semantic_engine() -> SemanticEngine:
    global _semantic_instance
    if _semantic_instance is None:
        _semantic_instance = SemanticEngine()
    return _semantic_instance
