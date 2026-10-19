from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.chunks import router as chunks_router
from app.api.v1.events import router as events_router
from app.api.v1.source import router as source_router
from app.api.v1.search import router as search_router
from app.api.v1.stream import router as stream_router
from app.api.v1.analytics import router as analytics_router
from app.db.base import Base
from app.db.session import engine




@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="InboundSense",
    version="0.1.0",
    description="Async NLP processing pipeline for inbound communications",
    lifespan=lifespan,
)

app.include_router(events_router, prefix="/api/v1")
app.include_router(chunks_router, prefix="/api/v1")
app.include_router(source_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(stream_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}