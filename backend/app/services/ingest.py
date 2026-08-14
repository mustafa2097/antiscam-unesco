from __future__ import annotations

import csv
import hashlib
import io
import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import ScamIndicator
from app.schemas import IndicatorRow, IngestFormat
from app.security import CONTROL_CHARS


async def ingest_scam_dataset(
    *,
    db: AsyncSession,
    raw: bytes,
    fmt: IngestFormat,
    source_name: str,
) -> dict[str, Any]:
    settings = get_settings()
    if not raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty file")
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="file too large",
        )

    digest = hashlib.sha256(raw).hexdigest()
    accepted_rows: list[dict[str, Any]] = []
    rejected = 0

    try:
        if fmt is IngestFormat.json:
            payload = json.loads(raw.decode("utf-8"))
            if isinstance(payload, dict):
                rows = payload.get("indicators", [])
            elif isinstance(payload, list):
                rows = payload
            else:
                raise ValueError("unsupported json root")
            if not isinstance(rows, list):
                raise ValueError("indicators must be a list")
        else:
            text = raw.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
    except (UnicodeDecodeError, json.JSONDecodeError, csv.Error, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"invalid dataset: {exc}",
        ) from exc

    safe_source = CONTROL_CHARS.sub("", source_name)[:255]

    for row in rows:
        if not isinstance(row, dict):
            rejected += 1
            continue
        try:
            normalized = {
                "pattern": row.get("pattern", ""),
                "category": row.get("category", ""),
                "severity": float(row["severity"]) if row.get("severity") not in (None, "") else None,
                "language": row.get("language", "") or "",
                "metadata": row.get("metadata") if isinstance(row.get("metadata"), dict) else {},
            }
            if normalized["severity"] is None:
                raise ValueError("severity required")
            indicator = IndicatorRow(**normalized)
            accepted_rows.append(
                {
                    "pattern": indicator.pattern,
                    "category": indicator.category,
                    "severity": indicator.severity,
                    "language": indicator.language,
                    "source": safe_source,
                    "content_sha256": digest,
                    "metadata_json": indicator.metadata,
                }
            )
        except (TypeError, ValueError):
            rejected += 1

    if accepted_rows:
        insert_stmt = insert(ScamIndicator).values(accepted_rows)
        upsert_stmt = insert_stmt.on_conflict_do_update(
            constraint="uq_indicator_pattern_cat_src",
            set_={
                "severity": insert_stmt.excluded.severity,
                "language": insert_stmt.excluded.language,
                "content_sha256": insert_stmt.excluded.content_sha256,
                "metadata_json": insert_stmt.excluded.metadata_json,
            },
        )
        await db.execute(upsert_stmt)
        await db.commit()

    return {
        "source": safe_source,
        "content_sha256": digest,
        "accepted": len(accepted_rows),
        "rejected": rejected,
        "indicators": [],
    }
