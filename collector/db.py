import asyncpg
import json
from datetime import datetime
from typing import List, Dict, Any

class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def init(self):
        self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)

    async def save_message(
        self,
        tg_msg_id: int,
        chat_id: str,
        chat_name: str,
        timestamp: datetime,
        text: str,
        media_paths: List[str],
        raw_json: Dict[str, Any]
    ):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (tg_message_id, chat_id, chat_name, timestamp, text, media_paths, raw_json)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (tg_message_id, chat_id) DO NOTHING
            """, tg_msg_id, chat_id, chat_name, timestamp, text, json.dumps(media_paths), json.dumps(raw_json, default=str))

    async def update_status(self, is_connected: bool, last_message_timestamp: datetime = None):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE collector_status
                SET is_connected = $1, last_message_timestamp = $2, updated_at = NOW()
                WHERE id = 1
            """, is_connected, last_message_timestamp)

    async def close(self):
        if self.pool:
            await self.pool.close()