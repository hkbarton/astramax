from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    id: str | None = None
    payload: str | None = None
    created_at: datetime | None = None
    processed_by: str | None = None

    class Config:
        orm_mode = True
