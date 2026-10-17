from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk
from app.db.session import get_db
from app.schemas import chunk
from app.schemas.search import SearchRequest, SearchResultItem, SearchResponse
from app.services.nlp import generate_embedding

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest,
                 db: AsyncSession = Depends(get_db)):
    query_vector = generate_embedding([request.query])[0]
    distance = Chunk.embedding.cosine_distance(query_vector)
    stmt = (
        select(Chunk, distance.label("distance"))
        .order_by(distance.asc())
        .limit(request.limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    results = [
        SearchResultItem(
            chunk_id=item.id,
            event_id=item.event_id,
            chunk_index=item.chunk_index,
            content=item.content,
            similarity=float(1.0 - distance),
        )
        for item, distance in rows
    ]

    return SearchResponse(
        query=request.query,
        results=results,
    )