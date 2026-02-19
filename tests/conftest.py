import sys
import os
import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from dotenv import load_dotenv
from app.main import app
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.database import Base, get_db

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

@pytest_asyncio.fixture(scope="function")
async def client():
    app.dependency_overrides[get_db] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()
