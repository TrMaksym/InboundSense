from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class ChunkCreate(BaseModel):
    event_id: UUID
    content: str = Field(
        ...,
        min_length=1,
        description="The content of the chunk"
    )
    embedding: list[float] = Field(
        ...,
        min_length=384,
        max_length=384,
        description="The embedding of the chunk"
    )


class ChunkBase(BaseModel):
    id: UUID
    event_id: UUID
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChunkSearchResult(ChunkBase):
    similarity: float = Field(
        ...,
        description="The similarity of the chunk to the query"
    )