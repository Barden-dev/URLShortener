from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl
from redis import asyncio as asyncredis
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_db import get_redis
from app.schemas.url_scheme import UrlCreate, UrlInfo
from app.services.url_service import (
    generate_secret_key,
    get_original_url,
    get_short_url_stats,
    increment_clicks_worker,
    save_url_worker,
)

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)


@router.post("/shorten", response_model=UrlInfo)
@limiter.limit("10/minute")
async def shorten(
    request: Request,
    scheme: UrlCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis_client: asyncredis.Redis = Depends(get_redis),
):
    secret_key = generate_secret_key()

    background_tasks.add_task(
        save_url_worker,
        secret_key=secret_key,
        target_url=str(scheme.target_url),
        redis_client=redis_client,
        db=db,
    )

    return UrlInfo(
        target_url=HttpUrl(scheme.target_url),
        secret_key=secret_key,
        clicks=0,
        is_active=True,
    )


@router.get("/{secret_key}")
async def redirect(
    secret_key: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis_client: asyncredis.Redis = Depends(get_redis),
):
    original_url = await get_original_url(
        redis_client=redis_client, db=db, secret_key=secret_key
    )
    if not original_url:
        raise HTTPException(status_code=404)

    background_tasks.add_task(increment_clicks_worker, secret_key=secret_key, db=db)

    return RedirectResponse(original_url)


@router.get("/stats/{secret_key}")
async def short_url_stats(secret_key: str, db: AsyncSession = Depends(get_db)):
    requested_url = await get_short_url_stats(db, secret_key)
    if not requested_url:
        raise HTTPException(status_code=404)

    return {"target_url": requested_url.target_url, "clicks": requested_url.clicks}
