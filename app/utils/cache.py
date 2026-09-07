"""Redis cache helpers with an explicit no-cache fallback for demo mode."""
import json
from redis import Redis
from app.config import settings


def get_cache() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def get_json(key: str) -> dict | None:
    try:
        value = get_cache().get(key)
        return json.loads(value) if value else None
    except Exception:
        return None


def set_json(key: str, value: dict, ttl_seconds: int = 300) -> bool:
    try:
        get_cache().setex(key, ttl_seconds, json.dumps(value, default=str))
        return True
    except Exception:
        return False
