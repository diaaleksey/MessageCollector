from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MessageOut(BaseModel):
    id: int
    tg_message_id: int
    chat_id: str
    chat_name: str
    timestamp: datetime
    text: Optional[str]
    media_paths: Optional[List[str]]

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    telegram_connected: bool
    buffer_size: int
    last_message_timestamp: Optional[datetime]
    uptime_seconds: int