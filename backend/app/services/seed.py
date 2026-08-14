from __future__ import annotations

from sqlalchemy import func, select
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


async def ensure_seed_opportunities(db: AsyncSession) -> None:
    count = await db.scalar(select(func.count()).select_from(Opportunity))
    if count and count > 0:
        return

    for row in SEED_OPPORTUNITIES:
        db.add(
            Opportunity(
                title_en=row["title_en"],
                title_ar=row["title_ar"],
                description_en=row["description_en"],
                description_ar=row["description_ar"],
                organization=row["organization"],
                position=row["position"],
                governorate=row["governorate"],
                city=row["city"],
                category=row["category"],
                mode=OpportunityMode(row["mode"]),
                opportunity_type=OpportunityType(row["opportunity_type"]),
                is_free=bool(row["is_free"]),
                is_volunteer=bool(row["is_volunteer"]),
                min_age=18,
                verified=True,
                ai_classified=False,
                source_url=row["source_url"],
                metadata_json={"seed": True},
            )
        )
    await db.commit()
