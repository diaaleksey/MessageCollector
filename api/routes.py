from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Optional
from datetime import datetime
import time

from settings import API_KEY
from db import Database
from models import MessageOut, HealthResponse

router = APIRouter()

# --- Зависимости для получения данных из состояния приложения ---

async def get_db(request: Request) -> Database:
    """Возвращает экземпляр БД из состояния приложения."""
    return request.app.state.db

async def get_start_time(request: Request) -> int:
    """Возвращает время запуска приложения."""
    return request.app.state.start_time

# --- Аутентификация ---

async def verify_api_key(api_key: str = Query(..., alias="X-API-Key", header=True)):
    """Проверка API-ключа, переданного в заголовке."""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

# --- Эндпоинты ---

@router.get("/messages", response_model=list[MessageOut])
async def get_messages(
    since: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    authenticated: bool = Depends(verify_api_key),
    db: Database = Depends(get_db)
):
    """
    Получить сообщения.
    - `since` (опционально): timestamp в ISO-формате.
    - `limit` (по умолчанию 100): максимальное количество.
    """
    messages = await db.get_messages(since, limit)
    return messages

@router.get("/health", response_model=HealthResponse)
async def health(
    authenticated: bool = Depends(verify_api_key),
    db: Database = Depends(get_db),
    start_time: int = Depends(get_start_time)
):
    """Статус сервиса."""
    status_data = await db.get_collector_status()
    count = await db.get_message_count()
    uptime = int(time.time() - start_time)
    return HealthResponse(
        status="ok",
        telegram_connected=status_data["is_connected"],
        buffer_size=count,
        last_message_timestamp=status_data["last_message_timestamp"],
        uptime_seconds=uptime
    )

@router.delete("/messages/cleanup")
async def cleanup_messages(
    older_than_days: int = Query(7, ge=1),
    authenticated: bool = Depends(verify_api_key),
    db: Database = Depends(get_db)
):
    """
    Удалить сообщения старше указанного количества дней.
    Возвращает количество удалённых записей.
    """
    deleted = await db.delete_older_than(older_than_days)
    return {"deleted": deleted}