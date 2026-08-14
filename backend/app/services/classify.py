from __future__ import annotations

from typing import Any

from app.models import OpportunityCategory, OpportunityMode, OpportunityType


def classify_opportunity(
    *,
    title: str,
    description: str,
    organization: str = "",
) -> dict[str, Any]:
    """
    Lightweight keyword classification for opportunity ingest.
    """
    from app.services.role_extractor import extract_role

    blob = f"{title} {description} {organization}".lower()
    role = extract_role(blob)

    category = None
    mode = None
    pricing = None
    labels: list[str] = []

    if any(k in blob for k in ("course", "certificate", "دورة", "شهادة", "تدريب")):
        category = OpportunityCategory.course.value
        labels.append("course")
        pricing = (
            OpportunityType.free.value
            if any(k in blob for k in ("free", "مجاني", "مجانا"))
            else OpportunityType.paid.value
        )
    elif any(k in blob for k in ("volunteer", "تطوع", "متطوع")):
        category = OpportunityCategory.volunteer.value
        labels.append("volunteer")
        pricing = OpportunityType.volunteer.value
    elif role or any(k in blob for k in ("job", "hiring", "وظيفة", "مطلوب")):
        category = OpportunityCategory.job.value
        labels.append("job")
        mode = (
            OpportunityMode.online.value
            if any(k in blob for k in ("remote", "online", "عن بعد", "أونلاين"))
            else OpportunityMode.offline.value
        )

    if role:
        labels.append(role)

    return {
        "category": category,
        "mode": mode,
        "pricing": pricing,
        "confidence": 0.7 if category else None,
        "labels": labels,
        "role": role,
    }


def apply_classification(record: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    category = result.get("category")
    mode = result.get("mode")
    pricing = result.get("pricing")

    if category == OpportunityCategory.job.value:
        record["category"] = OpportunityCategory.job.value
        if mode in (OpportunityMode.online.value, OpportunityMode.offline.value):
            record["mode"] = mode
    elif category == OpportunityCategory.course.value:
        record["category"] = OpportunityCategory.course.value
        if pricing == OpportunityType.free.value:
            record["opportunity_type"] = OpportunityType.free.value
            record["is_free"] = True
        elif pricing == OpportunityType.paid.value:
            record["opportunity_type"] = OpportunityType.paid.value
            record["is_free"] = False
    elif category == OpportunityCategory.volunteer.value:
        record["category"] = OpportunityCategory.volunteer.value
        record["is_volunteer"] = True
        record["opportunity_type"] = OpportunityType.volunteer.value

    record["ai_classified"] = category is not None
    record.setdefault("metadata_json", {})
    record["metadata_json"]["ai"] = {
        "confidence": result.get("confidence"),
        "labels": result.get("labels") or [],
    }
    return record
