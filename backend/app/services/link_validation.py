from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException, status

from app.config import get_settings


async def validate_link_upstream(url: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.link_validation_api_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LINK_VALIDATION_API_URL is not configured",
        )

    headers: dict[str, str] = {"Accept": "application/json"}
    if settings.link_validation_api_key:
        headers["Authorization"] = f"Bearer {settings.link_validation_api_key}"

    endpoint = settings.link_validation_api_url.rstrip("/") + "/validate"

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
            upstream = await client.post(endpoint, json={"url": url}, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="link validation upstream unavailable",
        ) from exc

    if upstream.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="link validation upstream rejected request",
        )

    try:
        data = upstream.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="invalid upstream response",
        ) from exc

    if not isinstance(data, dict):
        return {"upstream": data}
    return data
