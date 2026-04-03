from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.core.rate_limit import InMemoryRateLimitMiddleware
from backend.core.settings import settings
from backend.db.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="1.1.0", lifespan=lifespan)
app.include_router(router, prefix=settings.api_prefix)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(InMemoryRateLimitMiddleware, max_requests=settings.rate_limit_per_minute)
