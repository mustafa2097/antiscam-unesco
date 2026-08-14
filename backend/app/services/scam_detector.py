from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.predictor import predict_scam_probability
from app.models import ScamIndicator
from app.services.role_extractor import extract_role
from app.services.scam_patterns import BUILTIN_INDICATORS


def _match_indicators(text: str, indicators: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lowered = (text or "").lower()
    hits: list[dict[str, Any]] = []
    for item in indicators:
        pattern = str(item.get("pattern") or "").strip().lower()
        if not pattern or pattern not in lowered:
            continue
        hits.append(
            {
                "pattern": str(item.get("pattern")),
                "category": str(item.get("category") or "general"),
                "severity": float(item.get("severity") or 0.5),
                "language": str(item.get("language") or ""),
            }
        )
    return hits


async def _load_db_indicators(db: AsyncSession | None) -> list[dict[str, Any]]:
    if db is None:
        return []
    result = await db.execute(select(ScamIndicator).limit(2000))
    rows = result.scalars().all()
    return [
        {
            "pattern": row.pattern,
            "category": row.category,
            "severity": row.severity,
            "language": row.language,
        }
        for row in rows
    ]


def _combine_scores(
    *,
    ml_probability: float,
    ml_available: bool,
    matches: list[dict[str, Any]],
) -> tuple[float, list[str], str]:
    """
    Blend ML + rule hits into a single risk score in [0, 1].
    """
    flags: list[str] = []
    rule_score = 0.0
    if matches:
        # diminishing returns so many weak hits don't explode the score
        severities = sorted((m["severity"] for m in matches), reverse=True)
        acc = 0.0
        for i, sev in enumerate(severities[:8]):
            acc += sev * (0.55**i)
        rule_score = min(acc, 1.0)
        flags.extend(sorted({m["category"] for m in matches}))

    if ml_available:
        risk = (0.55 * ml_probability) + (0.45 * rule_score)
        flags.append("ml_model")
    else:
        risk = rule_score
        flags.append("rules_only")

    if risk >= 0.75:
        label = "high"
    elif risk >= 0.45:
        label = "medium"
    elif risk >= 0.2:
        label = "low"
    else:
        label = "safe"

    return round(min(max(risk, 0.0), 1.0), 4), flags, label


async def analyze_job_text(
    text: str,
    *,
    db: AsyncSession | None = None,
    extra_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    content = (text or "").strip()
    role = extract_role(content)

    db_indicators = await _load_db_indicators(db)
    indicators = db_indicators or BUILTIN_INDICATORS
    matches = _match_indicators(content, indicators)

    ml = predict_scam_probability(content)
    ml_prob = float(ml["probability"])
    ml_available = bool(ml["available"])

    risk_score, flags, risk_level = _combine_scores(
        ml_probability=ml_prob,
        ml_available=ml_available,
        matches=matches,
    )

    model_meta: dict[str, Any] = {}
    try:
        from app.ml.predictor import MODEL_PATH
        import json

        metrics_path = MODEL_PATH.with_name("metrics.json")
        if metrics_path.exists():
            raw = json.loads(metrics_path.read_text(encoding="utf-8"))
            model_meta = {
                "trained_on": raw.get("trained_on"),
                "roc_auc": raw.get("roc_auc"),
                "rows": raw.get("rows"),
            }
    except Exception:
        model_meta = {}

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "matched_indicators": [m["pattern"] for m in matches[:12]],
        "flags": flags,
        "metadata": {
            "detected_role": role,
            "ml_probability": ml_prob if ml_available else None,
            "ml_available": ml_available,
            "model": model_meta,
            "indicator_hits": matches[:12],
            "recommend": risk_score >= 0.45,
            **(extra_metadata or {}),
        },
    }
