import asyncio
from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk
from app.db.session import get_db
from app.schemas.chunk import ChunkBase, ChunkSearchRequest, ChunkSearchResult
from app.services.nlp import generate_embedding

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

@router.post(
    "/search",
    response_model=list[ChunkSearchResult],
    status_code=status.HTTP_200_OK,
)
async def search_chunks(
    search_in: ChunkSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> list[ChunkSearchResult]:
    embeddings = await asyncio.to_thread(generate_embedding, [search_in.query])
    query_vector = embeddings[0]

    distance_expr = Chunk.embedding.cosine_distance(query_vector)
    similarity_expr = (1 - distance_expr).label("similarity")
    query = (
        select(Chunk, similarity_expr)
        .order_by(distance_expr)
        .limit(search_in.limit)
    )
    result = await db.execute(query)
    rows = result.all()

    search_results = [
        ChunkSearchResult(
            id=chunk.id,
            event_id=chunk.event_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            created_at=chunk.created_at,
            similarity=float(similarity_score),
        )
        for chunk, similarity_score in rows
    ]

    return search_results

