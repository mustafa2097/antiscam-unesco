from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.governorates import GOVERNORATE_SLUGS, IRAQI_GOVERNORATES
from app.database import get_db
from app.models import Opportunity, OpportunityMode, OpportunityType
from app.rate_limit import limiter
from app.schemas import OpportunityCategoryQuery, OpportunityPublic, OpportunitySubFilter
from app.security import CONTROL_CHARS
from app.services.role_extractor import ROLE_KEYWORDS

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


def _clean_role(value: str | None) -> str:
    if not value:
        return ""
    cleaned = CONTROL_CHARS.sub("", value.strip()).lower()
    if len(cleaned) > 64:
        cleaned = cleaned[:64]
    return cleaned


def _clean_governorate(value: str | None) -> str:
    if not value or value.lower() == "all":
        return "all"
    slug = value.strip().lower()
    if slug not in GOVERNORATE_SLUGS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid governorate")
    return slug


def _apply_category_filters(
    clauses: list,
    category: OpportunityCategoryQuery | None,
    sub: OpportunitySubFilter | None,
) -> None:
    if category is None:
        return

    clauses.append(Opportunity.category == category.value)

    if category is OpportunityCategoryQuery.volunteer:
        clauses.append(Opportunity.is_volunteer.is_(True))
        return

    if category in (
        OpportunityCategoryQuery.job,
        OpportunityCategoryQuery.internship,
    ):
        if sub is OpportunitySubFilter.online:
            clauses.append(Opportunity.mode == OpportunityMode.online)
        elif sub is OpportunitySubFilter.onsite:
            clauses.append(Opportunity.mode == OpportunityMode.offline)
        return

    if category in (
        OpportunityCategoryQuery.course,
        OpportunityCategoryQuery.scholarship,
    ):
        if sub is OpportunitySubFilter.paid:
            clauses.extend(
                [
                    Opportunity.opportunity_type == OpportunityType.paid,
                    Opportunity.is_free.is_(False),
                ]
            )
        elif sub is OpportunitySubFilter.free:
            clauses.append(
                or_(
                    Opportunity.opportunity_type == OpportunityType.free,
                    Opportunity.is_free.is_(True),
                )
            )


@router.get("/governorates")
@limiter.limit("60/minute")
async def list_governorates(request: Request) -> list[dict[str, str]]:
    return [{"slug": slug, "name_en": en, "name_ar": ar} for slug, en, ar in IRAQI_GOVERNORATES]


@router.get("", response_model=list[OpportunityPublic])
@limiter.limit("60/minute")
async def list_opportunities(
    request: Request,
    role: str | None = Query(default=None, max_length=64),
    governorate: str | None = Query(default="all", max_length=64),
    category: OpportunityCategoryQuery | None = Query(default=None),
    sub: OpportunitySubFilter | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[OpportunityPublic]:
    gov = _clean_governorate(governorate)
    role_slug = _clean_role(role)

    if sub and category is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sub filter requires category",
        )
    if sub and category is OpportunityCategoryQuery.volunteer:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="volunteer has no sub filters",
        )
    if category in (
        OpportunityCategoryQuery.job,
        OpportunityCategoryQuery.internship,
    ) and sub not in (
        None,
        OpportunitySubFilter.online,
        OpportunitySubFilter.onsite,
    ):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid job sub")
    if category in (
        OpportunityCategoryQuery.course,
        OpportunityCategoryQuery.scholarship,
    ) and sub not in (
        None,
        OpportunitySubFilter.paid,
        OpportunitySubFilter.free,
    ):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid course sub")

    clauses = [
        Opportunity.verified.is_(True),
        Opportunity.min_age >= 18,
    ]

    if gov != "all":
        clauses.append(Opportunity.governorate == gov)

    if role_slug:
        keywords = ROLE_KEYWORDS.get(role_slug, (role_slug,))
        role_clauses = []
        for kw in keywords:
            pattern = f"%{kw}%"
            role_clauses.extend(
                [
                    Opportunity.position.ilike(pattern),
                    Opportunity.title_en.ilike(pattern),
                    Opportunity.title_ar.ilike(pattern),
                ]
            )
        clauses.append(or_(*role_clauses))

    _apply_category_filters(clauses, category, sub)

    stmt = (
        select(Opportunity)
        .where(and_(*clauses))
        .order_by(Opportunity.created_at.desc())
        .limit(150)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [OpportunityPublic.model_validate(row) for row in rows]
