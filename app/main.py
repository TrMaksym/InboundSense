from fastapi import FastAPI
from app.api.v1.events import router as events_router
from app.api.v1.chunks import router as chunks_router

app = FastAPI(
    title="InboundSense",
    version="0.1.0",
    description="Async NLP processing pipeline for inbound communications",
)

app.include_router(events_router, prefix="/api/v1")
app.include_router(chunks_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}