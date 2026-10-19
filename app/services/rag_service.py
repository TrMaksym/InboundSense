import asyncio
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk
from app.services.nlp import generate_embedding


async def stream_rag_response(query_text, db: AsyncSession, limit: int =3):
    payload = json.dumps({"type": "status", "message": "Searching..."})
    yield f"data: {payload}\n\n"
    query_vector = generate_embedding([query_text])[0]

    stmt = (
        select(
            Chunk.content,
            (1 - Chunk.embedding.cosine_distance(query_vector)).label("similarity"),
        )
        .order_by(Chunk.embedding.cosine_distance(query_vector))
        .limit(limit)
    )
    result = await db.execute(stmt)
    records = result.all()
    if not records:
        yield f"data: {json.dumps({'type': 'error', 'message': 'No results found'})}\n\n"
        return
    full_text = " ".join(r[0] for r in records)
    words = full_text.split()
    for word in words:
        payload = json.dumps({"type": "token", "token": word + " "})
        yield f"data: {payload}\n\n"
        await asyncio.sleep(0.04)
    done_payload = json.dumps({"type": "done"})
    yield f"data: {done_payload}\n\n"

