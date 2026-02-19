from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.url import UrlCreate, UrlInfo
from app.services.url_service import (
    create_short_url,
    get_original_url,
    get_short_url_stats,
)

router = APIRouter()


@router.post("/shorten", response_model=UrlInfo)
async def shorten(scheme: UrlCreate, db: AsyncSession = Depends(get_db)):
    created_url = await create_short_url(db, str(scheme.target_url))
    return created_url


@router.get("/{secret_key}")
async def redirect(secret_key: str, db: AsyncSession = Depends(get_db)):
    original_url = await get_original_url(db, secret_key)
    if not original_url:
        raise HTTPException(status_code=404)
    return RedirectResponse(original_url.target_url)


@router.get("/stats/{secret_key}")
async def short_url_stats(secret_key: str, db: AsyncSession = Depends(get_db)):
    requested_url = await get_short_url_stats(db, secret_key)
    if not requested_url:
        raise HTTPException(status_code=404)

    return {"target_url": requested_url.target_url, "clicks": requested_url.clicks}
