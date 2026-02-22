from contextlib import asynccontextmanager

import redis.asyncio as asyncredis
import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.endpoints import limiter, router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    r_client = asyncredis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = r_client

    yield

    await app.state.redis.aclose()


app = FastAPI(lifespan=lifespan)

Instrumentator().instrument(app).expose(app, include_redis=False)

app.include_router(router)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
