from uuid import UUID
from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Source
from app.db.session import get_db
from app.schemas.source import SourceCreate, SourceResponse

router = APIRouter(prefix="/sources", tags=["source"])

@router.post("/", status_code=201, response_model=SourceResponse)
async def create_source(
    source_in: SourceCreate,
    db: AsyncSession = Depends(get_db),
) -> Source:
    source = Source(**source_in.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source

@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(source_id: UUID, db: AsyncSession = Depends(get_db)) -> Source:
        query = select(Source).where(Source.id == source_id)
        result = await db.execute(query)
        source = result.scalar_one_or_none()
        if source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
        return source
