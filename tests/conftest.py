import asyncio
import os
import sys

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from fakeredis import FakeAsyncRedis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.core.redis_db import get_redis
from app.main import app

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


load_dotenv(".env.test")
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL is not set to .env.test")


engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
async_session = async_sessionmaker(engine)


@pytest_asyncio.fixture(autouse=True)
async def async_prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield


@pytest.fixture(scope="session")
def async_backend():
    return "asyncio"


async def override_db():
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture()
async def mock_redis():
    client = FakeAsyncRedis(decode_responses=True)
    yield client
    await client.flushall()


@pytest_asyncio.fixture(scope="function")
async def client(mock_redis):
    async def override_redis():
        yield mock_redis

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()
