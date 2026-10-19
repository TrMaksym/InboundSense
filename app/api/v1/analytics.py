from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event, Chunk
from app.db.session import get_db
from app.schemas.analytics import AnalyticsSchema

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/stats", response_model=AnalyticsSchema)
async def get_analytics(db: AsyncSession = Depends(get_db)):
    total_events = await db.scalar(select(func.count(Event.id))) or 0
    total_chunks = await db.scalar(select(func.count(Chunk.id))) or 0

    cat_result = await db.execute(
        select(Event.category, func.count(Event.id)).group_by(Event.category)
    )

    events_by_category = {
        cat or "unassigned": count for cat, count in cat_result.all()
    }

    status_result = await db.execute(
        select(Event.status, func.count(Event.id)).group_by(Event.status)
    )
    events_by_status = {
        status or "unknown": count for status, count in status_result.all()
    }

    return AnalyticsSchema(
        total_events=total_events,
        total_chunks=total_chunks,
        events_by_category=events_by_category,
        events_by_status=events_by_status
    )
