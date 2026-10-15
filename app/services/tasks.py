import asyncio
import uuid

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.nlp import process_event


@celery_app.task(name="process_event_task")
def process_event_task(event_id_str: str, payload_text: str):
    event_id = uuid.UUID(event_id_str)
    async def _run():
        async with SessionLocal() as session:
            await process_event(event_id=event_id, payload_text=payload_text, db=session)

    asyncio.run(_run())

    return {"status": "success", "event_id": event_id_str}