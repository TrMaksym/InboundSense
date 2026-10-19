from fastapi import APIRouter, Query
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.db.session import SessionLocal
from app.services.rag_service import stream_rag_response

router = APIRouter(prefix="/stream", tags=["stream"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/search")
async def stream_search(
        q: str = Query(..., description="Search query"),
        limit: int = Query(3, ge=1, le=10),
        db: AsyncSession = Depends(get_db),
    ) -> StreamingResponse:
    return StreamingResponse(
        stream_rag_response(query_text=q, db=db, limit=limit),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }

    )
