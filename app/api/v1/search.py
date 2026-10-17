import asyncio

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk
from app.db.session import get_db
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.nlp import generate_embedding

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
async def search(
        request: SearchRequest,
        db: AsyncSession = Depends(get_db),
):
    embeddings = await asyncio.to_thread(generate_embedding, [request.query])
    raw_vector = list(embeddings)[0]

    if hasattr(raw_vector, "tolist"):
        query_vector = raw_vector.tolist()
    else:
        query_vector = [float(x) for x in raw_vector]

    distance = Chunk.embedding.cosine_distance(query_vector)

    stmt = (
        select(Chunk, distance.label("distance"))
        .order_by(distance.asc())
        .limit(request.limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    results = []
    for item, dist in rows:
        similarity = float(1.0 - dist)

        if request.similarity_threshold is not None and similarity < request.similarity_threshold:
            continue

        results.append(
            SearchResultItem(
                chunk_id=item.id,
                event_id=item.event_id,
                chunk_index=item.chunk_index,
                content=item.content,
                similarity=similarity,
            )
        )

    return SearchResponse(
        query=request.query,
        results=results,
    )