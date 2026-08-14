from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Opportunity, OpportunityMode, OpportunityType, User
from app.security import hash_password
from app.services.seed_data import SEED_OPPORTUNITIES


async def ensure_seed_user(db: AsyncSession) -> None:
    settings = get_settings()
    email = (settings.seed_user_email or "").strip().lower()
    password = settings.seed_user_password or ""
    full_name = (settings.seed_user_full_name or "").strip()

    if not email or not password or not full_name:
        return

    existing = await db.execute(select(User).where(User.email == email))
    user = existing.scalar_one_or_none()
    if user:
        user.full_name = full_name
        user.password_hash = hash_password(password)
        user.is_active = True
        await db.commit()
        return

    db.add(
        User(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            locale="ar",
            is_active=True,
        )
    )
    await db.commit()


def _seed_fields(row: dict) -> dict:
    return {
        "title_en": row["title_en"],
        "title_ar": row["title_ar"],
        "description_en": row["description_en"],
        "description_ar": row["description_ar"],
        "organization": row["organization"],
        "position": row["position"],
        "governorate": row["governorate"],
        "city": row["city"],
        "category": row["category"],
        "mode": OpportunityMode(row["mode"]),
        "opportunity_type": OpportunityType(row["opportunity_type"]),
        "is_free": bool(row["is_free"]),
        "is_volunteer": bool(row["is_volunteer"]),
        "min_age": int(row.get("min_age", 18)),
        "verified": True,
        "ai_classified": False,
        "source_url": row["source_url"],
        "fallback_url": row.get("fallback_url", ""),
        "deadline": row.get("deadline", ""),
        "metadata_json": {
            "seed": True,
            "seed_id": row["seed_id"],
            "listing_status": row.get("listing_status", "open"),
        },
    }


async def ensure_seed_opportunities(db: AsyncSession) -> None:
    """Upsert catalog rows by stable seed_id; migrate legacy seed rows by title."""
    catalog_ids = {row["seed_id"] for row in SEED_OPPORTUNITIES}
    catalog_titles = {row["title_en"] for row in SEED_OPPORTUNITIES}
    title_to_row = {row["title_en"]: row for row in SEED_OPPORTUNITIES}

    result = await db.execute(select(Opportunity))
    existing_rows = list(result.scalars().all())

    by_seed_id: dict[str, Opportunity] = {}
    legacy_seed: list[Opportunity] = []
    for opp in existing_rows:
        meta = opp.metadata_json or {}
        if not meta.get("seed"):
            continue
        seed_id = meta.get("seed_id")
        if seed_id:
            by_seed_id[str(seed_id)] = opp
        else:
            legacy_seed.append(opp)

    changed = False
    for row in SEED_OPPORTUNITIES:
        seed_id = row["seed_id"]
        fields = _seed_fields(row)
        current = by_seed_id.get(seed_id)
        if current is None:
            for legacy in legacy_seed:
                if legacy.title_en == row["title_en"]:
                    current = legacy
                    legacy_seed.remove(legacy)
                    break
        if current is not None:
            for key, value in fields.items():
                setattr(current, key, value)
            by_seed_id[seed_id] = current
            changed = True
        else:
            db.add(Opportunity(**fields))
            changed = True

    for opp in existing_rows:
        meta = opp.metadata_json or {}
        if not meta.get("seed"):
            continue
        seed_id = meta.get("seed_id")
        if seed_id and str(seed_id) not in catalog_ids:
            await db.delete(opp)
            changed = True
        elif not seed_id and opp.title_en not in catalog_titles:
            await db.delete(opp)
            changed = True

    # One-time title refresh for legacy rows still in catalog under old titles.
    for legacy in legacy_seed:
        row = title_to_row.get(legacy.title_en)
        if not row:
            continue
        fields = _seed_fields(row)
        for key, value in fields.items():
            setattr(legacy, key, value)
        changed = True

    if changed:
        await db.commit()
