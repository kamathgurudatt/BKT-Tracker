from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()
try:
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True) if settings.redis_url else None
except Exception:
    redis_client = None
