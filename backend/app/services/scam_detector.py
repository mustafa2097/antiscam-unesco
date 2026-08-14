from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.predictor import predict_scam_probability
from app.models import ScamIndicator
from app.services.role_extractor import extract_role
from app.services.scam_patterns import BUILTIN_INDICATORS

CATEGORY_LABELS = {
    "payment": {"en": "Payment / fees", "ar": "طلبات مالية / رسوم"},
    "urgency": {"en": "Urgency pressure", "ar": "ضغط الاستعجال"},
    "identity": {"en": "Identity / documents", "ar": "هوية / مستندات"},
    "income": {"en": "Unrealistic income", "ar": "دخل غير واقعي"},
    "contact": {"en": "Suspicious contact", "ar": "وسيلة تواصل مشبوهة"},
    "general": {"en": "Other warning signs", "ar": "علامات تحذير أخرى"},
}


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


def _rule_score(matches: list[dict[str, Any]]) -> float:
    if not matches:
        return 0.0
    severities = sorted((m["severity"] for m in matches), reverse=True)
    acc = 0.0
    for i, sev in enumerate(severities[:8]):
        acc += sev * (0.55**i)
    return min(acc, 1.0)


def _category_signal_strength(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-category signal strength (0–100), not independent probabilities."""
    totals: dict[str, float] = {}
    reasons: dict[str, list[str]] = {}
    for hit in matches:
        cat = hit["category"]
        totals[cat] = totals.get(cat, 0.0) + float(hit["severity"])
        reasons.setdefault(cat, [])
        if hit["pattern"] not in reasons[cat]:
            reasons[cat].append(hit["pattern"])

    if not totals:
        return []

    peak = max(totals.values()) or 1.0
    ordered = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return [
        {
            "category": cat,
            "label_en": CATEGORY_LABELS.get(cat, CATEGORY_LABELS["general"])["en"],
            "label_ar": CATEGORY_LABELS.get(cat, CATEGORY_LABELS["general"])["ar"],
            "strength_pct": round(min(totals[cat] / peak, 1.0) * 100),
            "reasons": reasons.get(cat, [])[:4],
        }
        for cat, _ in ordered
    ]


def _build_breakdown(
    *,
    ml_probability: float,
    ml_available: bool,
    matches: list[dict[str, Any]],
    risk_score: float,
) -> dict[str, Any]:
    rule_score = _rule_score(matches)
    ml_pct = round(ml_probability * 100, 1)
    rules_pct = round(rule_score * 100, 1)
    final_pct = round(risk_score * 100, 1)

    if ml_available:
        ml_weight = 0.55
        rules_weight = 0.45
        ml_contrib = round(ml_probability * ml_weight * 100, 1)
        rules_contrib = round(rule_score * rules_weight * 100, 1)
        formula_en = f"{final_pct}% = 55% × ML ({ml_pct}%) + 45% × rules ({rules_pct}%)"
        formula_ar = f"{final_pct}% = 55% × نموذج ML ({ml_pct}%) + 45% × القواعد ({rules_pct}%)"
        mode = "blended"
    else:
        ml_weight = 0.0
        rules_weight = 1.0
        ml_contrib = 0.0
        rules_contrib = round(rule_score * 100, 1)
        formula_en = f"{final_pct}% = rules only ({rules_pct}%) — ML model unavailable"
        formula_ar = f"{final_pct}% = قواعد فقط ({rules_pct}%) — نموذج ML غير متاح"
        mode = "rules_only"

    return {
        "mode": mode,
        "final_pct": final_pct,
        "ml_probability_pct": ml_pct if ml_available else None,
        "rule_score_pct": rules_pct,
        "ml_weight_pct": round(ml_weight * 100),
        "rules_weight_pct": round(rules_weight * 100),
        "ml_contribution_pct": ml_contrib,
        "rules_contribution_pct": rules_contrib,
        "formula_en": formula_en,
        "formula_ar": formula_ar,
        "signals": _category_signal_strength(matches),
        "disclaimer_en": (
            "Category bars show relative signal strength from matched warning patterns, "
            "not separate probabilities that add to 100%."
        ),
        "disclaimer_ar": (
            "أشرطة الفئات تعرض قوة الإشارة النسبية من الأنماط المطابقة، "
            "وليست احتمالات مستقلة تجمع إلى 100%."
        ),
    }


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
    rule_score = _rule_score(matches)
    if matches:
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

    breakdown = _build_breakdown(
        ml_probability=ml_prob,
        ml_available=ml_available,
        matches=matches,
        risk_score=risk_score,
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
            "breakdown": breakdown,
            "recommend": risk_score >= 0.45,
            **(extra_metadata or {}),
        },
    }
