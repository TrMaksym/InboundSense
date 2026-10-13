from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum as SQLEnum, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class EventStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class Event(Base):
    __tablename__ = "events"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    status: Mapped[EventStatus] = mapped_column(
        SQLEnum(EventStatus),
        nullable=False,
        default=EventStatus.PENDING
    )
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    chunks: Mapped[list[Chunk]] = relationship(
        "Chunk",
        back_populates="event",
        cascade="all, delete-orphan",
    )


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id",ondelete="CASCADE"),
        index=True
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    embedding: Mapped[list[float]] = mapped_column(
        Vector(384),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    event: Mapped[Event] = relationship(
        "Event",
        back_populates="chunks",
    )