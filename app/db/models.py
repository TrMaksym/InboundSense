from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Index


from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum as SQLEnum, Float, ForeignKey, String, Text, func, Integer, Boolean
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
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        default=None
    )
    source: Mapped[Source] = relationship("Source", back_populates="events")


class Chunk(Base):
    __tablename__ = "chunks"

    _table_args__ = (
        Index(
            "idx_chunks_event_id_chunk_index",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": "16", "ef_construction": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"}
        )
    )
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
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


class SourceType(str, Enum):
    WEBHOOK = "webhook"
    API = "api"
    SCRAPER = "scraper"



class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), doc="The name of the source")
    source_type: Mapped[SourceType] = mapped_column(
        SQLEnum(SourceType),
        nullable=False,
        default=SourceType.WEBHOOK,
    )
    target_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        doc="The target URL of the source",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fetch_interval_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=60)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_polled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    events: Mapped[list[Event]] = relationship("Event", back_populates="source")