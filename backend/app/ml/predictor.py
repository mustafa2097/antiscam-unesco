from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

MODEL_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = MODEL_DIR / "scam_tfidf_logreg.joblib"

_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


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
