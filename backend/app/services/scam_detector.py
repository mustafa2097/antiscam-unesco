from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.predictor import explain_scam_features, predict_scam_probability
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

# Plain-language explanation of why each signal category raises scam risk.
CATEGORY_REASON = {
    "payment": {
        "en": "it asks you to pay money or fees up front — legitimate jobs never charge you to get hired",
        "ar": "يطلب منك دفع مال أو رسوم مقدماً، والوظيفة الحقيقية لا تطلب مالاً مقابل التوظيف",
    },
    "urgency": {
        "en": "it pressures you to act fast — a common trick to stop you from thinking or checking",
        "ar": "يضغط عليك للتصرف بسرعة، وهي حيلة شائعة لمنعك من التفكير أو التحقق",
    },
    "identity": {
        "en": "it asks for personal documents or ID too early, which can be used to steal your identity",
        "ar": "يطلب مستنداتك أو هويتك مبكراً جداً، وقد تُستخدم لسرقة هويتك",
    },
    "income": {
        "en": "it promises unrealistic income for little effort — a classic lure",
        "ar": "يعد بدخل غير واقعي مقابل مجهود بسيط، وهو طُعم كلاسيكي",
    },
    "contact": {
        "en": "it pushes contact through unofficial channels like personal messaging apps",
        "ar": "يدفعك للتواصل عبر قنوات غير رسمية مثل تطبيقات المراسلة الشخصية",
    },
    "general": {
        "en": "its wording matches other known scam patterns",
        "ar": "صياغته تطابق أنماط احتيال معروفة أخرى",
    },
}

LEVEL_STATEMENT = {
    "high": {
        "en": "This offer looks very likely to be a scam.",
        "ar": "هذا العرض يبدو محتالاً بدرجة كبيرة جداً.",
    },
    "medium": {
        "en": "This offer shows several scam warning signs — be careful.",
        "ar": "هذا العرض يحمل عدة علامات تحذير من الاحتيال، فكن حذراً.",
    },
    "low": {
        "en": "This offer shows a few mild warning signs.",
        "ar": "هذا العرض يحمل بعض العلامات التحذيرية الخفيفة.",
    },
    "safe": {
        "en": "This offer shows no clear scam signals, but always verify before sharing money or documents.",
        "ar": "هذا العرض لا يظهر إشارات احتيال واضحة، لكن تحقّق دائماً قبل دفع أي مال أو مشاركة مستندات.",
    },
}


# Short trait phrases used to describe, in plain words, what the model saw.
CATEGORY_TRAIT = {
    "payment": {"en": "a request to pay money up front", "ar": "طلب دفع مال مقدماً"},
    "urgency": {"en": "pressure to act quickly", "ar": "ضغطاً للتحرّك بسرعة"},
    "identity": {"en": "an early request for personal documents", "ar": "طلب مستندات شخصية مبكراً"},
    "income": {"en": "promises of unrealistic income", "ar": "وعوداً بدخل غير واقعي"},
    "contact": {"en": "a push toward unofficial contact channels", "ar": "توجيهاً لقنوات تواصل غير رسمية"},
    "general": {"en": "wording similar to known scam ads", "ar": "صياغة تشبه إعلانات النصب المعروفة"},
}


def _join_traits(traits: list[str], *, arabic: bool) -> str:
    if not traits:
        return ""
    if len(traits) == 1:
        return traits[0]
    sep = "، " if arabic else ", "
    last = " و" if arabic else ", and "
    return sep.join(traits[:-1]) + last + traits[-1]


def _evidence_sentence(
    content: str,
    matches: list[dict[str, Any]],
    *,
    ml_available: bool,
) -> str:
    """Return the sentence that most influenced the assessment."""
    sentences = [
        " ".join(part.split()).strip(" -•")
        for part in re.split(r"(?<=[.!?؟])\s+|\n+", content or "")
        if part.strip()
    ][:12]
    if not sentences:
        return ""

    def rule_weight(sentence: str) -> float:
        lowered = sentence.lower()
        return sum(
            float(hit.get("severity") or 0.0)
            for hit in matches
            if str(hit.get("pattern") or "").lower() in lowered
        )

    weighted = [(rule_weight(sentence), sentence) for sentence in sentences]
    best_rule_weight, best_rule_sentence = max(weighted, key=lambda item: item[0])
    if best_rule_weight > 0:
        return best_rule_sentence[:280]

    if ml_available:
        scored: list[tuple[float, str]] = []
        for sentence in sentences:
            if len(sentence) < 12:
                continue
            prediction = predict_scam_probability(sentence)
            if prediction["available"]:
                scored.append((float(prediction["probability"]), sentence))
        if scored:
            return max(scored, key=lambda item: item[0])[1][:280]

    return max(sentences, key=len)[:280]


