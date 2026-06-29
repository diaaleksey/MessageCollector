import asyncpg
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def init(self):
        self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)

    async def get_messages(self, since: Optional[datetime] = None, limit: int = 100) -> List[Dict]:
        async with self.pool.acquire() as conn:
            if since:
                rows = await conn.fetch("""
                    SELECT id, tg_message_id, chat_id, chat_name, timestamp, text, media_paths
                    FROM messages
                    WHERE timestamp > $1
                    ORDER BY timestamp DESC
                    LIMIT $2
                """, since, limit)
            else:
                rows = await conn.fetch("""
                    SELECT id, tg_message_id, chat_id, chat_name, timestamp, text, media_paths
                    FROM messages
                    ORDER BY timestamp DESC
                    LIMIT $1
                """, limit)
            return [dict(row) for row in rows]

    async def get_message_count(self) -> int:
        async with self.pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM messages")
            return count

    async def get_collector_status(self) -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT is_connected, last_message_timestamp
                FROM collector_status
                WHERE id = 1
            """)
            if row:
                return {"is_connected": row["is_connected"], "last_message_timestamp": row["last_message_timestamp"]}
            else:
                return {"is_connected": False, "last_message_timestamp": None}

    async def delete_older_than(self, older_than_days: int) -> int:
        async with self.pool.acquire() as conn:
            cutoff = datetime.utcnow() - timedelta(days=older_than_days)
            result = await conn.execute("""
                DELETE FROM messages
                WHERE timestamp < $1
            """, cutoff)
            deleted = int(result.split()[1]) if result.startswith("DELETE") else 0
            return deleted

    async def close(self):
        if self.pool:
            await self.pool.close()