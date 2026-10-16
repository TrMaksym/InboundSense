from enum import Enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.db.models import EventStatus

class EventCreate(BaseModel):
    text: str = Field(
        ...,
        min_length=5,
        max_length=5000,
        description="The text of the event"
    )
    source_id: UUID | None = None


class EventBase(BaseModel):
    text: str
    status: EventStatus
    category: str | None = None
    confidence: float | None = None


class EventResponse(EventBase):
    id: UUID
    created_at: datetime
    processed_at: datetime | None = None
    source_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)