def _build_narrative(
    *,
    risk_level: str,
    final_pct: float,
    ml_probability: float,
    ml_available: bool,
    signals: list[dict[str, Any]],
    model_meta: dict[str, Any],
    evidence_sentence: str = "",
    model_terms: list[str] | None = None,
) -> dict[str, str]:
    """Build a human-readable, number-free explanation of why the score was given."""
    reasons_en: list[str] = []
    reasons_ar: list[str] = []

    top_cats = [s["category"] for s in signals[:3]]
    traits_en = [CATEGORY_TRAIT.get(c, CATEGORY_TRAIT["general"])["en"] for c in top_cats]
    traits_ar = [CATEGORY_TRAIT.get(c, CATEGORY_TRAIT["general"])["ar"] for c in top_cats]
    quote_en = f'“{evidence_sentence}”' if evidence_sentence else "the offer"
    quote_ar = f"«{evidence_sentence}»" if evidence_sentence else "العرض"
    terms = [term for term in (model_terms or []) if term][:4]
    terms_en = ", ".join(f'“{term}”' for term in terms)
    terms_ar = "، ".join(f"«{term}»" for term in terms)

    # The wording changes within each risk band so a low score is not described
    # like a scam verdict. The explanation remains grounded in the strongest
    # sentence and any concrete warning categories that were actually matched.
    if risk_level == "high" and top_cats:
        joined_en = _join_traits(traits_en, arabic=False)
        joined_ar = _join_traits(traits_ar, arabic=True)
        reasons_en.append(
            f"The strongest sentence was {quote_en}. It combines {joined_en}; "
            "several strong warning signs appearing together is typical of scam ads."
        )
        reasons_ar.append(
            f"أكثر جملة أثّرت في التقييم هي {quote_ar}. جمعت هذه الجملة {joined_ar}؛ "
            "واجتماع عدة إشارات قوية بهذا الشكل شائع في إعلانات النصب."
        )
    elif risk_level == "high":
        feature_en = f" The strongest model cues were {terms_en}." if terms else ""
        feature_ar = f" أبرز العبارات التي دفعت المودل لهذا التقدير كانت {terms_ar}." if terms else ""
        reasons_en.append(
            f"The strongest sentence was {quote_en}. Its wording is highly similar to patterns "
            f"the model repeatedly sees in scam ads.{feature_en} "
            "The warning is therefore strong even without an exact phrase match."
        )
        reasons_ar.append(
            f"أكثر جملة أثّرت في التقييم هي {quote_ar}. صياغتها شديدة الشبه بأنماط يراها المودل "
            f"مراراً في إعلانات النصب.{feature_ar} لذلك التحذير قوي حتى دون تطابق عبارة حرفية."
        )
    elif risk_level == "medium" and top_cats:
        joined_en = _join_traits(traits_en, arabic=False)
        joined_ar = _join_traits(traits_ar, arabic=True)
        reasons_en.append(
            f"The sentence {quote_en} contains {joined_en}. These are meaningful warning signs, "
            "but the text does not contain enough strong evidence for a high-risk verdict."
        )
        reasons_ar.append(
            f"الجملة {quote_ar} تحتوي {joined_ar}. هذه إشارات تحذير واضحة، لكن النص لا يحتوي "
            "أدلة قوية كافية لاعتباره عالي الخطورة."
        )
    elif risk_level == "medium":
        feature_en = f" The main model cues were {terms_en}." if terms else ""
        feature_ar = f" أكثر العبارات تأثيراً في المودل كانت {terms_ar}." if terms else ""
        reasons_en.append(
            f"The sentence {quote_en} has a noticeable resemblance to scam-ad wording. "
            f"{feature_en} The similarity is worth caution, but it is not conclusive proof of fraud."
        )
        reasons_ar.append(
            f"في الجملة {quote_ar} لاحظ المودل تشابهاً ملحوظاً مع صياغة إعلانات النصب. "
            f"{feature_ar} هذا التشابه يستدعي الحذر، لكنه ليس دليلاً قاطعاً على الاحتيال."
        )
    elif risk_level == "low" and top_cats:
        joined_en = _join_traits(traits_en, arabic=False)
        joined_ar = _join_traits(traits_ar, arabic=True)
        reasons_en.append(
            f"The sentence {quote_en} contains {joined_en}, but the signal is limited and may have "
            "a legitimate explanation. The model therefore treats this as low risk, not as a scam verdict."
        )
        reasons_ar.append(
            f"في الجملة {quote_ar} لاحظ المودل {joined_ar}، لكن الإشارة محدودة وقد يكون لها "
            "تفسير طبيعي. لذلك اعتبر الخطر منخفضاً ولم يحكم بأن العرض نصب."
        )
    elif risk_level == "low":
        strength_en = "weak" if final_pct < 30 else "limited"
        strength_ar = "ضعيفاً" if final_pct < 30 else "محدوداً"
        feature_en = (
            f" The words or phrases that influenced it most were {terms_en}, "
            "but each can also appear in legitimate offers."
            if terms
            else ""
        )
        feature_ar = (
            f" أكثر الكلمات أو العبارات التي أثّرت في تقديره كانت {terms_ar}، "
            "لكنها قد تظهر أيضاً في عروض حقيقية."
            if terms
            else ""
        )
        reasons_en.append(
            f"In the sentence {quote_en}, the model noticed a {strength_en} and unclear pattern "
            f"that resembles some scam ads.{feature_en} The system did not match an explicit request "
            "for money, sensitive documents, or urgent action, so this is only a caution signal—not a scam verdict."
            " This is why the risk remains low."
        )
        reasons_ar.append(
            f"في الجملة {quote_ar} لاحظ المودل نمطاً {strength_ar} وغير واضح يشبه بعض إعلانات النصب."
            f"{feature_ar} لم يرصد النظام عبارة صريحة تطلب المال أو المستندات الحساسة أو الاستعجال، "
            "لذلك هذه إشارة للاحتياط فقط وليست حكماً بأن العرض نصب، ولهذا بقي مستوى الخطر منخفضاً."
        )
    elif top_cats:
        joined_en = _join_traits(traits_en, arabic=False)
        joined_ar = _join_traits(traits_ar, arabic=True)
        reasons_en.append(
            f"The sentence {quote_en} includes {joined_en}, but the signal is isolated and weak. "
            "Verify the source, but there is no clear basis to label the offer a scam."
        )
        reasons_ar.append(
            f"تتضمن الجملة {quote_ar} {joined_ar}، لكن الإشارة منفردة وضعيفة. "
            "تحقّق من المصدر، فلا يوجد أساس واضح لاعتبار العرض نصباً."
        )
    else:
        reasons_en.append(
            f"The model found no clear scam pattern in {quote_en}. The wording appears mostly normal; "
            "routine source verification is still recommended."
        )
        reasons_ar.append(
            f"لم يجد المودل نمط نصب واضحاً في {quote_ar}. الصياغة تبدو طبيعية في الغالب، "
            "ويُنصح فقط بالتحقق المعتاد من المصدر."
        )

    # Then explain, per detected category, why that trait is dangerous.
    for signal in signals[:4]:
        cat = signal["category"]
        reason = CATEGORY_REASON.get(cat, CATEGORY_REASON["general"])
        label_en = signal["label_en"]
        label_ar = signal["label_ar"]
        example = signal.get("reasons") or []
        example_en = f' (e.g. "{example[0]}")' if example else ""
        example_ar = f' (مثل: "{example[0]}")' if example else ""
        reasons_en.append(f"{label_en}: {reason['en']}{example_en}.")
        reasons_ar.append(f"{label_ar}: {reason['ar']}{example_ar}.")

    summary_en = " ".join(reasons_en)
    summary_ar = " ".join(reasons_ar)

    return {
        "summary_en": summary_en,
        "summary_ar": summary_ar,
        "reasons_en": reasons_en,
        "reasons_ar": reasons_ar,
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
    risk_level: str = "safe",
    model_meta: dict[str, Any] | None = None,
    content: str = "",
    model_terms: list[str] | None = None,
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

    signals = _category_signal_strength(matches)
    evidence = _evidence_sentence(content, matches, ml_available=ml_available)
    narrative = _build_narrative(
        risk_level=risk_level,
        final_pct=final_pct,
        ml_probability=ml_probability,
        ml_available=ml_available,
        signals=signals,
        model_meta=model_meta or {},
        evidence_sentence=evidence,
        model_terms=model_terms,
    )

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
        "signals": signals,
        "evidence_sentence": evidence,
        "model_terms": model_terms or [],
        "summary_en": narrative["summary_en"],
        "summary_ar": narrative["summary_ar"],
        "reasons_en": narrative["reasons_en"],
        "reasons_ar": narrative["reasons_ar"],
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
    model_terms = explain_scam_features(content) if ml_available else []

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

    breakdown = _build_breakdown(
        ml_probability=ml_prob,
        ml_available=ml_available,
        matches=matches,
        risk_score=risk_score,
        risk_level=risk_level,
        model_meta=model_meta,
        content=content,
        model_terms=model_terms,
    )

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
