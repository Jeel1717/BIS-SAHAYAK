"""
BIS Sahayak — Lightweight Local Embedding Service
Phase 7: RAG / AI Brain

High-performance, dependency-free local semantic feature embedder.
Runs 100% locally with zero external network downloads and zero cost (₹0).
No API key, no PyTorch, no HuggingFace downloads required.

Design:
  - Subword n-grams (3-gram, 4-gram) + word unigrams + bigrams
  - Domain synonym expansion for BIS consumer & hallmarking terms
  - Logarithmic term-frequency weighting
  - Signed feature hashing (MurmurHash/Sha256 hash trick) into fixed 384-d dense vectors
  - Unit L2-normalization for exact cosine distance search in pgvector (<=>)

Configuration (via .env):
  EMBEDDING_MODEL        Model identifier (default: local-lightweight-v1)
  EMBEDDING_DIMENSION    Vector dimension — MUST match the DB column (default: 384)
"""

import hashlib
import logging
import math
import os
import re
from functools import lru_cache
from typing import Sequence

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "local-lightweight-v1"
DEFAULT_DIMENSION = 384

# Common English stopwords to ignore in query/document matching
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from", "further",
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself",
    "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "she", "should", "so", "some", "such", "than", "that",
    "the", "their", "theirs", "them", "themselves", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "with", "would", "you", "your", "yours",
}

# Domain semantic synonym clusters for BIS standards, certification & hallmarking
SYNONYMS = {
    "buy": ["purchase", "buyer", "customer", "bought"],
    "buying": ["purchase", "purchasing", "buyer", "customer"],
    "purchase": ["buy", "buying", "buyer"],
    "check": ["verify", "verification", "test", "testing", "inspect", "assay", "authenticity"],
    "verify": ["check", "verification", "authenticity", "test"],
    "verification": ["check", "verify", "authenticity"],
    "hallmark": ["hallmarked", "hallmarking", "huid", "purity", "gold"],
    "hallmarked": ["hallmark", "hallmarking", "huid", "purity", "gold"],
    "hallmarking": ["hallmark", "hallmarked", "huid", "purity", "gold"],
    "gold": ["hallmark", "hallmarked", "jewellery", "purity", "carat", "karat"],
    "jewellery": ["jewelry", "gold", "hallmark", "ornament"],
    "consumer": ["customer", "citizen", "buyer", "public"],
    "consumers": ["customer", "citizen", "buyer", "public"],
    "isi": ["standard", "certification", "mark", "bis", "quality"],
    "standard": ["isi", "bis", "specification", "conformity"],
    "standards": ["standard", "isi", "bis", "specification"],
    "certification": ["standard", "licence", "license", "scheme", "conformity", "bis", "isi"],
    "product": ["products", "goods", "item", "article"],
    "products": ["product", "goods", "item", "article"],
    "complaint": ["grievance", "violation", "penalty", "misuse"],
}


def _stem(word: str) -> str:
    """Lightweight rule-based suffix trimmer."""
    for suffix in ("ing", "ed", "ly", "es", "s"):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word


def get_embedding_dimension() -> int:
    """Return the configured dimension of the embedding model."""
    return int(os.environ.get("EMBEDDING_DIMENSION", DEFAULT_DIMENSION))


def embed_text(text: str) -> list[float]:
    """
    Generate a single 384-dimensional unit-normalized embedding vector.

    Args:
        text: The text string to embed.

    Returns:
        List of floats (unit L2-normalized embedding vector).
    """
    dim = get_embedding_dimension()
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    content = [t for t in tokens if t not in STOPWORDS and len(t) > 1]

    # Semantic synonym expansion
    expanded = list(content)
    for t in content:
        if t in SYNONYMS:
            expanded.extend(SYNONYMS[t])
        s = _stem(t)
        if s in SYNONYMS:
            expanded.extend(SYNONYMS[s])

    # Term frequency mapping
    tf: dict[str, float] = {}
    for w in expanded:
        tf[w] = tf.get(w, 0.0) + 1.0

    features: dict[str, float] = {}
    # Word features with logarithmic TF scaling
    for w, count in tf.items():
        weight = 1.0 + math.log(count)
        features[f"w:{w}"] = weight * 2.0
        # Character subword ngrams (3-gram, 4-gram)
        for n in (3, 4):
            if len(w) >= n:
                for i in range(len(w) - n + 1):
                    features[f"c:{w[i:i+n]}"] = features.get(f"c:{w[i:i+n]}", 0.0) + 0.3

    # Word bigrams for local context
    for i in range(len(content) - 1):
        bigram = f"{content[i]}_{content[i+1]}"
        features[f"b:{bigram}"] = features.get(f"b:{bigram}", 0.0) + 1.5

    vec = np.zeros(dim, dtype=np.float32)
    for feat, weight in features.items():
        h = hashlib.sha256(feat.encode("utf-8")).digest()
        idx = int.from_bytes(h[:4], "big") % dim
        sign = 1.0 if (h[4] % 2 == 0) else -1.0
        vec[idx] += sign * weight

    norm = float(np.linalg.norm(vec))
    if norm > 1e-8:
        vec = vec / norm
    else:
        # Fallback to uniform unit vector for empty strings
        vec = np.ones(dim, dtype=np.float32) / np.sqrt(dim)

    return vec.tolist()


def embed_batch(texts: Sequence[str], batch_size: int = 64) -> list[list[float]]:
    """
    Generate embedding vectors for a sequence of texts.

    Args:
        texts: Sequence of strings to embed.
        batch_size: Processing batch size (kept for API compatibility).

    Returns:
        List of embedding vectors, one per input text.
    """
    if not texts:
        return []
    return [embed_text(t) for t in texts]
