import logging
import secrets

from redis import asyncio as asyncredis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import Url


def generate_secret_key():
    return secrets.token_urlsafe(8)


async def increment_clicks_worker(secret_key: str, db: AsyncSession):
    try:
        await db.execute(
            update(Url)
            .where(Url.secret_key == secret_key)
            .values(clicks=Url.clicks + 1)
        )
        await db.commit()
    except Exception as e:
        logging.error(f"Failed to increment clicks for {secret_key}: {e}")


async def save_url_worker(
    secret_key: str, target_url: str, redis_client, db: AsyncSession
):
    try:
        new_url = Url(secret_key=secret_key, target_url=target_url)
        db.add(new_url)
        await db.commit()
        cache_key = f"url_{secret_key}"
        await redis_client.set(cache_key, target_url, ex=86400)

    except Exception as e:
        logging.error(f"Ошибка при сохранении {secret_key}: {e}")


async def get_original_url(
    redis_client: asyncredis.Redis, db: AsyncSession, secret_key: str
) -> str:
    url_from_cache = await redis_client.get(f"url_{secret_key}")
    if url_from_cache:
        return url_from_cache

    result = await db.execute(select(Url).where(Url.secret_key == secret_key))
    url_object = result.scalars().first()

    if not url_object:
        return ""

    final_url = str(url_object.target_url)
    await redis_client.set(f"url_{secret_key}", final_url, ex=86400)

    return final_url


async def get_short_url_stats(db: AsyncSession, secret_key: str):
    result = await db.execute(select(Url).where(Url.secret_key == secret_key))

    return result.scalars().first()
