import asyncio
import uuid

from sqlalchemy import func, select

from app.core.celery_app import celery_app
from app.db.models import Event, Source, SourceType
from app.db.session import SessionLocal
from app.services.ml_engine import ml_engine
from app.services.nlp import process_event
from app.services.scraper import fetch_and_extract_text


@celery_app.task(name="process_event_task")
def process_event_task(event_id_str: str, payload_text: str):
    event_id = uuid.UUID(event_id_str)

    category, confidence = ml_engine.classify(payload_text)

    async def _run():
        async with SessionLocal() as session:
            event_stmt = select(Event).where(Event.id == event_id)
            res = await session.execute(event_stmt)
            event = res.scalar_one_or_none()

            if event and hasattr(event, "category"):
                event.category = category
                await session.commit()

            await process_event(
                event_id=event_id,
                payload_text=payload_text,
                db=session,
            )

    asyncio.run(_run())

    return {
        "status": "success",
        "event_id": event_id_str,
        "category": category,
        "confidence": confidence,
    }


async def _pol_scraper_sources() -> None:
    async with SessionLocal() as session:
        query = select(Source).where(
            Source.source_type == SourceType.SCRAPER,
            Source.is_active.is_(True),
            Source.target_url.is_not(None),
        )

        result = await session.execute(query)
        sources = result.scalars().all()

        for source in sources:
            text = await fetch_and_extract_text(source.target_url)
            if text:
                event = Event(text=text, source_id=source.id)
                session.add(event)
                source.last_polled_at = func.now()
                await session.commit()
                await session.refresh(event)

                process_event_task.delay(str(event.id), text)


@celery_app.task(name="poll_scraper_sources_task")
def poll_scraper_sources_task() -> None:
    asyncio.run(_pol_scraper_sources())