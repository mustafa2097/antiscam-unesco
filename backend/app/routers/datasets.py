from typing import Any

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.rate_limit import limiter
from app.schemas import IngestFormat, UserPublic
from app.security import CONTROL_CHARS
from app.services.ingest import ingest_scam_dataset

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("/scam/ingest")
@limiter.limit("5/minute")
async def ingest_dataset_route(
    request: Request,
    file: UploadFile = File(...),
    fmt: IngestFormat = Form(IngestFormat.json),
    db: AsyncSession = Depends(get_db),
    _: UserPublic = Depends(get_current_user),
) -> dict[str, Any]:
    raw = await file.read()
    source_name = CONTROL_CHARS.sub("", file.filename or "dataset").strip() or "dataset"
    return await ingest_scam_dataset(db=db, raw=raw, fmt=fmt, source_name=source_name)
