from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event
from app.db.session import get_db
from app.schemas.event import EventResponse, EventCreate

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    event_in: EventCreate,
    db: AsyncSession = Depends(get_db),
) -> Event:
    event = Event(text=event_in.text)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: UUID, db: AsyncSession = Depends(get_db)) -> Event:
    query = select(Event).where(Event.id == event_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
