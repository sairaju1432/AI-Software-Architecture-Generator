import json
from typing import Any

import redis
from redis.exceptions import RedisError

from app.core.config import get_settings


class Cache:
    """Small Redis wrapper that degrades gracefully when Redis is unavailable."""

    def __init__(self):
        self.client = redis.from_url(get_settings().redis_url, decode_responses=True)

    def get_json(self, key: str) -> Any | None:
        try:
            value = self.client.get(key)
        except RedisError:
            return None
        return json.loads(value) if value else None

    def set_json(self, key: str, value: Any, ttl: int = 86_400) -> None:
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except RedisError:
            return None
