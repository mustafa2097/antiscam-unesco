from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.rate_limit import limiter
from app.services.recommend import recommend_for_role

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


@router.get("")
@limiter.limit("60/minute")
async def get_recommendations(
    request: Request,
    role: str | None = Query(default=None, max_length=64),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return await recommend_for_role(db, role)
