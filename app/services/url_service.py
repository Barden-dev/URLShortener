import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import Url


async def create_short_url(db: AsyncSession, target_url: str) -> Url:
    secret = secrets.token_urlsafe(8)
    url = Url(secret_key=secret, target_url=target_url)
    db.add(url)
    await db.commit()
    await db.refresh(url)

    return url


async def get_original_url(db: AsyncSession, secret_key: str):
    result = await db.execute(select(Url).where(Url.secret_key == secret_key))
    url_object = result.scalars().first()
    if url_object:
        url_object.clicks = Url.clicks + 1
        await db.commit()
        await db.refresh(url_object)

    return url_object


async def get_short_url_stats(db: AsyncSession, secret_key: str):
    result = await db.execute(select(Url).where(Url.secret_key == secret_key))

    return result.scalars().first()
