from uuid import UUID
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Пошуковий запит")
    limit: int = Field(default=5, ge=1, le=50, description="Кількість результатів")


class SearchResultItem(BaseModel):
    chunk_id: UUID
    event_id: UUID
    chunk_index: int
    content: str
    similarity: float

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]