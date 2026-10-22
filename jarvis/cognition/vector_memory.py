"""
================================================================================
                    JARVIS VECTOR SEMANTIC MEMORY (RAG)
================================================================================
Lightweight local vector retrieval engine using pure NumPy TF-IDF vectorization
and cosine similarity geometry. Enables sub-millisecond semantic search across
past conversational contexts, developer notes, and personal facts.
================================================================================
"""

import math
import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

from jarvis.core.logger import get_logger


class VectorMemoryStore:
    """Stores text documents as normalized TF-IDF semantic embeddings."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self._documents: List[Dict[str, Any]] = []
        self._vocabulary: Dict[str, int] = {}
        self._idf: np.ndarray = np.array([])
        self._doc_matrix: Optional[np.ndarray] = None

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        return [w for w in cleaned.split() if len(w) > 2]

    def add_document(self, doc_id: str, content: str, category: str = "general") -> None:
        """Append document to vector corpus and rebuild sparse index."""
        self._documents.append({
            "id": doc_id,
            "content": content,
            "category": category
        })
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Recompute TF-IDF vocabulary matrix across all corpus documents."""
        if not self._documents:
            return

        # 1. Build unified vocabulary
        tokenized_docs = [self._tokenize(d["content"]) for d in self._documents]
        vocab = {}
        for tokens in tokenized_docs:
            for t in tokens:
                if t not in vocab:
                    vocab[t] = len(vocab)
        self._vocabulary = vocab

        V = len(vocab)
        N = len(self._documents)
        if V == 0 or N == 0:
            return

        # 2. Document frequency calculation
        df = np.zeros(V, dtype=np.float32)
        tf_matrix = np.zeros((N, V), dtype=np.float32)

        for doc_idx, tokens in enumerate(tokenized_docs):
            if not tokens:
                continue
            unique_tokens = set(tokens)
            for t in unique_tokens:
                df[vocab[t]] += 1
            for t in tokens:
                tf_matrix[doc_idx, vocab[t]] += 1

            # Sub-linear term frequency scaling
            tf_matrix[doc_idx] = np.log1p(tf_matrix[doc_idx])

        # 3. Inverse Document Frequency (IDF) with smooth smoothing
        self._idf = np.log((N + 1.0) / (df + 1.0)) + 1.0

        # 4. TF-IDF weighting and L2 normalization
        tfidf = tf_matrix * self._idf
        norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._doc_matrix = tfidf / norms

    def search_semantic(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Locate the top most semantically relevant documents matching query.
        """
        if not self._documents or self._doc_matrix is None or not self._vocabulary:
            return []

        tokens = self._tokenize(query)
        if not tokens:
            return []

        # Vectorize query
        q_vec = np.zeros(len(self._vocabulary), dtype=np.float32)
        for t in tokens:
            if t in self._vocabulary:
                q_vec[self._vocabulary[t]] += 1

        if np.all(q_vec == 0):
            return []

        q_vec = np.log1p(q_vec) * self._idf
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec /= q_norm

        # Compute cosine similarities across matrix
        similarities = np.dot(self._doc_matrix, q_vec)

        # Sort descending
        ranked_indices = np.argsort(-similarities)[:top_k]
        results = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            if score > 0.05: # Minimum threshold
                d = self._documents[idx].copy()
                d["similarity_score"] = round(score, 3)
                results.append(d)

        return results


def get_vector_memory() -> VectorMemoryStore:
    return VectorMemoryStore()
