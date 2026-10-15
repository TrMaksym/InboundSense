import uuid
from typing import Sequence
from sqlalchemy import update
from curl_cffi import AsyncSession
from fastembed import TextEmbedding

from app.db.models import Chunk, Event, EventStatus

embedding_model = TextEmbedding(model_name="BAAI/bge-small-en")


def split_text_into_chunks(
        text: str,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
) -> list:
    cleaned_text = text.strip()
    if not cleaned_text:
        return []

    if len(cleaned_text) <= chunk_size:
        return [cleaned_text]

    chunks = []
    start = 0

    while start < len(cleaned_text):
        end = start + chunk_size

        if end >= len(cleaned_text):
            chunks.append(cleaned_text[start:]. strip())
            break

        window = cleaned_text[start:end]
        last_space = window.rfind(" ")

        if last_space != -1:
            end = start + last_space

        chunk = cleaned_text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        next_start = end - chunk_overlap
        start = next_start if next_start > start else end

    return chunks



def generate_embedding(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []

    embedding_generator = embedding_model.embed(texts)
    return list(embedding_generator)


async def process_event(event_id: uuid.UUID, payload_text: str, db: AsyncSession):
    chunks = split_text_into_chunks(payload_text)
    if not chunks:
        return []

    embeddings = generate_embedding(chunks)

    chunk_records = []
    for index, (text, vector) in enumerate(zip(chunks, embeddings)):
        chunk_record = Chunk(
            event_id=event_id,
            chunk_index=index,
            content=text,
            embedding=vector,
        )
        chunk_records.append(chunk_record)

    db.add_all(chunk_records)

    await db.execute(
        update(Event)
        .where(Event.id == event_id)
        .values(status=EventStatus.PROCESSED)
    )

    await db.commit()

    return chunk_records
