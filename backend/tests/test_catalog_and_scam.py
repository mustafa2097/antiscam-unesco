from __future__ import annotations

import pytest

from app.services.scam_detector import _build_breakdown, _combine_scores, _match_indicators
from app.services.scam_patterns import BUILTIN_INDICATORS
from app.services.seed_data import SEED_OPPORTUNITIES


def test_seed_catalog_has_direct_urls_and_ids():
    assert len(SEED_OPPORTUNITIES) >= 40
    seed_ids = [row["seed_id"] for row in SEED_OPPORTUNITIES]
    assert len(seed_ids) == len(set(seed_ids))
    for row in SEED_OPPORTUNITIES:
        assert row["source_url"].startswith("https://")
        assert "seed_id" in row


def test_job_rows_with_fallback_have_search_url():
    jobs = [row for row in SEED_OPPORTUNITIES if row["category"] == "job"]
    assert jobs
    for row in jobs:
        assert row.get("fallback_url", "").startswith("https://")


def test_scam_breakdown_blended_mode():
    text = "pay registration fee urgently via telegram guaranteed $5000 daily"
    matches = _match_indicators(text, BUILTIN_INDICATORS)
    risk_score, flags, level = _combine_scores(
        ml_probability=0.8,
        ml_available=True,
        matches=matches,
    )
    breakdown = _build_breakdown(
        ml_probability=0.8,
        ml_available=True,
        matches=matches,
        risk_score=risk_score,
        risk_level=level,
        model_meta={"rows": 17879},
    )
    assert breakdown["mode"] == "blended"
    assert breakdown["ml_weight_pct"] == 55
    assert breakdown["rules_weight_pct"] == 45
    assert breakdown["signals"]
    assert "55%" in breakdown["formula_en"]
    assert level in {"high", "medium", "low", "safe"}
    assert "ml_model" in flags
    assert breakdown["summary_en"] and breakdown["summary_ar"]
    assert breakdown["reasons_en"] and breakdown["reasons_ar"]
    assert any("AI noticed" in r for r in breakdown["reasons_en"])
    assert not any("trained on" in r for r in breakdown["reasons_en"])


def test_scam_breakdown_rules_only_mode():
    matches = _match_indicators("wire transfer fee", BUILTIN_INDICATORS)
    risk_score, _, _ = _combine_scores(
        ml_probability=0.0,
        ml_available=False,
        matches=matches,
    )
    breakdown = _build_breakdown(
        ml_probability=0.0,
        ml_available=False,
        matches=matches,
        risk_score=risk_score,
    )
    assert breakdown["mode"] == "rules_only"
    assert breakdown["ml_contribution_pct"] == 0.0
    assert "rules only" in breakdown["formula_en"].lower()
