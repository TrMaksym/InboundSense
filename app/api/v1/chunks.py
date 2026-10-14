from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk
from app.db.session import get_db
from app.schemas.chunk import ChunkBase

router = APIRouter(prefix="/chunks", tags=["chunks"])


@router.get("/{chunk_id}", response_model=ChunkBase, status_code=status.HTTP_200_OK)
async def get_chunk(
    chunk_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Chunk:
    query = select(Chunk).where(Chunk.id == chunk_id)
    result = await db.execute(query)
    chunk = result.scalar_one_or_none()
    if chunk is None:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk


@router.get(
    "/by-event/{event_id}",
    response_model=list[ChunkBase],
    status_code=status.HTTP_200_OK,
)
async def get_chunks_by_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Sequence[Chunk]:
    query = select(Chunk).where(Chunk.event_id == event_id)
    chunks = (await db.execute(query)).scalars().all()
    return chunks