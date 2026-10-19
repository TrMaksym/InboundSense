from pydantic import BaseModel


class AnalyticsSchema(BaseModel):
    total_events: int
    total_chunks: int
    events_by_category: dict[str, int]
    events_by_status: dict[str, int]