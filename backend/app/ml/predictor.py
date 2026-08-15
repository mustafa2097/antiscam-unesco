from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

MODEL_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = MODEL_DIR / "scam_tfidf_logreg.joblib"

_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
_EXPLANATION_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "عن",
    "على",
    "في",
    "من",
    "إلى",
    "او",
    "أو",
    "مع",
    "هذا",
    "هذه",
}


def normalize_text(text: str) -> str:
    return " ".join(_TOKEN_RE.findall((text or "").lower()))


@lru_cache(maxsize=1)
def load_model() -> Any | None:
    if not MODEL_PATH.exists():
        return None
    try:
        import joblib

        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def predict_scam_probability(text: str) -> dict[str, float | bool]:
    """
    Returns ML probability that a job post is a scam.
    Falls back to unavailable when the artifact is missing.
    """
    cleaned = normalize_text(text)
    if not cleaned:
        return {"available": False, "probability": 0.0}

    pipeline = load_model()
    if pipeline is None:
        return {"available": False, "probability": 0.0}

    try:
        proba = float(pipeline.predict_proba([cleaned])[0][1])
    except Exception:
        return {"available": False, "probability": 0.0}

    return {"available": True, "probability": round(min(max(proba, 0.0), 1.0), 4)}


def explain_scam_features(text: str, *, limit: int = 4) -> list[str]:
    """Return the text features that pushed the logistic model toward scam."""
    cleaned = normalize_text(text)
    pipeline = load_model()
    if not cleaned or pipeline is None:
        return []

    try:
        vectorizer = pipeline.named_steps["tfidf"]
        classifier = pipeline.named_steps["clf"]
        row = vectorizer.transform([cleaned])
        coefficients = classifier.coef_[0]
        feature_names = vectorizer.get_feature_names_out()
        contributions = sorted(
            (
                (float(row[0, index]) * float(coefficients[index]), str(feature_names[index]))
                for index in row.indices
                if float(coefficients[index]) > 0
            ),
            reverse=True,
        )
    except Exception:
        return []

    features: list[str] = []
    for contribution, term in contributions:
        if contribution <= 0 or term in features:
            continue
        words = term.split()
        if not words or all(word in _EXPLANATION_STOPWORDS for word in words):
            continue
        # Prefer meaningful phrases and avoid returning a unigram already
        # represented inside a stronger bigram.
        if any(term in existing.split() and " " in existing for existing in features):
            continue
        features.append(term)
        if len(features) >= max(1, limit):
            break
    return features
