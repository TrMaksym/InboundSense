from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.db.models import SourceType


class SourceBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=150, description="Name of the source")
    source_type: SourceType = Field(default=SourceType.WEBHOOK, description="Type of the source")
    target_url: str | None = Field(None,max_length=255, description="Target URL of the source")
    is_active: bool = Field(True, description="Status of the source")
    fetch_interval_minutes: int | None = Field(default=60, ge=1, description="Fetch interval in minutes")


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: UUID
    created_at: datetime
    last_polled_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)