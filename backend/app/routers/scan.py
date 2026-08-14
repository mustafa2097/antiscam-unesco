import hashlib
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.rate_limit import limiter
from app.schemas import LinkScanRequest, TextScanRequest
from app.security import XSS_PATTERN, sanitize_text
from app.services.link_validation import validate_link_upstream
from app.services.recommend import recommend_for_role
from app.services.role_extractor import extract_role
from app.services.scam_detector import analyze_job_text

router = APIRouter(prefix="/api/scan", tags=["scan"])

ALLOWED_UPLOAD_MIME = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "application/pdf",
        "text/plain",
    }
)


async def _attach_recommendations(db: AsyncSession, result: dict[str, Any]) -> dict[str, Any]:
    meta = result.setdefault("metadata", {})
    if meta.get("recommend"):
        meta["recommendations"] = await recommend_for_role(db, meta.get("detected_role"))
    else:
        meta["recommendations"] = None
    return result


@router.post("/text")
@limiter.limit("20/minute")
async def scan_text(
    request: Request,
    body: TextScanRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await analyze_job_text(
        body.content,
        db=db,
        extra_metadata={"channel": "text", "length": len(body.content)},
    )
    return await _attach_recommendations(db, result)


@router.post("/image")
@limiter.limit("10/minute")
async def scan_image(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    settings = get_settings()
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_UPLOAD_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="unsupported media type",
        )

    try:
        filename = sanitize_text(file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid filename") from exc

    if XSS_PATTERN.search(filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid filename")

    raw = await file.read(settings.max_upload_bytes + 1)
    if len(raw) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty file")
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="file too large",
        )

    # Prefer readable text from .txt; otherwise fall back to filename keywords.
    ocr_text = ""
    if content_type == "text/plain":
        ocr_text = sanitize_text(raw.decode("utf-8", errors="ignore"))
    analysis_text = ocr_text or filename

    result = await analyze_job_text(
        analysis_text,
        db=db,
        extra_metadata={
            "channel": "image",
            "content_type": content_type,
            "size_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "ocr_text": ocr_text,
            "filename": filename,
        },
    )
    return await _attach_recommendations(db, result)


@router.post("/link")
@limiter.limit("15/minute")
async def scan_link(
    request: Request,
    body: LinkScanRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    upstream: dict[str, Any] | None = None
    settings = get_settings()
    if settings.link_validation_api_url:
        try:
            upstream = await validate_link_upstream(body.url)
        except HTTPException:
            upstream = {"status": "upstream_unavailable"}
    else:
        upstream = {"status": "skipped", "reason": "LINK_VALIDATION_API_URL not set"}

    # Analyze URL string + any upstream flags as text heuristics.
    blob = body.url
    if isinstance(upstream, dict):
        blob = f"{body.url} {upstream}"

    result = await analyze_job_text(
        blob,
        db=db,
        extra_metadata={"channel": "link", "url": body.url, "upstream": upstream},
    )
    # Role from URL alone is weak; keep extractor on URL if missing.
    if not result["metadata"].get("detected_role"):
        result["metadata"]["detected_role"] = extract_role(body.url)
    return await _attach_recommendations(db, result)
